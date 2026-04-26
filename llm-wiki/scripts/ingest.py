#!/usr/bin/env python3
"""
Ingest a raw source into the LLM Wiki.
Reads a source file, extracts metadata, scaffolds wiki pages, and updates index/log.
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import date


def slugify(name: str) -> str:
    return name.lower().replace(" ", "-").replace("_", "-")


def frontmatter(title: str, tags=None, sources=None, created=None):
    fm = ["---", f"title: {title}", f"created: {created or date.today().isoformat()}"]
    if tags:
        fm.append(f"tags: [{', '.join(tags)}]")
    if sources:
        fm.append(f"sources: [{', '.join(sources)}]")
    fm.append("---")
    return "\n".join(fm)


def main():
    parser = argparse.ArgumentParser(description="Ingest a raw source into the LLM Wiki.")
    parser.add_argument("source", help="Path to the source file to ingest")
    parser.add_argument("--wiki", default=".", help="Wiki root directory (default: .)")
    parser.add_argument("--title", help="Override page title (default: filename stem)")
    parser.add_argument("--tags", nargs="*", help="Tags for the source page")
    args = parser.parse_args()

    wiki_root = Path(args.wiki).resolve()
    source_path = Path(args.source).resolve()

    if not source_path.exists():
        print(f"ERROR: Source file not found: {source_path}")
        sys.exit(1)

    # Determine raw/ location - copy or link the source
    raw_dir = wiki_root / "raw"
    raw_dir.mkdir(exist_ok=True)

    dest_raw = raw_dir / source_path.name
    if dest_raw.exists():
        print(f"WARNING: {dest_raw} already exists, skipping copy")
    else:
        import shutil
        shutil.copy2(source_path, dest_raw)
        print(f"Copied source to: {dest_raw}")

    # Generate source page
    title = args.title or source_path.stem
    source_page = wiki_root / "pages" / "sources" / f"{slugify(title)}.md"
    source_page.parent.mkdir(parents=True, exist_ok=True)

    content_lines = [
        frontmatter(title, tags=args.tags, sources=[source_path.name]),
        "",
        f"# {title}",
        "",
        "## Overview",
        f"_Source: {source_path.name}_",
        "",
        "## Key Takeaways",
        "- [TODO: LLM to fill after reading source]",
        "",
        "## Notes",
        "- [TODO: LLM to expand with detailed notes]",
        "",
        "## See also",
        "- [[entities/...]]",
        "- [[concepts/...]]",
        "- [[index]]",
    ]

    if source_page.exists():
        print(f"WARNING: Source page {source_page} already exists, skipping")
    else:
        source_page.write_text("\n".join(content_lines))
        print(f"Created source page: {source_page}")

    # Update index
    index_path = wiki_root / "index.md"
    append_text = f"\n- [[sources/{slugify(title)}]] — {title}"
    if index_path.exists():
        index_path.write_text(index_path.read_text() + append_text)
    else:
        index_path.write_text(f"# Wiki Index\n\n## Sources\n{append_text}\n")
    print(f"Updated index: {index_path}")

    # Append log
    log_path = wiki_root / "log.md"
    log_entry = f"\n## [{date.today().isoformat()}] ingest | {title}"
    if log_path.exists():
        log_path.write_text(log_path.read_text() + log_entry)
    else:
        log_path.write_text(f"# Wiki Log\n{log_entry}\n")
    print(f"Updated log: {log_path}")

    print("\n✓ Ingest complete. Next steps:")
    print("  1. LLM reads the raw source and fills in Key Takeaways + Notes")
    print("  2. Update entity/concept pages as needed")
    print("  3. Update cross-references in See also sections")


if __name__ == "__main__":
    main()