---
name: llm-wiki
description: Build and maintain a persistent personal knowledge base using LLMs. Use when the user wants to: (1) create a wiki-based knowledge management system, (2) ingest sources (articles, papers, books) and integrate them into a structured wiki, (3) maintain cross-referenced markdown files that compound over time, (4) set up an LLM-driven knowledge base with raw sources, wiki layer, and schema conventions, (5) do research or deep-dive accumulation on a topic. Triggers: "build a wiki", "set up a knowledge base", "ingest this article into my wiki", "maintain a personal knowledge base", "LLM-based wiki", "personal wiki".
---

# LLM Wiki Skill

Builds and maintains a persistent compounding wiki — a structured directory of LLM-generated markdown files maintained between you and your sources. The wiki grows richer with every source added and every question asked.

## Core Architecture

Three layers:

1. **Raw sources** — immutable source documents (articles, papers, images). Your source of truth. Never modified.
2. **Wiki** — LLM-generated markdown files (summaries, entity pages, concept pages, synthesis). The LLM owns this layer entirely.
3. **Schema** — a configuration file (e.g. `WIKI.md` at root of the wiki directory) that tells the LLM conventions, structure, and workflows.

## Directory Layout

```
wiki/
├── WIKI.md           # Schema: conventions, structure, workflows
├── index.md          # Catalog of all wiki pages with summaries
├── log.md            # Chronological append-only record
├── raw/              # Source documents (immutable)
└── pages/            # LLM-generated wiki pages
    ├── entities/     # People, places, companies
    ├── concepts/     # Topics, ideas, techniques
    ├── sources/      # Per-source summary pages
    └── synthesis/    # Overviews, comparisons, analyses
```

## Workflows

### Setting Up a New Wiki

1. Create the directory structure above
2. Create `WIKI.md` as the schema — describe conventions, page formats, naming, tagging
3. Create `index.md` and `log.md` as empty shells
4. Add the first source and run the first ingest

### Ingesting a Source

1. Add the source file to `wiki/raw/`
2. Read the source fully
3. Discuss key takeaways with the user
4. Write a source summary page under `pages/sources/`
5. Update `index.md` with the new page entry
6. Update relevant entity/concept pages across the wiki
7. Add entry to `log.md` with prefix `## [YYYY-MM-DD] ingest | Title`
8. Flag any contradictions with existing pages

A single source typically touches 10-15 wiki pages.

### Answering a Query

1. Read `index.md` to find relevant pages
2. Read relevant pages
3. Synthesize an answer with citations
4. If the answer is valuable (comparison, analysis, connection discovered), file it back into the wiki as a new page

### Linting the Wiki (health-check)

Run periodically. The LLM checks for:
- Contradictions between pages
- Stale claims superseded by newer sources
- Orphan pages with no inbound links
- Concepts mentioned but lacking their own page
- Missing cross-references
- Data gaps that could be filled with a web search
- Log entries without corresponding page updates

## Special Files

### index.md

Content-oriented catalog of all wiki pages. Each entry has a link, one-line summary, and optional metadata (date, source count). Organized by category. The LLM updates it on every ingest. Read this first when answering queries.

### log.md

Append-only chronological record of what happened and when. Each entry starts with a consistent prefix like `## [YYYY-MM-DD]`. Parseable with `grep "^## \[" log.md | tail -5`. Gives a timeline of the wiki's evolution.

## Recommended Tools

- **Obsidian** — the IDE for the wiki. Graph view shows the shape of the knowledge base.
- **Obsidian Web Clipper** — browser extension to convert web articles to markdown for raw sources.
- **Marp** — markdown-based slide decks. Useful for presentations from wiki content.
- **Dataview** — Obsidian plugin for querying page frontmatter, generates dynamic tables.
- **qmd** — local search engine for markdown files (BM25/vector + LLM re-ranking). CLI and MCP server available.

## Tips

- Download images locally (Obsidian: Settings → Files and Links → Attachment folder path; hotkey Ctrl+Shift+D to download)
- The wiki is just a git repo — version history and branching come for free
- LLMs can't read markdown + inline images in one pass — read text first, then view referenced images separately
- Batch-ingest many sources at once for speed; ingest one at a time for depth and quality control
- Good answers filed back into the wiki compound just like sources do

## Scripts

- `scripts/new_wiki.py` — scaffold a new wiki directory structure
- `scripts/ingest.py` — process a raw source and scaffold wiki pages
- `scripts/lint.py` — health-check the wiki for orphans, stale claims, broken links
- `scripts/search.py` — search wiki pages by keyword or topic

All scripts accept `--help` for usage. Run from the wiki root directory.