#!/usr/bin/env python3
"""
Scan a directory for Markdown files, send each file's content to a local LLM API,
and write the generated instruction-output JSONL to a mirrored directory tree.
"""

from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path
from typing import List, Dict, Any, Iterable

from openai import OpenAI

API_BASE = os.getenv("LLM_API_BASE", "http://127.0.0.1:1234")
MODEL_NAME = os.getenv("MODEL_NAME", "local-model")
DEFAULT_SOURCE_DIR = Path(os.getenv("INFO_SOURCE_DIR", "config/input/website/content/en/docs"))
DEFAULT_OUTPUT_DIR = Path(os.getenv("INFO_OUTPUT_DIR", "output"))
DEFAULT_WORKERS = int(os.getenv("INFO_WORKERS", "1"))
MAX_RETRIES = 3
RETRY_DELAY = 2

SYSTEM_PROMPT = (
    "You are a dataset generation engine that converts Markdown knowledge into "
    "instruction-output JSONL pairs for LLM fine-tuning."
)

# Get the project root directory (parent of src)
PROJECT_ROOT = Path(__file__).parent.parent
PROMPT_FILE = PROJECT_ROOT / "templates" / "prompt.txt"


def load_prompt_template(prompt_path: Path = PROMPT_FILE) -> str:
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt template file not found: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


PROMPT_TEMPLATE = load_prompt_template()


def build_instruction(context: str) -> str:
    return PROMPT_TEMPLATE.replace("{context}", context.strip())


def build_messages(context: str) -> List[Dict[str, Any]]:
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": build_instruction(context)},
    ]


def call_llm(messages: List[Dict[str, Any]]) -> str:
    client = OpenAI(
        base_url=f"{API_BASE.rstrip('/')}/v1",
        api_key="dummy"
    )
    
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                max_tokens=4096,
                temperature=0.7,
                top_p=0.85,
                n=1,
                timeout=120
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                print(f"LLM call failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
                time.sleep(RETRY_DELAY)
            else:
                raise e


def normalize_jsonl(text: str) -> str:
    lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
    valid_lines = []
    for line in lines:
        try:
            json.loads(line)
        except json.JSONDecodeError:
            continue
        valid_lines.append(line)

    if not valid_lines:
        cleaned = text.strip()
        return cleaned + ("\n" if not cleaned.endswith("\n") else "")

    return "\n".join(valid_lines) + "\n"


def find_markdown_files(root: Path) -> Iterable[Path]:
    if not root.exists():
        raise FileNotFoundError(f"Source directory not found: {root}")
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def derive_output_path(md_path: Path, source_root: Path, output_root: Path) -> Path:
    try:
        relative = md_path.relative_to(source_root)
    except ValueError:
        relative = Path(md_path.name)
    return (output_root / relative).with_suffix(".jsonl")


def process_markdown(md_path: Path, source_root: Path, output_root: Path, current: int, total: int):
    output_path = derive_output_path(md_path, source_root, output_root)
    
    print(f"[{current}/{total}] Processing: {md_path}")
    print(f"Output: {output_path}")
    
    # Skip if already processed
    if output_path.exists():
        print(f"SKIPPED - Already processed | Remaining: {total - current}")
        return
    
    context = md_path.read_text(encoding="utf-8")
    messages = build_messages(context)
    
    # Save prompt to log folder
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / f"{md_path.stem}_prompt.json"
    log_path.write_text(json.dumps(messages, indent=2), encoding="utf-8")
    
    start_time = time.time()
    response = call_llm(messages)
    end_time = time.time()
    processing_time = end_time - start_time
    
    jsonl_output = normalize_jsonl(response)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(jsonl_output, encoding="utf-8")
    print(f"SUCCESS - Saved JSONL | LLM Time: {processing_time:.2f}s | Remaining: {total - current}")


def parse_args():
    parser = argparse.ArgumentParser(description="Generate JSONL pairs from Markdown docs.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE_DIR, help="Directory to scan for .md files.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directory to write JSONL files.")
    return parser.parse_args()


def main():
    args = parse_args()
    source_root = args.source.resolve()
    output_root = args.output.resolve()

    markdown_files = list(find_markdown_files(source_root))
    if not markdown_files:
        print(f"No Markdown files found under {source_root}")
        return

    total_files = len(markdown_files)
    print(f"Found {total_files} Markdown files under {source_root}")
    output_root.mkdir(parents=True, exist_ok=True)

    for i, md_file in enumerate(markdown_files, 1):
        try:
            process_markdown(md_file, source_root, output_root, i, total_files)
        except Exception as exc:
            print(f"ERROR - Failed processing: {exc} | Remaining: {total_files - i}")
            continue
        print()  # Empty line for readability


if __name__ == "__main__":
    main()

