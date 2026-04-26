# AI Skills

A collection of Claude Code skills for building and querying a personal knowledge base powered by LLMs.

## Skills

### llm-wiki

Build and maintain a persistent compounding wiki — a structured directory of LLM-generated markdown files that grows richer with every source added and every question asked.

**Architecture:**
- **Raw sources** — immutable source documents (articles, papers, images)
- **Wiki** — LLM-generated markdown files (summaries, entity pages, concept pages, synthesis)
- **Schema** — configuration file defining conventions and workflows

**Features:**
- Ingest sources and generate interconnected wiki pages
- Cross-reference entities, concepts, and sources
- Lint for contradictions, stale claims, and orphans
- Search across accumulated knowledge

**Scripts:** `new_wiki.py`, `ingest.py`, `lint.py`, `search.py`

### llm-wiki-rag

Ask questions against your personal wiki and get cited answers using RAG.

**Usage:**
```bash
python3 llm-wiki-rag/scripts/answer.py "your question" --top-k 5
```

**Scripts:** `search_wiki.py`, `fetch_pages.py`, `answer.py`

## Getting Started

1. Set up a wiki with `llm-wiki/scripts/new_wiki.py`
2. Ingest sources with `llm-wiki/scripts/ingest.py`
3. Query your knowledge base with `llm-wiki-rag/scripts/answer.py`

## Requirements

- Python 3.x
- Claude Code with skill support
- For RAG: a configured LLM API key

See individual skill SKILL.md files for detailed documentation.