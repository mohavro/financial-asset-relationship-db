#!/usr/bin/env python3
"""
Context Chunker for PR Agent
Handles large context by chunking and summarizing content when approaching token limits.
"""

import re
import yaml
import sys
from typing import List, Dict, Tuple
from dataclasses import dataclass
from pathlib import Path

# Try to import tiktoken for accurate token estimation
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("Warning: tiktoken not available, using heuristic token estimation", file=sys.stderr)
    print("For more accurate token counting, install tiktoken: pip install tiktoken", file=sys.stderr)


@dataclass
class ContextChunk:
    """Represents a chunk of context"""
    content: str
    tokens: int
    priority: int
    chunk_type: str  # review_comments, code_changes, test_failures, ci_logs, full_diff


class ContextChunker:
    """
    Manages context chunking for PR agent to avoid token limit errors.
    
    Note: This class is not thread-safe. Do not share instances across threads.
    Create a separate ContextChunker per thread or execution context.
    """
    
    def __init__(self, config_path: str = ".github/pr-agent-config.yml"):
        self.config_path = config_path
        self.config: Dict = {}

        # Load configuration if available
        cfg_file = Path(config_path)
        if cfg_file.exists():
            try:
                with cfg_file.open("r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: failed to load config from {config_path}: {e}", file=sys.stderr)
                self.config = {}

        # Read agent context settings with safe defaults
        agent_cfg = (self.config.get("agent") or {}).get("context") or {}
        self.max_tokens: int = int(agent_cfg.get("max_tokens", 32000))
        self.chunk_size: int = int(agent_cfg.get("chunk_size", max(1, self.max_tokens - 4000)))
        self.overlap_tokens: int = int(agent_cfg.get("overlap_tokens", 2000))
        self.summarization_threshold: int = int(agent_cfg.get("summarization_threshold", int(self.max_tokens * 0.9)))

        # Prepare priority order
        limits_cfg = (self.config.get("limits") or {}).get("fallback") or {}
        self.priority_order: List[str] = limits_cfg.get("priority_order", [
            "review_comments",
            "test_failures",
            "changed_files",
            "ci_logs",
            "full_diff",
        ])
        # Map chunk type to priority index (lower is higher priority)
        self.priority_map: Dict[str, int] = {name: i for i, name in enumerate(self.priority_order)}

        # Setup tokenizer/encoder if tiktoken available
        self._encoder = None
        if TIKTOKEN_AVAILABLE:
            try:
                # Use a common 32k context model encoding if available; fallback to cl100k_base
                self._encoder = tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                print(f"Warning: failed to initialize tiktoken encoder: {e}", file=sys.stderr)
                self._encoder = None

        # Precompiled regexes or any other helpers
        self._whitespace_re = re.compile(r"\s+")
        self.config: Dict = {}

        # Load configuration if available
        cfg_file = Path(config_path)
        if cfg_file.exists():
            try:
                with cfg_file.open("r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: failed to load config from {config_path}: {e}", file=sys.stderr)
                self.config = {}

        # Read agent context settings with safe defaults
        agent_cfg = (self.config.get("agent") or {}).get("context") or {}
        self.max_tokens: int = int(agent_cfg.get("max_tokens", 32000))
        self.chunk_size: int = int(agent_cfg.get("chunk_size", max(1, self.max_tokens - 4000)))
        self.overlap_tokens: int = int(agent_cfg.get("overlap_tokens", 2000))
        self.summarization_threshold: int = int(agent_cfg.get("summarization_threshold", int(self.max_tokens * 0.9)))

        # Prepare priority order
        limits_cfg = (self.config.get("limits") or {}).get("fallback") or {}
        self.priority_order: List[str] = limits_cfg.get("priority_order", [
            "review_comments",
            "test_failures",
            "changed_files",
            "ci_logs",
            "full_diff",
        ])
        # Map chunk type to priority index (lower is higher priority)
        self.priority_map: Dict[str, int] = {name: i for i, name in enumerate(self.priority_order)}

        # Setup tokenizer/encoder if tiktoken available
        self._encoder = None
        if TIKTOKEN_AVAILABLE:
            try:
                # Use a common 32k context model encoding if available; fallback to cl100k_base
                self._encoder = tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                print(f"Warning: failed to initialize tiktoken encoder: {e}", file=sys.stderr)
                self._encoder = None

        # Precompiled regexes or any other helpers
        self._whitespace_re = re.compile(r"\s+")
        self.config: Dict = {}

        # Load configuration if available
        cfg_file = Path(config_path)
        if cfg_file.exists():
            try:
                with cfg_file.open("r", encoding="utf-8") as f:
                    self.config = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"Warning: failed to load config from {config_path}: {e}", file=sys.stderr)
                self.config = {}

        # Read agent context settings with safe defaults
        agent_cfg = (self.config.get("agent") or {}).get("context") or {}
        self.max_tokens: int = int(agent_cfg.get("max_tokens", 32000))
        self.chunk_size: int = int(agent_cfg.get("chunk_size", max(1, self.max_tokens - 4000)))
        self.overlap_tokens: int = int(agent_cfg.get("overlap_tokens", 2000))
        self.summarization_threshold: int = int(agent_cfg.get("summarization_threshold", int(self.max_tokens * 0.9)))

        # Prepare priority order
        limits_cfg = (self.config.get("limits") or {}).get("fallback") or {}
        self.priority_order: List[str] = limits_cfg.get("priority_order", [
            "review_comments",
            "test_failures",
            "changed_files",
            "ci_logs",
            "full_diff",
        ])
        # Map chunk type to priority index (lower is higher priority)
        self.priority_map: Dict[str, int] = {name: i for i, name in enumerate(self.priority_order)}

        # Setup tokenizer/encoder if tiktoken available
        self._encoder = None
        if TIKTOKEN_AVAILABLE:
            try:
                # Use a common 32k context model encoding if available; fallback to cl100k_base
                self._encoder = tiktoken.get_encoding("cl100k_base")
            except Exception as e:
                print(f"Warning: failed to initialize tiktoken encoder: {e}", file=sys.stderr)
                self._encoder = None

        # Precompiled regexes or any other helpers
        self._whitespace_re = re.compile(r"\s+")
    def _build_full_content(self, sections: Dict[str, str]) -> str:
        """Build full content when under summarization threshold."""
        return '\n\n---\n\n'.join([
            f"## {section_type.replace('_', ' ').title()}\n\n{content}"
            for section_type, content in sections.items()
        ])

    def _build_limited_content(self, chunks: List[ContextChunk]) -> str:
        """Assemble content from chunks within token limit, adding summaries and omissions."""
        result_parts: List[str] = []
        current_tokens = 0
        included_indices = set()
        omissions: List[str] = []

        # First pass: include full chunks where possible
        for idx, chunk in enumerate(chunks):
            header = f"## {chunk.chunk_type.replace('_', ' ').title()}\n\n"
            if current_tokens + chunk.tokens <= self.max_tokens:
                result_parts.append(f"{header}{chunk.content}")
                current_tokens += chunk.tokens
                included_indices.add(idx)

        # Second pass: include summaries for remaining high-priority chunks
        for idx, chunk in enumerate(chunks):
            if idx in included_indices:
                continue
            summary = self.summarize_chunk(chunk)
            summary_tokens = self.estimate_tokens(summary)
            if current_tokens + summary_tokens <= self.max_tokens:
                result_parts.append(summary)
                current_tokens += summary_tokens
                included_indices.add(idx)
            else:
                omissions.append(chunk.chunk_type.upper())

        # Final pass: add a compact omitted notice if anything left out
        if omissions:
            unique_omissions: List[str] = []
            seen = set()
            for o in omissions:
                if o not in seen:
                    seen.add(o)
                    unique_omissions.append(o)
            omitted_note = f"[Omitted due to context limit: {', '.join(unique_omissions)}]"
            if current_tokens + self.estimate_tokens(omitted_note) <= self.max_tokens:
                result_parts.append(omitted_note)

        return '\n\n---\n\n'.join(result_parts)

    def process_context(self, pr_data: Dict) -> Tuple[str, bool]:
        """
        Process PR context and return optimized content.
        Returns: (processed_content, was_chunked)
        """
        sections = self.extract_content_sections(pr_data)
        total_tokens = sum(self.estimate_tokens(content) for content in sections.values())

        if total_tokens <= self.summarization_threshold:
            return self._build_full_content(sections), False

        chunks = self.create_chunks(sections)
        processed_content = self._build_limited_content(chunks)
        return processed_content, True
        return processed_content, True

def main():
    """Example usage"""
    chunker = ContextChunker()
    
    # Example PR data
    example_pr = {
        'reviews': [
            {
                'user': {'login': 'reviewer1'},
                'state': 'changes_requested',
                'body': 'Please fix the bug in the database connection and add tests.'
            }
        ],
        'files': [
            {
                'filename': 'src/data/database.py',
                'additions': 50,
                'deletions': 20,
                'patch': '@@ -1,5 +1,10 @@\n-old code\n+new code'
            }
        ]
    }
    
    processed, chunked = chunker.process_context(example_pr)
    print(f"Chunked: {chunked}")
    print(f"\nProcessed content:\n{processed}")


if __name__ == "__main__":
    main()
