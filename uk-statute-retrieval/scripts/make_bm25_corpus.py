import json
import argparse
from pathlib import Path
from tqdm import tqdm

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data_json",
        type=str,
        default="/home/amal/Desktop/Legal RAG content/Data.json",
        help="Path to Data.json corpus",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default="bm25_corpus_jsonl",
        help="Output directory for BM25 docs",
    )
    args = parser.parse_args()

    data_path = Path(args.data_json)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "docs.jsonl"

    print(f"Loading corpus from {data_path}")
    with data_path.open("r", encoding="utf-8") as f:
        corpus = json.load(f)
    print(f"Loaded {len(corpus)} chunks")

    with out_file.open("w", encoding="utf-8") as out_f:
        for item in tqdm(corpus, desc="Writing BM25 docs"):
            meta = item.get("metadata", {})
            chunk_id = meta.get("chunk_id")
            if chunk_id is None:
                # Fallback if field name differs
                chunk_id = meta.get("chunk_id", meta.get("doc_id"))

            text = item.get("content", "").strip()
            if not chunk_id or not text:
                continue

            doc = {
                "id": chunk_id,
                "contents": text,
            }
            out_f.write(json.dumps(doc) + "\n")

    print(f"Wrote BM25 docs to {out_file}")

if __name__ == "__main__":
    main()
