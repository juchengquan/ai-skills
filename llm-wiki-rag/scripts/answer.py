#!/usr/bin/env python3
"""
Full RAG flow: search wiki → fetch pages → answer question
Usage: python answer.py "<question>" [--top-k 5]

When LLM_API_KEY is set, calls MiniMax API directly.
Otherwise, outputs structured context for LLM synthesis.
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path

# Configuration
SCRIPT_DIR = Path(__file__).parent


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
PAGES_DIR = WIKI_VAULT / "pages"


def search_wiki(query, top_k=5):
    """Search wiki using the search_wiki script."""
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "search_wiki.py"), query, "--top-k", str(top_k)],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stderr
        marker = "--- JSON OUTPUT ---"
        json_start = output.find(marker)
        
        if json_start != -1:
            json_str = output[json_start + len(marker):].strip()
            return json.loads(json_str)
        
    except Exception as e:
        print(f"Search error: {e}", file=sys.stderr)
    return []


def fetch_pages(paths):
    """Fetch content from multiple pages."""
    try:
        result = subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "fetch_pages.py")] + paths,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stderr
        marker = "--- JSON OUTPUT ---"
        json_start = output.find(marker)
        
        if json_start != -1:
            json_str = output[json_start + len(marker):].strip()
            return json.loads(json_str)
        
    except Exception as e:
        print(f"Fetch error: {e}", file=sys.stderr)
    return []


def build_context(pages):
    """Build context string from fetched pages."""
    context_parts = []
    
    for page in pages:
        if "error" in page:
            continue
        
        rel_path = page["path"]
        
        context_parts.append(f"\n{'='*60}")
        context_parts.append(f"Source: [[{rel_path}]]")
        context_parts.append(f"{'='*60}")
        
        title = page.get("frontmatter", {}).get("title", rel_path)
        context_parts.append(f"# {title}\n")
        
        body = page.get("body", "")
        context_parts.append(body)
    
    return "\n".join(context_parts)


def call_minimax_api(prompt, api_key):
    """Call MiniMax API for chat completion."""
    try:
        import requests
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "MiniMax-M2.7",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant answering questions based on a personal wiki. Always cite sources using [[filename]] notation."},
                {"role": "user", "content": prompt}
            ]
        }
        
        response = requests.post(
            "https://api.minimax.io/v1/text/chatcompletion_v2",
            headers=headers,
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        else:
            return f"API Error {response.status_code}: {response.text}"
            
    except ImportError:
        return "Error: 'requests' library not installed. Run: pip install requests"
    except Exception as e:
        return f"Error: {str(e)}"


def generate_answer(question, context, api_key=None):
    """Generate answer - either via API or return prompt for manual answering."""
    
    prompt = f"""You are answering a question using a personal wiki as your knowledge base.

## Question
{question}

## Context from Wiki
{context}

## Instructions
1. Answer the question based only on the context provided
2. Cite your sources using [[filename]] notation inline
3. If the wiki doesn't contain enough information, say so honestly
4. Highlight any valuable insights or connections discovered
5. Keep the answer focused and well-structured

## Answer"""

    if api_key:
        return call_minimax_api(prompt, api_key)
    else:
        return None, prompt


def suggest_writeback(question, answer, sources):
    """Suggest content to write back to the wiki."""
    suggestions = []
    
    if len(sources) > 2:
        suggestions.append({
            "type": "synthesis",
            "trigger": f"Consulted {len(sources)} wiki pages",
            "action": "Consider creating a synthesis page connecting these concepts"
        })
    
    suggestions.append({
        "type": "concept_note",
        "trigger": f"Question: {question[:100]}...",
        "action": "Review if a new concept page should be created"
    })
    
    return suggestions


def main():
    parser = argparse.ArgumentParser(description="Wiki RAG - Answer from your wiki")
    parser.add_argument("question", help="Question to answer")
    parser.add_argument("--top-k", type=int, default=5, help="Pages to retrieve")
    parser.add_argument("--api-key", type=str, help="MiniMax API key (or set MINIMAX_API_KEY env)")
    args = parser.parse_args()
    
    # Get API key from args or environment
    api_key = args.api_key or os.environ.get("MINIMAX_API_KEY") or os.environ.get("OPENAI_API_KEY")
    
    print("="*60, file=sys.stderr)
    print("LLM Wiki RAG", file=sys.stderr)
    print("="*60, file=sys.stderr)
    print(f"Wiki: {WIKI_VAULT}", file=sys.stderr)
    print(f"Question: {args.question}", file=sys.stderr)
    print(f"Top-k: {args.top_k}", file=sys.stderr)
    print(f"API mode: {'MiniMax API' if api_key else 'Prompt output (no API key)'}") 
    print(file=sys.stderr)
    
    # Step 1: Search
    print("Step 1: Searching wiki...", file=sys.stderr)
    search_results = search_wiki(args.question, top_k=args.top_k)
    print(f"Found {len(search_results)} relevant pages", file=sys.stderr)
    
    if not search_results:
        print("\nNo relevant pages found.")
        return
    
    # Step 2: Fetch
    print("\nStep 2: Fetching pages...", file=sys.stderr)
    paths = [r["file"] for r in search_results]
    pages = fetch_pages(paths)
    print(f"Fetched {len(pages)} pages", file=sys.stderr)
    
    # Step 3: Build context
    print("\nStep 3: Building context...", file=sys.stderr)
    context = build_context(pages)
    print(f"Context: {len(context)} chars", file=sys.stderr)
    
    # Step 4: Generate answer
    print("\nStep 4: Generating answer...", file=sys.stderr)
    
    if api_key:
        answer = call_minimax_api(
            f"""Answer this question based on the wiki context below.

Question: {args.question}

Context:
{context}

Answer with citations using [[filename]] notation.""",
            api_key
        )
        print("\n" + "="*60)
        print("ANSWER:")
        print("="*60)
        print(answer)
    else:
        # Output structured format for manual LLM answering
        output = {
            "question": args.question,
            "sources": [r["path"] for r in search_results],
            "context": context,
            "answer_prompt": f"""You are answering a question using a personal wiki.

Question: {args.question}

Context from Wiki:
{context}

Instructions:
1. Answer based only on the context
2. Cite sources using [[filename]] notation
3. Be focused and well-structured

Answer:"""
        }
        
        print("\n" + "="*60)
        print("STRUCTURED OUTPUT (for LLM synthesis):")
        print("="*60)
        print(json.dumps(output, indent=2, ensure_ascii=False))
        
        print("\n" + "="*60, file=sys.stderr)
        print("SOURCES:", file=sys.stderr)
        print("="*60, file=sys.stderr)
        for r in search_results:
            print(f"  - {r['path']} (score: {r['score']})", file=sys.stderr)
        
        print("\nSet MINIMAX_API_KEY env var or use --api-key for auto-answer.", file=sys.stderr)

if __name__ == "__main__":
    main()
