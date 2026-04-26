#!/usr/bin/env python3
"""
Fetch content from wiki pages by their paths.
Usage: python fetch_pages.py <path1> <path2> ...
       python fetch_pages.py --list file_with_paths.txt
"""

import os
import sys
import json
import argparse
from pathlib import Path


def find_wiki():
    """Auto-discover wiki location by searching common paths."""
    # 1. WIKI_PATH environment variable (highest priority)
    wiki_path = os.environ.get("WIKI_PATH")
    if wiki_path:
        wiki = Path(wiki_path)
        if (wiki / "WIKI.md").exists():
            return wiki
        if wiki.is_dir():
            return wiki

    # 2. .ai-skills-wiki file in home directory
    config_file = Path.home() / ".ai-skills-wiki"
    if config_file.exists():
        wiki_path = config_file.read_text().strip()
        wiki = Path(wiki_path)
        if wiki.exists() and (wiki / "WIKI.md").exists():
            return wiki

    # 3. Common wiki paths
    search_paths = [
        Path(os.path.expanduser("~/.ai-skills/wiki")),
        Path(os.path.expanduser("~/Documents/ai-skills-wiki")),
        Path(os.path.expanduser("~/Library/Mobile Documents/iCloud~md~obsidian/Documents/llm-wiki")),
        Path(os.path.expanduser("~/obsidian/llm-wiki")),
        Path("/llm-wiki"),
    ]

    # 4. Check cwd for WIKI.md
    cwd = Path.cwd()
    if (cwd / "WIKI.md").exists():
        return cwd

    for search_path in search_paths:
        if (search_path / "WIKI.md").exists():
            return search_path

    # Fallback to default Obsidian path
    return search_paths[2]


WIKI_VAULT = find_wiki()


def fetch_page(relative_path):
    """Fetch a single page's content."""
    path = WIKI_VAULT / relative_path
    
    if not path.exists():
        return {"error": f"File not found: {path}", "path": relative_path}
    
    if not path.is_file():
        return {"error": f"Not a file: {path}", "path": relative_path}
    
    try:
        content = path.read_text(encoding="utf-8")
        
        # Extract frontmatter
        lines = content.split("\n")
        frontmatter = {}
        body_start = 0
        
        if lines and lines[0].strip() == "---":
            for i in range(1, len(lines)):
                if lines[i].strip() == "---":
                    body_start = i + 1
                    break
                if ":" in lines[i]:
                    key, val = lines[i].split(":", 1)
                    frontmatter[key.strip()] = val.strip()
        
        body = "\n".join(lines[body_start:]).strip()
        
        return {
            "path": relative_path,
            "full_path": str(path),
            "frontmatter": frontmatter,
            "body": body,
            "raw": content
        }
    except Exception as e:
        return {"error": str(e), "path": relative_path}


def fetch_multiple(paths):
    """Fetch multiple pages."""
    results = []
    for path in paths:
        path = path.strip()
        if path:
            result = fetch_page(path)
            results.append(result)
    return results


def format_page(page):
    """Format a single page for display."""
    if "error" in page:
        return f"ERROR: {page['error']}"
    
    output = []
    output.append(f"\n{'='*70}")
    output.append(f"PAGE: {page['path']}")
    output.append(f"{'='*70}")
    
    if page.get("frontmatter"):
        output.append("\nFrontmatter:")
        for k, v in page["frontmatter"].items():
            output.append(f"  {k}: {v}")
    
    output.append(f"\n--- Content ---")
    output.append(page.get("body", "")[:2000])
    
    if len(page.get("body", "")) > 2000:
        output.append(f"\n... [truncated, full length: {len(page['body'])} chars]")
    
    return "\n".join(output)


def main():
    parser = argparse.ArgumentParser(description="Fetch wiki page content")
    parser.add_argument("paths", nargs="*", help="Page paths relative to wiki root")
    parser.add_argument("--list", type=str, help="File containing list of paths (one per line)")
    args = parser.parse_args()
    
    paths = []
    
    if args.list:
        list_file = Path(args.list)
        if list_file.exists():
            paths.extend(list_file.read_text().splitlines())
    
    paths.extend(args.paths)
    
    if not paths:
        print("Usage: fetch_pages.py <path1> <path2> ...\n       fetch_pages.py --list paths.txt")
        return
    
    print(f"Fetching {len(paths)} pages from wiki...", file=sys.stderr)
    print(f"Wiki vault: {WIKI_VAULT}", file=sys.stderr)
    
    results = fetch_multiple(paths)
    
    # Human-readable output to stderr
    for page in results:
        print(format_page(page), file=sys.stderr)
    
    # JSON output for programmatic use
    print("\n\n--- JSON OUTPUT ---", file=sys.stderr)
    print(json.dumps(results, indent=2), file=sys.stderr)


if __name__ == "__main__":
    main()
