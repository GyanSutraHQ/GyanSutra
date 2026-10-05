"""ASGI security, CORS, body bounds and per-process request limits."""

import logging
import os
import time

from cachetools import TTLCache
from starlette.datastructures import Headers, MutableHeaders
from starlette.responses import JSONResponse, Response

from .config import integer

DEFAULT_ORIGINS = {
    "https://gyansutraapp.com",
    "https://www.gyansutraapp.com",
    "https://gyansutraapp.pages.dev",
    "https://santanu-sp.github.io",
    "https://localhost",
    "http://localhost:5173",
    "http://localhost:3001",
}
SECURITY = {
    "x-content-type-options": "nosniff",
    "x-frame-options": "SAMEORIGIN",
    "referrer-policy": "no-referrer",
    "strict-transport-security": "max-age=31536000; includeSubDomains",
    "cross-origin-opener-policy": "same-origin",
    "cross-origin-resource-policy": "same-origin",
    "x-dns-prefetch-control": "off",
    "x-download-options": "noopen",
    "x-permitted-cross-domain-policies": "none",
    "origin-agent-cluster": "?1",
    "content-security-policy": "default-src 'self';base-uri 'self';font-src 'self' https: data:;form-action 'self';frame-ancestors 'self';img-src 'self' data:;object-src 'none';script-src 'self';script-src-attr 'none';style-src 'self' https: 'unsafe-inline';upgrade-insecure-requests",
}


class ApiMiddleware:
    def __init__(self, app):
        self.app = app
        self.origins = DEFAULT_ORIGINS | {
            o.strip().rstrip("/")
            for o in (os.getenv("ALLOWED_ORIGINS") or os.getenv("CORS_ORIGIN", "")).split(",")
            if o.strip()
        }
        self.counts = TTLCache(10000, 900)
        self.ask_limit = integer("ASK_RATE_LIMIT_MAX", 20, 1, 200)
        self.proxy_hops = integer(
            "TRUST_PROXY_HOPS", 1 if os.getenv("NODE_ENV") == "production" else 0, 0, 10
        )

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        headers = Headers(scope=scope)
        origin = headers.get("origin")
        allowed = not origin or "*" in self.origins or origin.rstrip("/") in self.origins
        extra = {}
        response_started = False
        if origin and allowed:
            extra.update(
                {
                    "access-control-allow-origin": origin,
                    "access-control-allow-credentials": "true",
                    "vary": "Origin",
                }
            )

        async def secured(message):
            nonlocal response_started
            if message["type"] == "http.response.start":
                response_started = True
                output = MutableHeaders(scope=message)
                for key, value in {**SECURITY, **extra}.items():
                    output[key] = value
            await send(message)

        async def dispatch(input_receive):
            try:
                await self.app(scope, input_receive, secured)
            except Exception:
                if response_started:
                    raise
                logging.exception("API request failed")
                await JSONResponse({"error": "Internal server error."}, 500)(
                    scope, input_receive, secured
                )

        if not allowed:
            return await JSONResponse({"error": "Origin is not allowed by CORS."}, 403)(
                scope, receive, secured
            )
        if scope["method"] == "OPTIONS" and origin:
            extra.update(
                {
                    "access-control-allow-methods": "GET,POST",
                    "access-control-allow-headers": "Content-Type,Authorization",
                }
            )
            return await Response(status_code=204)(scope, receive, secured)
        # Express accepted trailing slashes; retain that route compatibility.
        path = scope["path"].rstrip("/") or "/"
        scope = {**scope, "path": path}
        if path == "/api" or path.startswith("/api/"):
            ip = scope.get("client", ("unknown", 0))[0]
            if self.proxy_hops and headers.get("x-forwarded-for"):
                chain = [v.strip() for v in headers["x-forwarded-for"].split(",")] + [ip]
                ip = chain[max(0, len(chain) - 1 - self.proxy_hops)]
            limits = [("general", 900, 200, "Too many requests, please try again later.")]
            if path == "/api/ask" or path.startswith("/api/ask/"):
                limits.append(
                    (
                        "ask",
                        900,
                        self.ask_limit,
                        "Too many questions - please wait a moment before asking again.",
                    )
                )
            if path == "/api/narration" or path.startswith("/api/narration/"):
                limits.append(("narration", 60, 60, "Too many requests, please try again later."))
            for bucket, window, maximum, message in limits:
                key = (bucket, ip)
                reset, count = self.counts.get(key, (time.monotonic() + window, 0))
                if reset <= time.monotonic():
                    reset, count = time.monotonic() + window, 0
                count += 1
                self.counts[key] = (reset, count)
                extra.update(
                    {
                        "ratelimit-limit": str(maximum),
                        "ratelimit-remaining": str(max(0, maximum - count)),
                        "ratelimit-reset": str(max(0, int(reset - time.monotonic()))),
                        "ratelimit-policy": f"{maximum};w={window}",
                    }
                )
                if count > maximum:
                    extra["retry-after"] = extra["ratelimit-reset"]
                    return await JSONResponse({"error": message}, 429)(scope, receive, secured)
        if scope["method"] in {"POST", "PUT", "PATCH"}:
            body = bytearray()
            while True:
                message = await receive()
                if message["type"] == "http.disconnect":
                    return
                body.extend(message.get("body", b""))
                if len(body) > 10240:
                    return await JSONResponse({"error": "request entity too large"}, 413)(
                        scope, receive, secured
                    )
                if not message.get("more_body"):
                    break
            delivered = False

            async def replay():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": bytes(body), "more_body": False}
                return await receive()

            return await dispatch(replay)
        return await dispatch(receive)
