#!/usr/bin/env python3
"""
Scan a directory for Markdown files, send each file's content to a local LLM API,
and write the generated instruction-output JSONL to a mirrored directory tree.
"""

import argparse
from pathlib import Path

from config import Config
from llm_client import LLMClient
from processor import DatasetProcessor


def parse_args():
    config = Config()
    parser = argparse.ArgumentParser(description="Generate JSONL pairs from Markdown docs.")
    parser.add_argument("--source", type=Path, default=config.default_source_dir, help="Directory to scan for .md files.")
    parser.add_argument("--output", type=Path, default=config.default_output_dir, help="Directory to write JSONL files.")
    return parser.parse_args()


def main():
    args = parse_args()
    config = Config()
    llm_client = LLMClient(config)
    processor = DatasetProcessor(config, llm_client)
    
    source_root = args.source.resolve()
    output_root = args.output.resolve()
    
    processor.process_directory(source_root, output_root)


if __name__ == "__main__":
    main()
