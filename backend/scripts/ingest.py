"""Corpus ingestion with stable record IDs, provenance, and bounded write batches."""

import argparse
import asyncio

from google.cloud.firestore_v1.vector import Vector

from gyansutra.corpus import (  # Re-export the original preparation API.
    chunks,
    gita_records,
    ramayana_records,
    vishnu_records,
    word_meanings,
)
from gyansutra.embedding import LocalScriptureEmbeddings
from gyansutra.firestore import ScriptureStore
from gyansutra.text import POLICY

__all__ = ["chunks", "gita_records", "ramayana_records", "vishnu_records", "word_meanings"]


async def ingest(args):
    store, embeddings = ScriptureStore(), LocalScriptureEmbeddings()
    batch, count = [], 0
    try:
        if args.source == "gita" and not args.dry_run:
            await store.batch_write(
                "chapters",
                [
                    {"id": f"chapter_{v['number']}", "data": {**v, "sourceText": "Bhagavad Gita"}}
                    for v in POLICY["chapters"]
                ],
            )
        records = (
            gita_records()
            if args.source == "gita"
            else vishnu_records()
            if args.source == "vishnu"
            else ramayana_records(args.kanda)
        )
        for doc_id, record, text in records:
            vector = (
                None
                if args.skip_embed or not text
                else (await embeddings.aembed_documents([text]))[0]
            )
            record["embedding"] = Vector(vector) if vector else None
            batch.append({"id": doc_id, "data": record})
            count += 1
            if len(batch) >= 50:
                if not args.dry_run:
                    await store.batch_write("verses", batch)
                batch.clear()
        if batch and not args.dry_run:
            await store.batch_write("verses", batch)
        print(
            f"Prepared {count} records. "
            + ("Dry run; Firestore was not changed." if args.dry_run else "Ingestion completed.")
        )
    finally:
        await store.close()
        embeddings.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", choices=["gita", "vishnu", "ramayana"])
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-embed", action="store_true")
    parser.add_argument("--kanda", type=int, choices=range(1, 8))
    asyncio.run(ingest(parser.parse_args()))
