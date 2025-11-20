"""Dataset processor for converting markdown to JSONL."""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Iterable

from config import Config
from llm_client import LLMClient


class DatasetProcessor:
    """Processes markdown files into JSONL datasets."""
    
    def __init__(self, config: Config, llm_client: LLMClient):
        self.config = config
        self.llm_client = llm_client
    
    def find_markdown_files(self, root: Path) -> Iterable[Path]:
        if not root.exists():
            raise FileNotFoundError(f"Source directory not found: {root}")
        return sorted(path for path in root.rglob("*.md") if path.is_file())
    
    def derive_output_path(self, md_path: Path, source_root: Path, output_root: Path) -> Path:
        try:
            relative = md_path.relative_to(source_root)
        except ValueError:
            relative = Path(md_path.name)
        return (output_root / relative).with_suffix(".jsonl")
    
    def normalize_jsonl(self, text: str) -> str:
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
    
    def save_prompt_log(self, md_path: Path, messages: List[Dict[str, Any]]):
        """Save prompt to log directory."""
        self.config.log_dir.mkdir(exist_ok=True)
        log_path = self.config.log_dir / f"{md_path.stem}_prompt.json"
        log_path.write_text(json.dumps(messages, indent=2), encoding="utf-8")
    
    def process_file(self, md_path: Path, source_root: Path, output_root: Path, current: int, total: int):
        output_path = self.derive_output_path(md_path, source_root, output_root)
        
        print(f"[{current}/{total}] Processing: {md_path}")
        print(f"Output: {output_path}")
        
        # Skip if already processed
        if output_path.exists():
            print(f"SKIPPED - Already processed | Remaining: {total - current}")
            return
        
        context = md_path.read_text(encoding="utf-8")
        messages = self.llm_client.build_messages(context)
        
        self.save_prompt_log(md_path, messages)
        
        start_time = time.time()
        response = self.llm_client.call_llm(messages)
        processing_time = time.time() - start_time
        
        jsonl_output = self.normalize_jsonl(response)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(jsonl_output, encoding="utf-8")
        print(f"SUCCESS - Saved JSONL | LLM Time: {processing_time:.2f}s | Remaining: {total - current}")
    
    def process_directory(self, source_root: Path, output_root: Path):
        markdown_files = list(self.find_markdown_files(source_root))
        if not markdown_files:
            print(f"No Markdown files found under {source_root}")
            return

        total_files = len(markdown_files)
        print(f"Found {total_files} Markdown files under {source_root}")
        output_root.mkdir(parents=True, exist_ok=True)

        for i, md_file in enumerate(markdown_files, 1):
            try:
                self.process_file(md_file, source_root, output_root, i, total_files)
            except Exception as exc:
                print(f"ERROR - Failed processing: {exc} | Remaining: {total_files - i}")
                continue
            print()  # Empty line for readability
