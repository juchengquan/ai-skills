#!/usr/bin/env python3
"""
Search the LLM Wiki pages by keyword or topic.
At small scale, uses simple grep. At larger scale, consider qmd (BM25/vector + LLM re-ranking).
"""

import argparse
import os
import re
import sys
from pathlib import Path


def search_grep(root: Path, query: str, context_lines: int = 2) -> list[dict]:
    """Simple grep-based search."""
    results = []
    pattern = re.compile(query, re.IGNORECASE)
    for md_file in root.rglob("*.md"):
        # Skip raw/ sources unless explicitly included
        if "raw/" in md_file.parts:
            continue
        try:
            lines = md_file.read_text().split("\n")
        except Exception:
            continue
        for i, line in enumerate(lines):
            if pattern.search(line):
                # Get surrounding context
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                snippet = "\n".join(f"  {j+1}: {lines[j]}" for j in range(start, end))
                results.append({
                    "file": md_file.relative_to(root),
                    "line": i + 1,
                    "match": line.strip(),
                    "context": snippet,
                })
    return results


def main():
    parser = argparse.ArgumentParser(description="Search LLM Wiki pages.")
    parser.add_argument("query", help="Search query (regex supported)")
    parser.add_argument("--wiki", default=".", help="Wiki root directory (default: .)")
    parser.add_argument("--context", type=int, default=2, help="Lines of context around matches (default: 2)")
    args = parser.parse_args()

    wiki_root = Path(args.wiki).resolve()

    if not (wiki_root / "pages").exists():
        print("ERROR: No pages/ directory found.")
        sys.exit(1)

    results = search_grep(wiki_root, args.query, context_lines=args.context)

    if not results:
        print(f"No matches found for: {args.query}")
        sys.exit(0)

    print(f"Found {len(results)} match(es) for: {args.query}")
    print()
    for r in results:
        print(f">>> {r['file']} (line {r['line']})")
        print(r["context"])
        print()


if __name__ == "__main__":
    main()