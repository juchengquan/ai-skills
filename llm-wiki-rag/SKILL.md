---
name: llm-wiki-rag
description: Ask questions against your personal wiki and get cited answers. Use when: (1) user asks about concepts in their llm-wiki, (2) researching topics covered in their knowledge base, (3) searching accumulated notes. Triggers: "search my wiki", "what does my wiki say about X", "ask my knowledge base", "wiki RAG", "from my wiki".
---

# Wiki RAG Skill

Answer questions using your personal wiki as a knowledge base with cited sources.

## How It Works

```
User Question → search → fetch → synthesize → cite → answer
```

## Usage

Use exec tool to run the scripts:

```bash
# Ask a question (outputs structured JSON)
python3 /Users/user_name/.openclaw/workspace/_repository/llm-wiki-rag/scripts/answer.py "<question>" --top-k 5
```

## Search Tips

- Use **keyword queries** not full sentences
  - ✅ `"harness design"` 
  - ❌ `"What is harness design?"`
- For better results, use specific terms from wiki pages

## Workflow

1. **Run answer.py** with the user's question
2. **Parse JSON output** (look for `answer_prompt` field)
3. **Synthesize answer** using the context
4. **Cite sources** using [[filename]] notation
5. **Propose writeback** if valuable insights found

## Wiki Location

The skill automatically discovers your wiki with this priority:

1. **`WIKI_PATH`** environment variable — explicit path
2. **`~/.ai-skills-wiki`** file — contains wiki path (one line)
3. Common paths checked for `WIKI.md`:
   - `~/.ai-skills/wiki`
   - `~/Documents/ai-skills-wiki`
   - `~/Library/Mobile Documents/iCloud~md~obsidian/Documents/llm-wiki/` (Obsidian iCloud)
   - `~/obsidian/llm-wiki`
   - `/llm-wiki`
4. Current working directory (if it contains `WIKI.md`)

**To set a custom wiki:**
```bash
export WIKI_PATH=/path/to/your/wiki
```

Or create `~/.ai-skills-wiki` with the path on a single line.

## Scripts

| Script | Purpose |
|--------|---------|
| `search_wiki.py <query> [--top-k N]` | Keyword search |
| `fetch_pages.py <path1> <path2>...` | Fetch page content |
| `answer.py "<question>" [--top-k N]` | Full RAG pipeline |

## Citation Format

Always cite wiki sources:

```
According to [[pages/concepts/harness-design.md]]:
> relevant quote

Source: pages/concepts/harness-design.md
```

## Example Invocation

```bash
python3 answer.py "harness design" --top-k 3
```

Parse the JSON output, extract `context` and `sources`, then synthesize an answer.
