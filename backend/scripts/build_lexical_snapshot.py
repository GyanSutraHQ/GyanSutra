"""Prepare optional Ramayana keyword records from local, source-matched data.

This never writes Firestore or calls a model. The output must be bundled with
the API deployment and configured with RAG_LEXICAL_SNAPSHOT.
"""

import argparse
import json
from pathlib import Path

from gyansutra.corpus import ramayana_records
from gyansutra.firestore import retrieved


def build(output):
    path = Path(output)
    if path.exists():
        raise FileExistsError(f"Snapshot already exists: {path}; choose a new output path.")
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("x") as stream:
        for doc_id, record, _ in ramayana_records():
            stream.write(
                json.dumps(
                    retrieved({"id": doc_id, **record}, 0),
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
                + "\n"
            )
            count += 1
    print(json.dumps({"records": count, "output": str(path), "bytes": path.stat().st_size}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True)
    build(parser.parse_args().output)
