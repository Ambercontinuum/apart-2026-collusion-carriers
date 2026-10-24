"""Record exact bytes with attributed contributor and independent recorder identity."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = ROOT / "notes" / "apart_2026" / "provenance"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--contributor", required=True)
    parser.add_argument("--recorder", default="codex")
    parser.add_argument("--attribution-basis", required=True)
    args = parser.parse_args()
    payload = args.source.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    STORE.mkdir(parents=True, exist_ok=True)
    artifact = STORE / digest
    if artifact.exists():
        if artifact.read_bytes() != payload:
            raise ValueError("existing artifact does not match its digest")
    else:
        with artifact.open("xb") as stream:
            stream.write(payload)
    record = {
        "schema": "apart.contribution.v1",
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "contributor_id": args.contributor,
        "recorder_id": args.recorder,
        "attribution_basis": args.attribution_basis,
        "source_name": args.source.name,
        "sha256": digest,
        "size_bytes": len(payload),
        "artifact": digest,
        "authentication": "attributed receipt; not a contributor signature",
    }
    # One receipt per file avoids concurrent writers sharing an append stream.
    import uuid
    receipt = STORE / (str(uuid.uuid4()) + ".json")
    with receipt.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(record, stream, indent=2)
        stream.write("\n")
    print(json.dumps(record))


if __name__ == "__main__":
    main()
