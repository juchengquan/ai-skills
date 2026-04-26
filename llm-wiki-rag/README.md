# llm-wiki-rag

Automated Wiki RAG skill for answering questions from a personal knowledge base.

## Structure

```
llm-wiki-rag/
├── SKILL.md              # Skill definition & workflow
├── README.md             # This file
└── scripts/
    ├── search_wiki.py    # Keyword search across wiki
    ├── fetch_pages.py    # Fetch page content
    └── answer.py         # Full RAG pipeline
```

## Quick Start

```bash
# Search
python3 scripts/search_wiki.py "harness design" --top-k 3

# Fetch specific pages
python3 scripts/fetch_pages.py pages/concepts/harness-design.md

# Full RAG flow
python3 scripts/answer.py "harness design principles"
```

## Architecture

```
User Query → search_wiki.py → fetch_pages.py → answer.py → LLM → Answer + Citations
                                                        ↓
                                                  Writeback Proposal
```

## Search Tip

Use **keyword queries** not full sentences:
- ✅ `"harness design"` 
- ❌ `"What is harness design?"`

For full-sentence semantic search, use OpenClaw's `memory_search(corpus=wiki)`.

## TODO

- [x] Keyword search
- [x] Page fetching
- [x] RAG pipeline with citations
- [ ] Vector/semantic search upgrade
- [ ] LLM API integration (auto-answer)
- [ ] Writeback with approval gate
