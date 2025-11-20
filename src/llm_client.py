"""LLM API client for generating datasets."""

import time
from typing import List, Dict, Any

from openai import OpenAI
from config import Config


class LLMClient:
    """Handles LLM API interactions."""
    
    def __init__(self, config: Config):
        self.config = config
        self.client = OpenAI(
            base_url=f"{config.api_base.rstrip('/')}/v1",
            api_key="dummy"
        )
        self._prompt_template = None
    
    @property
    def prompt_template(self) -> str:
        """Lazy load prompt template."""
        if self._prompt_template is None:
            if not self.config.prompt_file.exists():
                raise FileNotFoundError(f"Prompt template file not found: {self.config.prompt_file}")
            self._prompt_template = self.config.prompt_file.read_text(encoding="utf-8")
        return self._prompt_template
    
    def build_messages(self, context: str) -> List[Dict[str, Any]]:
        instruction = self.prompt_template.replace("{context}", context.strip())
        return [
            {"role": "system", "content": self.config.system_prompt},
            {"role": "user", "content": instruction},
        ]
    
    def call_llm(self, messages: List[Dict[str, Any]]) -> str:
        for attempt in range(self.config.max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.config.model_name,
                    messages=messages,
                    max_tokens=4096,
                    temperature=0.7,
                    top_p=0.85,
                    n=1,
                    timeout=120
                )
                return response.choices[0].message.content
            except Exception as e:
                if attempt < self.config.max_retries - 1:
                    print(f"LLM call failed (attempt {attempt + 1}/{self.config.max_retries}): {e}")
                    time.sleep(self.config.retry_delay)
                else:
                    raise e
