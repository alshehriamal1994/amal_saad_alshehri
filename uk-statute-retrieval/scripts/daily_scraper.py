#!/usr/bin/env python3
"""
daily_scraper.py

Optional maintenance script for fetching/updating external resources daily.
This is intentionally generic and uses only CLI args (no hard-coded paths).

Example:
  python scripts/daily_scraper.py --base_url "https://example.com/file.json" --out_dir data/daily --name statutes.json
"""

from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
from datetime import datetime, timezone
import urllib.request


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, out_path: Path, timeout: int = 60) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "uk-statute-retrieval/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    out_path.write_bytes(data)


def main() -> None:
    p = argparse.ArgumentParser(description="Optional daily fetch/update helper (no dataset bundled).")
    p.add_argument("--base_url", required=True, help="URL to download from (external resource).")
    p.add_argument("--out_dir", required=True, help="Directory to write outputs (e.g., data/daily).")
    p.add_argument("--name", default="download.bin", help="Output filename inside out_dir.")
    p.add_argument("--run_date", default=None, help="Override date stamp (YYYY-MM-DD). Default: today (UTC).")
    p.add_argument("--keep_dated_copy", action="store_true", help="Also save a dated copy under out_dir/archive/YYYY-MM-DD/.")
    p.add_argument("--timeout", type=int, default=60, help="Download timeout (seconds).")
    args = p.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.run_date:
        stamp = args.run_date
    else:
        stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    latest_path = out_dir / args.name
    download(args.base_url, latest_path, timeout=args.timeout)

    digest = sha256_file(latest_path)
    meta_path = out_dir / (args.name + ".sha256")
    meta_path.write_text(digest + "\n", encoding="utf-8")

    if args.keep_dated_copy:
        archive_dir = out_dir / "archive" / stamp
        archive_dir.mkdir(parents=True, exist_ok=True)
        archived = archive_dir / args.name
        archived.write_bytes(latest_path.read_bytes())
        (archive_dir / (args.name + ".sha256")).write_text(digest + "\n", encoding="utf-8")

    print(f"[OK] Downloaded: {args.base_url}")
    print(f"[OK] Saved:      {latest_path}")
    print(f"[OK] SHA256:     {digest}")


if __name__ == "__main__":
    main()
