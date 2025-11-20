"""Configuration settings for the dataset generator."""

import os
from pathlib import Path


class Config:
    """Configuration settings for the dataset generator."""
    
    def __init__(self):
        self.api_base = os.getenv("LLM_API_BASE", "http://127.0.0.1:1234")
        self.model_name = os.getenv("MODEL_NAME", "local-model")
        self.default_source_dir = Path(os.getenv("INFO_SOURCE_DIR", "config/input/website/content/en/docs"))
        self.default_output_dir = Path(os.getenv("INFO_OUTPUT_DIR", "output"))
        self.workers = int(os.getenv("INFO_WORKERS", "1"))
        self.max_retries = 3
        self.retry_delay = 2
        self.project_root = Path(__file__).parent.parent
        self.prompt_file = self.project_root / "templates" / "prompt.txt"
        self.log_dir = Path("logs")
        
        self.system_prompt = (
            "You are a dataset generation engine that converts Markdown knowledge into "
            "instruction-output JSONL pairs for LLM fine-tuning."
        )
