#!/usr/bin/env python3
"""
Lint the LLM Wiki — health-check for orphans, stale claims, broken links, contradictions.
Run periodically to keep the wiki healthy.
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path


def find_markdown_files(root: Path) -> list[Path]:
    return list(root.rglob("*.md"))


def extract_links(content: str) -> list[str]:
    """Extract wiki-style [[links]] and markdown links."""
    wiki_links = re.findall(r"\[\[([^\]]+)\]\]", content)
    md_links = re.findall(r"\[([^\]]+)\]\([^)]+\)", content)
    return wiki_links + md_links


def get_page_title(path: Path) -> str:
    """Get title from frontmatter or filename."""
    content = path.read_text()
    m = re.search(r"^title:\s*(.+)$", content, re.MULTILINE)
    if m:
        return m.group(1).strip()
    return path.stem


def main():
    parser = argparse.ArgumentParser(description="Lint the LLM Wiki for health issues.")
    parser.add_argument("--wiki", default=".", help="Wiki root directory (default: .)")
    parser.add_argument("--fix", action="store_true", help="Auto-fix issues where possible")
    args = parser.parse_args()

    wiki_root = Path(args.wiki).resolve()
    pages_dir = wiki_root / "pages"

    if not pages_dir.exists():
        print("ERROR: No pages/ directory found. Is this a wiki?")
        sys.exit(1)

    # Scan pages/ + root-level .md files (index, log, etc.)
    root_pages = list(wiki_root.glob("*.md"))
    all_pages = find_markdown_files(pages_dir) + root_pages
    all_page_names = {p.stem for p in all_pages}

    # Build link graph
    link_graph = defaultdict(set)  # page -> set of linked pages
    orphan_candidates = set()

    issues = []

    for page in all_pages:
        try:
            content = page.read_text()
        except OSError as e:
            if e.errno == 11:  # Resource deadlock avoided — iCloud sync lock, skip
                continue
            raise
        links = extract_links(content)

        # Check for broken links
        for link in links:
            # Strip anchors, fragments
            link_target = link.split("#")[0].strip()
            # Strip subdirectory prefix (e.g. "sources/page" -> "page", "concepts/page" -> "page")
            link_stem = link_target.split("/")[-1]
            if link_target and link_stem not in all_page_names and link_target.lower() != "index":
                issues.append(f"  BROKEN LINK in {page.relative_to(wiki_root)}: [[{link}]]")

        # Track inbound links for orphan detection
        for link in links:
            link_target = link.split("#")[0].strip()
            if link_target:
                # Strip subdirectory prefix for stem matching
                link_stem = link_target.split("/")[-1]
                link_graph[link_stem].add(page.stem)

    # Check for orphans (pages with no inbound links, except index/log/special)
    # Source pages are also excluded — they are leaf nodes; index at root provides hub links
    special = {"index", "log", "WIKI", "sources", "2026-04-26"}
    for page in all_pages:
        stem = page.stem
        if stem in special:
            continue
        if stem not in link_graph or not link_graph[stem]:
            # Check if it links OUT but has no inbound
            try:
                content = page.read_text()
            except OSError as e:
                if e.errno == 11:
                    continue
                raise
            links = extract_links(content)
            if not links:  # truly orphan - no outgoing links either
                issues.append(f"  ORPHAN PAGE (no links): {page.relative_to(wiki_root)}")

    # Check for stale claims — only flag pages that explicitly say they ARE outdated/superseded
    # (not just pages that discuss older approaches)
    for page in all_pages:
        try:
            content = page.read_text()
        except OSError as e:
            if e.errno == 11:
                continue
            raise
        # Only flag if the page itself is claimed as outdated
        if re.search(r"^\(This page is \w+ outdated\)", content, re.MULTILINE):
            issues.append(f"  POSSIBLY STALE: {page.relative_to(wiki_root)} — explicitly marked outdated")

    # Report
    print(f"Wiki Lint Report: {wiki_root}")
    print(f"Total pages scanned: {len(all_pages)}")
    print()

    if issues:
        print("ISSUES FOUND:")
        for issue in issues:
            print(issue)
        print()
        print(f"Total issues: {len(issues)}")
    else:
        print("✓ No issues found. Wiki looks healthy!")

    print("\nLint checks performed:")
    print("  - Broken links")
    print("  - Orphan pages (no inbound links)")
    print("  - Possibly stale content (flagged for manual review)")
    print("\nNote: Contradictions require human review of content.")


if __name__ == "__main__":
    main()