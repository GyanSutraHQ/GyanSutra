"""Bounded asynchronous proxy to the existing Python narration worker."""

import asyncio
import os
from collections import OrderedDict

import httpx

from .cache import ServiceError


class NarrationService:
    def __init__(self, http: httpx.AsyncClient):
        self.http = http
        self.cache = OrderedDict()
        self.cache_bytes = 0
        self.in_flight = 0

    async def audio(self, text, locale, style):
        url = os.getenv("NARRATION_SERVICE_URL")
        if not url:
            raise ServiceError("Natural narration is not configured.", "NARRATION_UNAVAILABLE")
        key = (url, text, locale, style)
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        if self.in_flight >= 2:
            raise ServiceError("Narrator is busy. Please try again.", "NARRATION_BUSY")
        self.in_flight += 1
        headers = (
            {"Authorization": "Bearer " + os.environ["NARRATION_SERVICE_TOKEN"]}
            if os.getenv("NARRATION_SERVICE_TOKEN")
            else {}
        )
        try:
            async with asyncio.timeout(85):
                async with self.http.stream(
                    "POST",
                    url.rstrip("/") + "/synthesize",
                    headers=headers,
                    json={"text": text.strip(), "locale": locale, "style": style},
                    timeout=85,
                ) as response:
                    if not response.is_success or "audio/wav" not in response.headers.get(
                        "content-type", ""
                    ):
                        raise ValueError("Invalid narration response")
                    chunks, size = [], 0
                    async for chunk in response.aiter_bytes():
                        size += len(chunk)
                        if size > 8 * 1024 * 1024:
                            raise ValueError("Audio too large")
                        chunks.append(chunk)
                    audio = b"".join(chunks)
            if len(audio) < 44 or audio[:4] != b"RIFF" or audio[8:12] != b"WAVE":
                raise ValueError("Invalid audio")
            self.cache_bytes -= len(self.cache.get(key, b""))
            self.cache[key] = audio
            self.cache_bytes += len(audio)
            while self.cache_bytes > 32 * 1024 * 1024:
                self.cache_bytes -= len(self.cache.popitem(last=False)[1])
            return audio
        except Exception as error:
            raise ServiceError(
                "Natural narration is temporarily unavailable.", "NARRATION_UNAVAILABLE"
            ) from error
        finally:
            self.in_flight -= 1
