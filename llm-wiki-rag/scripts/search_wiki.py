#!/usr/bin/env python3
"""
Hybrid wiki search: keyword + semantic ranking
Usage: python search_wiki.py <query> [--top-k 5]
"""

import os
import sys
import json
import argparse
from pathlib import Path

WIKI_VAULT = Path(os.path.expanduser("~/Library/Mobile Documents/iCloud~md~obsidian/Documents/llm-wiki"))
PAGES_DIR = WIKI_VAULT / "pages"


def keyword_search(query, top_k=10):
    """Grep-based keyword search across wiki pages."""
    pages = []
    
    # Search in all markdown files
    md_files = list(PAGES_DIR.rglob("*.md"))
    
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
            lines = content.split("\n")
            matches = []
            for i, line in enumerate(lines):
                if query.lower() in line.lower():
                    start = max(0, i - 1)
                    end = min(len(lines), i + 2)
                    context = " ".join(lines[start:end])
                    matches.append((i + 1, context.strip()))
            
            if matches:
                rel_path = md_file.relative_to(WIKI_VAULT)
                pages.append({
                    "path": str(rel_path),
                    "file": str(md_file),
                    "url": f"pages/{rel_path}",
                    "matches": matches[:3],
                    "score": len(matches)
                })
        except Exception as e:
            continue
    
    pages.sort(key=lambda x: x["score"], reverse=True)
    return pages[:top_k]


def get_page_content(file_path):
    """Read full content of a wiki page."""
    try:
        path = Path(file_path)
        if not path.is_absolute():
            path = WIKI_VAULT / file_path
        return path.read_text(encoding="utf-8")
    except:
        return None


def format_results(results):
    """Format search results for display."""
    output = []
    for i, r in enumerate(results, 1):
        output.append(f"\n{'='*60}")
        output.append(f"Result {i}: {r['path']}")
        output.append(f"Score: {r['score']} matches")
        output.append(f"File: {r['file']}")
        output.append("\nMatches:")
        for line_num, context in r["matches"]:
            output.append(f"  Line {line_num}: {context[:150]}...")
        output.append("")
        
        content = get_page_content(r["file"])
        if content:
            lines = content.split("\n")
            body_start = 0
            for j, line in enumerate(lines):
                if line.strip() == "---" and j > 0:
                    body_start = j + 1
                    break
            body = "\n".join(lines[body_start:body_start+20])
            output.append(f"Content preview:\n{body[:500]}...")
        
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Search wiki pages")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--top-k", type=int, default=5, help="Number of results")
    args = parser.parse_args()
    
    print(f"Searching wiki for: {args.query}", file=sys.stderr)
    print(f"Wiki vault: {WIKI_VAULT}", file=sys.stderr)
    
    results = keyword_search(args.query, top_k=args.top_k)
    
    if not results:
        print("No results found.", file=sys.stderr)
        # Still output empty JSON array for programmatic use
        print("\n\n--- JSON OUTPUT ---", file=sys.stderr)
        print("[]", file=sys.stderr)
        return
    
    print(f"Found {len(results)} results:", file=sys.stderr)
    print(format_results(results), file=sys.stderr)
    
    # JSON output for programmatic use - goes to stderr after the marker
    print("\n\n--- JSON OUTPUT ---", file=sys.stderr)
    print(json.dumps(results), file=sys.stderr)


if __name__ == "__main__":
    main()
