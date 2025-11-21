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
    """Manages context chunking for PR agent to avoid token limit errors"""
    
    def __init__(self, config_path: str = ".github/pr-agent-config.yml"):
        """Initialize chunker with configuration"""
        self.config = self._load_config(config_path)
        self._validate_config()
        
        # Load configuration with safe defaults
        self.max_tokens = self.config.get('agent', {}).get('context', {}).get('max_tokens', 32000)
        self.chunk_size = self.config.get('agent', {}).get('context', {}).get('chunk_size', 28000)
        self.overlap = self.config.get('agent', {}).get('context', {}).get('overlap_tokens', 2000)
        self.summarization_threshold = self.config.get('agent', {}).get('context', {}).get('summarization_threshold', 30000)
        
        # Priority mapping with default fallback
        priority_order = self.config.get('limits', {}).get('fallback', {}).get('priority_order', [
            'review_comments', 'test_failures', 'changed_files', 'ci_logs', 'full_diff'
        ])
        self.priority_map = {item: idx for idx, item in enumerate(priority_order)}
        
        # Initialize tokenizer if available
        self.tokenizer = None
        if TIKTOKEN_AVAILABLE:
            try:
                # Use cl100k_base encoding (GPT-4, GPT-3.5-turbo)
                self.tokenizer = tiktoken.get_encoding('cl100k_base')
            except Exception as e:
                print(f"Warning: Failed to initialize tiktoken encoder: {e}", file=sys.stderr)
                self.tokenizer = None
    
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from YAML file with robust error handling"""
        try:
            config_file = Path(config_path)
            if not config_file.exists():
                print(f"Warning: Config file not found: {config_path}", file=sys.stderr)
                print("Using default configuration values", file=sys.stderr)
                return self._get_default_config()
            
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                
            if config is None:
                print(f"Warning: Config file is empty: {config_path}", file=sys.stderr)
                return self._get_default_config()
                
            return config
            
        except yaml.YAMLError as e:
            print(f"Error: Invalid YAML in config file {config_path}: {e}", file=sys.stderr)
            print("Using default configuration values", file=sys.stderr)
            return self._get_default_config()
        except Exception as e:
            print(f"Error: Could not load config from {config_path}: {e}", file=sys.stderr)
            print("Using default configuration values", file=sys.stderr)
            return self._get_default_config()
    
    def _get_default_config(self) -> dict:
        """Return default configuration values"""
        return {
            'agent': {
                'context': {
                    'max_tokens': 32000,
                    'chunk_size': 28000,
                    'overlap_tokens': 2000,
                    'summarization_threshold': 30000,
                    'summarization': {
                        'max_summary_tokens': 2000
                    }
                }
            },
            'limits': {
                'fallback': {
                    'priority_order': [
                        'review_comments',
                        'test_failures',
                        'changed_files',
                        'ci_logs',
                        'full_diff'
                    ]
                }
            }
        }
    
    def _validate_config(self) -> None:
        """Validate configuration has required values"""
        required_keys = [
            ('agent', 'context', 'max_tokens'),
            ('agent', 'context', 'chunk_size'),
            ('agent', 'context', 'overlap_tokens'),
        ]
        
        for keys in required_keys:
            current = self.config
            for key in keys:
                if not isinstance(current, dict) or key not in current:
                    print(f"Warning: Missing config key: {'.'.join(keys)}", file=sys.stderr)
                    break
                current = current[key]
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text.
        Uses tiktoken if available for accurate counting, otherwise falls back to heuristic.
        
        Args:
            text: The text to estimate tokens for
            
        Returns:
            Estimated token count
        """
        if not text:
            return 0
            
        # Use tiktoken for accurate token counting if available
        if self.tokenizer is not None:
            try:
                return len(self.tokenizer.encode(text))
            except Exception as e:
                print(f"Warning: tiktoken encoding failed: {e}, using fallback", file=sys.stderr)
                # Fall through to heuristic method
        
        # Fallback: Heuristic estimation
        # Base estimation: ~4 characters per token for English text
        base_tokens = len(text) / 4
        
        # Adjust for code structure (more tokens for special characters)
        code_chars = len(re.findall(r'[{}()\[\];]', text))
        code_adjustment = code_chars * 0.5
        
        # Adjust for whitespace (tokens consume whitespace)
        whitespace_chars = len(re.findall(r'\s+', text))
        whitespace_adjustment = whitespace_chars * 0.25
        
        # Adjust for markdown/formatting
        formatting_chars = len(re.findall(r'[*_`#\-]', text))
        formatting_adjustment = formatting_chars * 0.3
        
        total_tokens = base_tokens + code_adjustment + whitespace_adjustment + formatting_adjustment
        
        # Add 10% safety margin for heuristic estimation
        return int(total_tokens * 1.1)
    
    def extract_content_sections(self, pr_data: Dict) -> Dict[str, str]:
        """Extract different sections from PR data"""
        sections = {}
        
        # Review comments (highest priority)
        if 'reviews' in pr_data:
            comments = []
            for review in pr_data.get('reviews', []):
                if review.get('state') == 'changes_requested':
                    comments.append(f"**{review.get('user', {}).get('login', 'Unknown')}:** {review.get('body', '')}")
            sections['review_comments'] = '\n\n'.join(comments)
        
        # Test failures
        if 'check_runs' in pr_data:
            failures = []
            for check in pr_data.get('check_runs', []):
                if check.get('conclusion') == 'failure':
                    failures.append(f"**{check.get('name')}:** {check.get('output', {}).get('summary', '')}")
            sections['test_failures'] = '\n\n'.join(failures)
        
        # Changed files
        if 'files' in pr_data:
            files_content = []
            for file in pr_data.get('files', []):
                files_content.append(f"**{file.get('filename')}** (+{file.get('additions', 0)} -{file.get('deletions', 0)})")
                if 'patch' in file and file.get('patch'):
                    files_content.append(f"```diff\n{file['patch']}\n```")
            sections['changed_files'] = '\n\n'.join(files_content)
        
        # CI logs (summarized)
        if 'ci_logs' in pr_data:
            sections['ci_logs'] = pr_data['ci_logs']
        
        # Full diff
        if 'diff' in pr_data:
            sections['full_diff'] = pr_data['diff']
        
        return sections
    
    def create_chunks(self, sections: Dict[str, str]) -> List[ContextChunk]:
        """Create prioritized chunks from sections"""
        chunks = []
        
        for section_type, content in sections.items():
            if not content:
                continue
            
            tokens = self.estimate_tokens(content)
            priority = self.priority_map.get(section_type, 999)
            
            # If section is small enough, keep as single chunk
            if tokens <= self.chunk_size:
                chunks.append(ContextChunk(
                    content=content,
                    tokens=tokens,
                    priority=priority,
                    chunk_type=section_type
                ))
            else:
                # Split large sections into multiple chunks
                sub_chunks = self._split_content(content, section_type, priority)
                chunks.extend(sub_chunks)
        
        # Sort by priority
        chunks.sort(key=lambda x: x.priority)
        return chunks
    
        for line in lines:
            line_tokens = self.estimate_tokens(line)

            # Handle ultra-long lines that exceed chunk_size to avoid data loss
            if line_tokens > self.chunk_size:
                # Flush current chunk if it has content before emitting oversized line
                if current_chunk:
                    chunk_content = '\n'.join(current_chunk)
                    chunks.append(ContextChunk(
                        content=chunk_content,
                        tokens=current_tokens,
                        priority=priority,
                        chunk_type=chunk_type
                    ))
                    current_chunk = []
                    current_tokens = 0

                # Emit the oversized line as its own chunk
                chunks.append(ContextChunk(
                    content=line,
                    tokens=line_tokens,
                    priority=priority,
                    chunk_type=chunk_type
                ))
                continue
    
            if current_tokens + line_tokens > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_content = '\n'.join(current_chunk)
                chunks.append(ContextChunk(
                    content=chunk_content,
                    tokens=current_tokens,
                    priority=priority,
                    chunk_type=chunk_type
                ))

                # Start new chunk with overlap
                overlap_lines = self._get_overlap_lines(current_chunk)
                current_chunk = overlap_lines + [line]
                current_tokens = sum(self.estimate_tokens(ln) for ln in current_chunk)
            else:
                current_chunk.append(line)
                current_tokens += line_tokens
    
    def _get_overlap_lines(self, lines: List[str]) -> List[str]:
        """Get overlap lines for continuity between chunks"""
        overlap_tokens = 0
        overlap_lines = []
        
        # Take last N lines that fit in overlap budget
        for line in reversed(lines):
            line_tokens = self.estimate_tokens(line)
            if overlap_tokens + line_tokens <= self.overlap:
                overlap_lines.insert(0, line)
                overlap_tokens += line_tokens
            else:
                break
        
        return overlap_lines
    
    def summarize_chunk(self, chunk: ContextChunk) -> str:
        """Create a summary of a chunk"""
        # Extract key information
        summary_parts = [f"[{chunk.chunk_type.upper()} SUMMARY]"]
        
        if chunk.chunk_type == "review_comments":
            # Extract action items from comments
            action_items = re.findall(r'(?:fix|add|update|remove|refactor|change)\s+[^\n.!?]{10,100}', 
                                     chunk.content, re.IGNORECASE)
            if action_items:
                summary_parts.append("Action items:")
                summary_parts.extend([f"- {item.strip()}" for item in action_items[:5]])
        
        elif chunk.chunk_type == "changed_files":
            # Extract file names and change counts
            files = re.findall(r'\*\*([^*]+)\*\*\s+\(\+(\d+)\s+-(\d+)\)', chunk.content)
            if files:
                summary_parts.append("Modified files:")
                summary_parts.extend([f"- {f[0]} (+{f[1]} -{f[2]})" for f in files[:10]])
        
        elif chunk.chunk_type == "test_failures":
            # Extract test names and error messages
            failures = re.findall(r'\*\*([^*]+)\*\*:', chunk.content)
            if failures:
                summary_parts.append("Failed tests:")
                summary_parts.extend([f"- {f}" for f in failures[:5]])
        
        summary = '\n'.join(summary_parts)
        
        # Ensure summary is within token limit
        summary_tokens = self.estimate_tokens(summary)
        max_summary = self.config.get('agent', {}).get('context', {}).get('summarization', {}).get('max_summary_tokens', 2000)
        
        if summary_tokens > max_summary:
            # Truncate summary
            target_chars = int(max_summary * 4)  # Rough conversion
            summary = summary[:target_chars] + "\n... (truncated)"
        
        return summary
    
    def process_context(self, pr_data: Dict) -> Tuple[str, bool]:
        """
        Process PR context and return optimized content.
        Returns: (processed_content, was_chunked)
        """
        # Extract sections
        sections = self.extract_content_sections(pr_data)
        
        # Calculate total tokens
        total_tokens = sum(self.estimate_tokens(content) for content in sections.values())
        
        # If under threshold, return as is
        if total_tokens <= self.summarization_threshold:
            full_content = '\n\n---\n\n'.join([
                f"## {section_type.replace('_', ' ').title()}\n\n{content}"
                for section_type, content in sections.items()
            ])
            return full_content, False
        
        # Create chunks
        chunks = self.create_chunks(sections)
        
        # Build context within token limit
        result_parts = []
        current_tokens = 0
        
        # Ensure chunks are processed strictly by priority (already sorted)
        included_indices = set()
        summaries = []
        omissions = []

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
                # Keep track of omissions with minimal metadata
                omissions.append(chunk.chunk_type.upper())

        # Final pass: add a compact omitted notice if anything left out
        if omissions:
            unique_omissions = []
            seen = set()
            for o in omissions:
                if o not in seen:
                    seen.add(o)
                    unique_omissions.append(o)
            omitted_note = f"[Omitted due to context limit: {', '.join(unique_omissions)}]"
            # Add only if it fits, otherwise drop silently
            if current_tokens + self.estimate_tokens(omitted_note) <= self.max_tokens:
                result_parts.append(omitted_note)
        processed_content = '\n\n---\n\n'.join(result_parts)
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
