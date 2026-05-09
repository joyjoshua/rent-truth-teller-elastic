import json
import os
from pathlib import Path

from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

es = Elasticsearch(
    os.getenv("ES_URL"),
    api_key=os.getenv("ES_API_KEY"),
)

INDEX = "blr-rentals"
INPUT = ROOT / "data/processed/blr_rentals.jsonl"


def generate_actions():
    with INPUT.open("r", encoding="utf-8") as f:
        for line in f:
            doc = json.loads(line)
            yield {
                "_index": INDEX,
                "_id": doc["doc_id"],
                "_source": doc,
            }


def main() -> None:
    success, errors = bulk(es, generate_actions(), chunk_size=500)
    print(f"Indexed {success} documents. Errors: {len(errors)}")

    if errors:
        for e in errors[:5]:
            print(f"  {e}")

    es.indices.refresh(index=INDEX)
    count = es.count(index=INDEX)["count"]
    print(f"Total documents in {INDEX}: {count}")


if __name__ == "__main__":
    main()
