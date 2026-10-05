"""Fetch source-attributed commentary/translation data without using GenAI."""

import asyncio
import json
from collections import defaultdict

import httpx

from gyansutra.config import ROOT


async def enrich():
    async with httpx.AsyncClient(timeout=15) as client:

        async def fetch(name):
            response = await client.get(
                f"https://raw.githubusercontent.com/gita/gita/main/data/{name}.json"
            )
            response.raise_for_status()
            return response.json()

        verses, commentaries, translations = await asyncio.gather(
            *(fetch(n) for n in ("verse", "commentary", "translation"))
        )
    coordinates = {v["id"]: (v["chapter_number"], v["verse_number"]) for v in verses}
    explanations, additional = defaultdict(list), defaultdict(list)
    for rows, target, field, author, language in [
        (commentaries, explanations, "explanation", "Traditional Acharya", "sanskrit"),
        (translations, additional, "translation", "Scholar", "english"),
    ]:
        for row in rows:
            key = coordinates.get(row["verse_id"])
            if key and row.get("description", "").strip():
                target[key].append(
                    {
                        "author": row.get("authorName") or author,
                        "language": row.get("lang") or language,
                        field: row["description"].strip(),
                    }
                )
    path = ROOT / "data/gita.json"
    data = json.loads(path.read_text())
    for verse in data:
        key = (verse["chapter_number"], verse["verse_number"])
        verse.update(
            detailed_explanations=explanations[key], additional_translations=additional[key]
        )
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)
    print(f"Enriched {len(data)} verses with attributed source data.")


if __name__ == "__main__":
    asyncio.run(enrich())
