#!/usr/bin/env python3
"""
Research Gatherer — OpenAI-Compatible API Server

Exposes the research-gatherer tool as a third-party search engine with
OpenAI-compatible chat completions endpoint, tool-calling integration,
citation-aware LLM synthesis, and direct REST endpoints.

Run:
  python ai_api.py                          # defaults: localhost:8000
  python ai_api.py --port 9000 --host 0.0.0.0
  uvicorn ai_api:app --reload --port 8000

Configuration:
  Copy .env.example → .env and fill in your LLM provider credentials.
  Supports any OpenAI-compatible endpoint: OpenAI, Ollama, vLLM, Groq,
  Together, DeepSeek, OpenRouter, LocalAI, etc.

Environment variables (all settable via .env):
  RESEARCH_API_KEY          API key for authentication (default: none = open)
  LLM_API_BASE              Base URL for OpenAI-compatible LLM (default: none)
  LLM_API_KEY               API key for LLM provider (default: none)
  LLM_MODEL                 Model name for LLM (default: gpt-4o)
  RESEARCH_OUTPUT_DIR       Default output directory (default: research_output)
  RESEARCH_PARSE_WORKERS    Parallel Jina parse workers (default: 4)
  RESEARCH_JINA_TIMEOUT     Per-URL Jina timeout in seconds (default: 30)
  RESEARCH_RATE_LIMIT       Delay between sequential Jina calls (default: 0.5)
"""

import os
import sys
import json
import time
import uuid
import asyncio
import argparse
import traceback
from datetime import datetime, timezone
from typing import (
    Any, AsyncGenerator, Callable, Dict, List, Literal, Optional, Union,
)
from contextlib import asynccontextmanager

# ---------------------------------------------------------------------------
# .env loading — must happen before any env-dependent imports
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    # Load .env from the same directory as this file
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if os.path.exists(_env_path):
        load_dotenv(_env_path)
except ImportError:
    pass  # python-dotenv not installed — rely on real env vars

from fastapi import FastAPI, HTTPException, Depends, Request, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
import httpx

# ---------------------------------------------------------------------------
# Path setup — replicate research_gatherer.py's sys.path logic
# ---------------------------------------------------------------------------
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
for sub in ('utils', 'engines'):
    p = os.path.join(_SCRIPT_DIR, sub)
    if p not in sys.path:
        sys.path.insert(0, p)

from helper import setup_logger  # noqa: E402
from research_gatherer import (  # noqa: E402
    ResearchGatherer,
    SearchEngineLoader,
    JinaParser,
    ACADEMIC_FILTER,
)
from image_gatherer import ImageGatherer  # noqa: E402

logger = setup_logger(name='ResearchAPI')

# ===================================================================
# Configuration (all read from environment / .env)
# ===================================================================

API_KEY = os.environ.get('RESEARCH_API_KEY', '')
LLM_API_BASE = os.environ.get('LLM_API_BASE', '').rstrip('/')
LLM_API_KEY = os.environ.get('LLM_API_KEY', '')
LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-4o')
DEFAULT_OUTPUT_DIR = os.environ.get('RESEARCH_OUTPUT_DIR', 'research_output')
PARSE_WORKERS = int(os.environ.get('RESEARCH_PARSE_WORKERS', '4'))
JINA_TIMEOUT = int(os.environ.get('RESEARCH_JINA_TIMEOUT', '30'))
RATE_LIMIT = float(os.environ.get('RESEARCH_RATE_LIMIT', '0.5'))

# ===================================================================
# OpenAI-Compatible Pydantic Schemas
# ===================================================================

# -- Tool definitions ------------------------------------------------

class FunctionParameters(BaseModel):
    type: Literal['object'] = 'object'
    properties: Dict[str, Any] = {}
    required: List[str] = []


class FunctionDef(BaseModel):
    name: str
    description: str
    parameters: FunctionParameters = FunctionParameters()


class ToolDef(BaseModel):
    type: Literal['function'] = 'function'
    function: FunctionDef


class ToolCall(BaseModel):
    id: str = Field(default_factory=lambda: f"call_{uuid.uuid4().hex[:24]}")
    type: Literal['function'] = 'function'
    function: FunctionDef


class ToolCallFunction(BaseModel):
    name: str
    arguments: str  # JSON string


class ToolCallMessage(BaseModel):
    id: str
    type: Literal['function'] = 'function'
    function: ToolCallFunction


# -- Chat message schemas --------------------------------------------

class ChatMessage(BaseModel):
    role: str
    content: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCallMessage]] = None
    tool_call_id: Optional[str] = None


class ChatCompletionRequest(BaseModel):
    model: str = 'research-assistant'
    messages: List[ChatMessage]
    tools: Optional[List[ToolDef]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = 'auto'
    stream: bool = False
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    top_p: Optional[float] = 1.0


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class Choice(BaseModel):
    index: int = 0
    message: ChatMessage
    finish_reason: Optional[str] = 'stop'


class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:12]}")
    object: str = 'chat.completion'
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str = 'research-assistant'
    choices: List[Choice]
    usage: Usage = Usage()


class StreamChoice(BaseModel):
    index: int = 0
    delta: Dict[str, Any]
    finish_reason: Optional[str] = None


class ChatCompletionChunk(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:12]}")
    object: str = 'chat.completion.chunk'
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str = 'research-assistant'
    choices: List[StreamChoice]


# -- Model schema ----------------------------------------------------

class ModelObject(BaseModel):
    id: str
    object: str = 'model'
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = 'research-gatherer'


class ModelListResponse(BaseModel):
    object: str = 'list'
    data: List[ModelObject]


# -- Direct REST schemas ---------------------------------------------

class SearchRequest(BaseModel):
    query: str
    engines: Optional[List[str]] = None


class SearchResponse(BaseModel):
    query: str
    links: List[str]
    count: int
    elapsed_seconds: float


class ParseRequest(BaseModel):
    urls: List[str]
    output_dir: Optional[str] = None


class ParseResponseItem(BaseModel):
    url: str
    title: Optional[str] = None
    markdown_length: int
    saved: bool
    filepath: Optional[str] = None
    error: Optional[str] = None


class ParseResponse(BaseModel):
    results: List[ParseResponseItem]
    success_count: int
    fail_count: int
    elapsed_seconds: float


class ImageRequest(BaseModel):
    keywords: List[str]
    output_dir: Optional[str] = None
    min_size: int = 300


class ImageResponse(BaseModel):
    keywords: List[str]
    output_dir: str
    elapsed_seconds: float


class DeepResearchRequest(BaseModel):
    query: str
    output_dir: Optional[str] = None
    filter_domains: Optional[str] = None
    academic: bool = False
    max_parse: int = 0
    max_runtime: int = 0


class DeepResearchResponse(BaseModel):
    query: str
    links_collected: int
    documents_parsed: int
    summary_path: Optional[str]
    elapsed_seconds: float


# --- Citation-aware research request/response ----------------------

class ResearchSynthesisRequest(BaseModel):
    """Search + LLM synthesis with citations in one call."""
    query: str
    max_results: int = Field(default=5, ge=1, le=20, description='Max search results to synthesize')
    parse_top: int = Field(default=3, ge=0, le=10, description='Parse top N results for deeper context')
    academic_only: bool = False
    temperature: float = 0.3
    max_tokens: int = 4096


class Citation(BaseModel):
    index: int
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None


class ResearchSynthesisResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
    search_count: int
    parsed_count: int
    model_used: str
    elapsed_seconds: float


# ===================================================================
# Registered Tools — exposed to LLM via /v1/chat/completions
# ===================================================================

RESEARCH_TOOLS: List[ToolDef] = [
    ToolDef(function=FunctionDef(
        name='search',
        description=(
            'Search the web using multiple search engines (Google, Bing, Yahoo, '
            'DuckDuckGo, etc.). Returns a deduplicated list of URLs relevant to '
            'the query. Use this to find sources, articles, and references.'
        ),
        parameters=FunctionParameters(
            properties={
                'query': {
                    'type': 'string',
                    'description': 'The search query string. Supports dork syntax like site:example.com "exact phrase" filetype:pdf',
                },
            },
            required=['query'],
        ),
    )),
    ToolDef(function=FunctionDef(
        name='parse_url',
        description=(
            'Parse a URL into clean markdown text using Jina AI Reader. '
            'Returns the extracted content as readable text. Useful for '
            'getting the full content of a search result.'
        ),
        parameters=FunctionParameters(
            properties={
                'url': {
                    'type': 'string',
                    'description': 'The URL to parse into markdown',
                },
            },
            required=['url'],
        ),
    )),
    ToolDef(function=FunctionDef(
        name='parse_urls',
        description=(
            'Parse multiple URLs into clean markdown text in parallel. '
            'Returns a list of parsed contents. More efficient than calling '
            'parse_url multiple times.'
        ),
        parameters=FunctionParameters(
            properties={
                'urls': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'List of URLs to parse',
                },
                'max_items': {
                    'type': 'integer',
                    'description': 'Maximum number of URLs to parse (default: 10)',
                },
            },
            required=['urls'],
        ),
    )),
    ToolDef(function=FunctionDef(
        name='gather_images',
        description=(
            'Search for and download presentation-quality images related to '
            'the given keywords. Images are saved locally and metadata is returned.'
        ),
        parameters=FunctionParameters(
            properties={
                'keywords': {
                    'type': 'array',
                    'items': {'type': 'string'},
                    'description': 'Keywords to search for images',
                },
                'min_size': {
                    'type': 'integer',
                    'description': 'Minimum image dimension in pixels (default: 300)',
                },
            },
            required=['keywords'],
        ),
    )),
    ToolDef(function=FunctionDef(
        name='deep_research',
        description=(
            'Perform deep research on a topic: searches multiple engines, '
            'parses top results via Jina, and generates a structured research '
            'summary. Best for comprehensive research tasks.'
        ),
        parameters=FunctionParameters(
            properties={
                'query': {
                    'type': 'string',
                    'description': 'Research topic or query',
                },
                'academic_only': {
                    'type': 'boolean',
                    'description': 'If true, only parse results from academic/peer-reviewed domains',
                },
                'max_parse': {
                    'type': 'integer',
                    'description': 'Maximum number of URLs to parse (0 = unlimited)',
                },
            },
            required=['query'],
        ),
    )),
]


# ===================================================================
# Tool Execution
# ===================================================================

async def _run_in_thread(func: Callable, *args, **kwargs) -> Any:
    """Run a synchronous function in a thread pool to avoid blocking."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: func(*args, **kwargs))


def _execute_search(query: str) -> dict:
    """Execute search across all engines."""
    t0 = time.monotonic()
    loader = SearchEngineLoader(debug_mode=False)
    loader.load_engines()
    links = loader.search_all(query)
    elapsed = time.monotonic() - t0
    return {
        'query': query,
        'links': links,
        'count': len(links),
        'elapsed_seconds': round(elapsed, 2),
    }


def _execute_parse_url(url: str) -> dict:
    """Parse a single URL via Jina."""
    parser = JinaParser(rate_limit_delay=RATE_LIMIT, request_timeout=JINA_TIMEOUT)
    t0 = time.monotonic()
    md = parser.parse_url(url)
    elapsed = time.monotonic() - t0
    if md:
        title = parser.extract_title(md)
        return {
            'url': url,
            'title': title,
            'content': md[:8000],  # Truncate for LLM context
            'markdown_length': len(md),
            'elapsed_seconds': round(elapsed, 2),
        }
    return {'url': url, 'error': 'Failed to parse', 'elapsed_seconds': round(elapsed, 2)}


def _execute_parse_urls(urls: list, max_items: int = 10) -> dict:
    """Parse multiple URLs via Jina (sequential, capped)."""
    urls = urls[:max_items]
    t0 = time.monotonic()
    parser = JinaParser(rate_limit_delay=RATE_LIMIT, request_timeout=JINA_TIMEOUT)
    results = []
    success = 0
    for url in urls:
        md = parser.parse_url(url)
        if md:
            title = parser.extract_title(md)
            results.append({
                'url': url, 'title': title,
                'content': md[:8000],
                'markdown_length': len(md),
            })
            success += 1
        else:
            results.append({'url': url, 'error': 'Failed to parse'})
    elapsed = time.monotonic() - t0
    return {
        'results': results, 'success_count': success,
        'fail_count': len(urls) - success,
        'elapsed_seconds': round(elapsed, 2),
    }


def _execute_gather_images(keywords: list, min_size: int = 300) -> dict:
    """Gather images for given keywords."""
    t0 = time.monotonic()
    output_dir = os.path.join(DEFAULT_OUTPUT_DIR, 'images')
    gatherer = ImageGatherer(output_dir=output_dir, min_image_size=min_size)
    gatherer.gather(keywords)
    elapsed = time.monotonic() - t0
    image_count = 0
    if os.path.exists(output_dir):
        for _, _, files in os.walk(output_dir):
            image_count += sum(
                1 for f in files
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp'))
            )
    return {
        'keywords': keywords, 'images_found': image_count,
        'output_dir': output_dir,
        'elapsed_seconds': round(elapsed, 2),
    }


def _execute_deep_research(query: str, academic_only: bool = False, max_parse: int = 0) -> dict:
    """Full pipeline: search → parse → summary."""
    t0 = time.monotonic()
    output_dir = os.path.join(DEFAULT_OUTPUT_DIR, f'research_{uuid.uuid4().hex[:8]}')
    gatherer = ResearchGatherer(
        output_dir=output_dir, debug_mode=False,
        parse_workers=PARSE_WORKERS, rate_limit_delay=RATE_LIMIT,
        max_parse=max_parse,
    )
    # Phase 1: search
    gatherer.search_and_collect([query])
    links_count = len(gatherer.link_manager.links)
    # Phase 2: parse
    if academic_only:
        gatherer.parse_collected_links(keyword_filter=ACADEMIC_FILTER)
    else:
        gatherer.parse_collected_links()
    # Phase 3: summary
    gatherer.generate_summary()
    # Count parsed docs
    parsed_dir = os.path.join(output_dir, 'parsed_content')
    doc_count = 0
    if os.path.exists(parsed_dir):
        for _, _, files in os.walk(parsed_dir):
            doc_count += sum(1 for f in files if f.endswith('.md'))
    elapsed = time.monotonic() - t0
    summary_path = os.path.join(output_dir, 'RESEARCH_SUMMARY.md')
    return {
        'query': query, 'links_collected': links_count,
        'documents_parsed': doc_count, 'output_dir': output_dir,
        'summary_path': summary_path if os.path.exists(summary_path) else None,
        'elapsed_seconds': round(elapsed, 2),
    }


TOOL_EXECUTORS: Dict[str, Callable] = {
    'search': lambda args: _execute_search(args['query']),
    'parse_url': lambda args: _execute_parse_url(args['url']),
    'parse_urls': lambda args: _execute_parse_urls(
        args['urls'], args.get('max_items', 10)
    ),
    'gather_images': lambda args: _execute_gather_images(
        args['keywords'], args.get('min_size', 300)
    ),
    'deep_research': lambda args: _execute_deep_research(
        args['query'], args.get('academic_only', False), args.get('max_parse', 0),
    ),
}


# ===================================================================
# Citation-Aware Research Synthesis Engine
# ===================================================================

CITATION_SYSTEM_PROMPT = """\
You are ResearchGPT, an expert research assistant. You are given a user \
question and a set of search results (URLs with optional parsed content). \
Your task is to synthesize a comprehensive, accurate answer using the \
provided sources.

## CRITICAL: Citation Rules
1. Every factual claim MUST be supported by a citation from the sources.
2. Use inline citation markers: [1], [2], [3], etc. matching the source numbers.
3. List all sources at the end under "## Sources".
4. If the sources are insufficient, say so explicitly.
5. Never fabricate information not present in the provided sources.
6. When multiple sources agree, cite all of them.

## Response Format
Provide a clear, well-structured answer with inline citations. End with:

## Sources
[1] Title — URL
[2] Title — URL
...

If no LLM backend is configured, provide a raw synthesis of the search results \
with inline citations based solely on the provided context.
"""


def _build_citation_context(search_result: dict, parsed_results: list) -> str:
    """Build a context block from search + parse results for the LLM."""
    parts = []
    links = search_result.get('links', [])

    # Numbered source list
    source_map: Dict[int, str] = {}
    for idx, url in enumerate(links, 1):
        source_map[idx] = url
        parts.append(f"[{idx}] {url}")

    # Parse result content
    if parsed_results:
        parts.append("")
        parts.append("=== PARSED CONTENT ===")
        for pr in parsed_results:
            url = pr.get('url', '')
            title = pr.get('title', 'Untitled')
            content = pr.get('content', pr.get('error', 'No content'))
            # Find source number
            src_num = next((k for k, v in source_map.items() if v == url), '?')
            parts.append(f"\n--- Source [{src_num}] {title} ---")
            parts.append(f"URL: {url}")
            # Truncate content for context window
            parts.append(content[:6000])
            parts.append("---")

    return "\n".join(parts)


async def _synthesis_with_llm(
    query: str, context: str, temperature: float = 0.3, max_tokens: int = 4096,
) -> str:
    """Send search context to LLM for citation-aware synthesis."""
    messages = [
        {'role': 'system', 'content': CITATION_SYSTEM_PROMPT},
        {'role': 'user', 'content': f"User question: {query}\n\nSources and context:\n{context}"},
    ]
    resp_data = await llm.chat(
        messages=messages, tools=None, tool_choice='none',
        temperature=temperature, max_tokens=max_tokens,
    )
    choice = resp_data.get('choices', [{}])[0]
    msg = choice.get('message', {})
    return msg.get('content', '')


def _synthesis_without_llm(query: str, search_result: dict, parsed_results: list) -> str:
    """Fallback: synthesize answer directly from search results (no LLM)."""
    links = search_result.get('links', [])
    count = search_result.get('count', 0)

    parts = [
        f"**Search results for:** {query}",
        f"Found **{count}** results across multiple search engines.\n",
        "## Top Sources\n",
    ]

    for idx, url in enumerate(links[:10], 1):
        # Try to find parsed title
        parsed = next((p for p in parsed_results if p.get('url') == url), None)
        title = parsed.get('title') if parsed else None
        snippet = None
        if parsed and parsed.get('content'):
            # Extract first meaningful paragraph
            lines = [
                l.strip() for l in parsed['content'].split('\n')
                if l.strip() and not l.startswith('#') and not l.startswith('---')
            ]
            snippet = lines[0][:300] if lines else None

        display = title or url
        parts.append(f"[{idx}] **{display}**")
        parts.append(f"    {url}")
        if snippet:
            parts.append(f"    > {snippet}")
        parts.append("")

    if parsed_results:
        parts.append("\n## Parsed Content Summary\n")
        for pr in parsed_results:
            if pr.get('error'):
                continue
            title = pr.get('title', 'Untitled')
            content = pr.get('content', '')
            # Extract first 500 chars of body
            body_lines = [
                l.strip() for l in content.split('\n')
                if l.strip() and not l.startswith('#') and not l.startswith('---')
                and not l.startswith('Title:') and not l.startswith('URL:')
            ]
            body_snippet = ' '.join(body_lines)[:500]
            parts.append(f"**{title}**")
            if body_snippet:
                parts.append(f"> {body_snippet}...")
            parts.append("")

    parts.append("\n*Note: No LLM backend configured. This is a raw synthesis of search results. "
                 "Set LLM_API_BASE and LLM_API_KEY in .env for AI-powered answers with citations.*")
    return "\n".join(parts)


# ===================================================================
# Conversation Memory (in-memory, per-session)
# ===================================================================

class ConversationStore:
    """In-memory store for conversation histories, keyed by session ID."""

    def __init__(self, max_sessions: int = 1000):
        self._store: Dict[str, List[ChatMessage]] = {}
        self._meta: Dict[str, Dict[str, Any]] = {}
        self._max_sessions = max_sessions

    def get(self, session_id: str) -> List[ChatMessage]:
        return self._store.get(session_id, [])

    def append(self, session_id: str, message: ChatMessage):
        if session_id not in self._store:
            if len(self._store) >= self._max_sessions:
                # Evict oldest session
                oldest = next(iter(self._store))
                del self._store[oldest]
                del self._meta[oldest]
            self._store[session_id] = []
            self._meta[session_id] = {'created': time.time()}
        self._store[session_id].append(message)

    def delete(self, session_id: str):
        self._store.pop(session_id, None)
        self._meta.pop(session_id, None)

    def list_sessions(self) -> List[str]:
        return list(self._store.keys())


conversations = ConversationStore()

# ===================================================================
# LLM Client — supports any OpenAI-compatible endpoint
# ===================================================================

class LLMClient:
    """Async wrapper around any OpenAI-compatible chat completions API.

    Configure via .env:
      LLM_API_BASE  = https://api.openai.com/v1
      LLM_API_KEY   = sk-...
      LLM_MODEL     = gpt-4o

    Works with: OpenAI, Ollama, vLLM, Groq, Together, DeepSeek,
    OpenRouter, LocalAI, Anyscale, Moonshot, or any compatible endpoint.
    """

    def __init__(self, base_url: str = '', api_key: str = '', model: str = ''):
        self.base_url = base_url or LLM_API_BASE
        self.api_key = api_key or LLM_API_KEY
        self.model = model or LLM_MODEL

    @property
    def available(self) -> bool:
        return bool(self.base_url and self.api_key)

    @property
    def provider_info(self) -> dict:
        """Return info about the configured provider."""
        if not self.available:
            return {'configured': False}
        # Detect provider from base URL
        provider = 'custom'
        base_lower = self.base_url.lower()
        if 'openai.com' in base_lower:
            provider = 'openai'
        elif 'ollama' in base_lower or '11434' in base_lower:
            provider = 'ollama'
        elif 'groq' in base_lower:
            provider = 'groq'
        elif 'together' in base_lower:
            provider = 'together'
        elif 'deepseek' in base_lower:
            provider = 'deepseek'
        elif 'openrouter' in base_lower:
            provider = 'openrouter'
        elif 'localai' in base_lower or '8080' in base_lower:
            provider = 'localai'
        elif 'vllm' in base_lower or '8001' in base_lower:
            provider = 'vllm'
        return {
            'configured': True,
            'provider': provider,
            'base_url': self.base_url,
            'model': self.model,
        }

    async def chat(
        self,
        messages: List[dict],
        tools: Optional[List[dict]] = None,
        tool_choice: Union[str, dict] = 'auto',
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> dict:
        """Non-streaming chat completion. Returns raw API response dict."""
        if not self.available:
            raise HTTPException(
                500,
                'LLM backend not configured. Set LLM_API_BASE and LLM_API_KEY '
                'in your .env file or environment variables.'
            )
        body: Dict[str, Any] = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
        }
        if tools:
            body['tools'] = tools
            body['tool_choice'] = tool_choice

        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f'{self.base_url}/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json=body,
            )
            resp.raise_for_status()
            return resp.json()

    async def chat_stream(
        self,
        messages: List[dict],
        tools: Optional[List[dict]] = None,
        tool_choice: Union[str, dict] = 'auto',
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> AsyncGenerator[str, None]:
        """Streaming chat completion. Yields SSE data lines."""
        if not self.available:
            raise HTTPException(500, 'LLM backend not configured')
        body: Dict[str, Any] = {
            'model': self.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'stream': True,
        }
        if tools:
            body['tools'] = tools
            body['tool_choice'] = tool_choice

        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream(
                'POST',
                f'{self.base_url}/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json=body,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith('data: '):
                        yield line + '\n\n'
                    elif line.strip() == '':
                        continue


llm = LLMClient()

# ===================================================================
# System Prompt for tool-calling mode
# ===================================================================

SYSTEM_PROMPT = """\
You are ResearchGPT, an expert AI research assistant powered by a \
multi-engine search system with 13+ search engines (Google, Bing, Yahoo, \
DuckDuckGo, Yandex, Naver, Mojeek, etc.).

## Available Tools
- **search**: Search the web across multiple engines. Returns deduplicated URLs.
- **parse_url**: Extract clean markdown from a single URL via Jina AI Reader.
- **parse_urls**: Parse multiple URLs in one call (more efficient).
- **gather_images**: Find and download presentation-quality images.
- **deep_research**: Full pipeline: search → parse → summarize with structured output.

## Guidelines
1. When asked to research a topic, ALWAYS start with `search` to find sources.
2. For important results, use `parse_url` to get full content before answering.
3. Use `deep_research` for comprehensive tasks needing a full summary.
4. **ALWAYS cite your sources** with URLs when providing information.
5. Use inline markers [1], [2], etc. and list sources at the end.
6. Be concise but thorough. Prioritize accuracy over speed.
7. For academic research, use `deep_research` with `academic_only: true`.
8. If the user asks about current events, search first — your training data has a cutoff.
"""

# ===================================================================
# Authentication
# ===================================================================

async def verify_api_key(request: Request):
    """Dependency: verify API key if RESEARCH_API_KEY is set."""
    if not API_KEY:
        return  # No key configured — open access
    key = request.headers.get('X-API-Key', '')
    if key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or missing API key. Pass X-API-Key header.',
        )

# ===================================================================
# FastAPI Application
# ===================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('=' * 60)
    logger.info('Research Gatherer API starting up...')
    logger.info(f'LLM provider: {llm.provider_info}')
    logger.info(f'Auth: {"enabled" if API_KEY else "disabled (open access)"}')
    logger.info(f'Parse workers: {PARSE_WORKERS}, Jina timeout: {JINA_TIMEOUT}s')
    logger.info('=' * 60)
    yield
    logger.info('Research Gatherer API shutting down.')


app = FastAPI(
    title='Research Gatherer API',
    description=(
        'OpenAI-compatible API for multi-engine web research with LLM '
        'tool-calling integration and citation-aware synthesis.\n\n'
        '## Endpoints\n'
        '- `POST /v1/chat/completions` — OpenAI-compatible chat with tool calling\n'
        '- `GET  /v1/models` — List available models\n'
        '- `POST /v1/research` — Search + LLM synthesis with citations\n'
        '- `GET  /v1/search` — Direct search endpoint\n'
        '- `POST /v1/parse` — Direct URL parsing\n'
        '- `POST /v1/images` — Direct image gathering\n'
        '- `POST /v1/deep-research` — Full research pipeline\n'
        '- `GET  /v1/sessions` — Manage conversation sessions\n'
        '- `GET  /health` — Health check\n'
        '- `GET  /docs` — Interactive API documentation'
    ),
    version='2.0.0',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)


# ===================================================================
# Health & Models
# ===================================================================

@app.get('/health')
async def health_check():
    return {
        'status': 'ok',
        'version': '2.0.0',
        'llm': llm.provider_info,
        'engines_loaded': True,
        'parse_workers': PARSE_WORKERS,
        'auth_enabled': bool(API_KEY),
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }


@app.get('/v1/models', response_model=ModelListResponse)
async def list_models():
    models = [
        ModelObject(id='research-assistant', owned_by='research-gatherer'),
    ]
    if llm.available:
        models.append(
            ModelObject(id=llm.model, owned_by=llm.provider_info.get('provider', 'llm'))
        )
    return ModelListResponse(data=models)


# ===================================================================
# Citation-Aware Research Synthesis — /v1/research
# ===================================================================

@app.post('/v1/research', response_model=ResearchSynthesisResponse)
async def research_synthesis(
    body: ResearchSynthesisRequest,
    _: None = Depends(verify_api_key),
):
    """Search the web, optionally parse top results, then synthesize an
    answer with proper citations using the configured LLM.

    If no LLM is configured, returns a raw synthesis of search results.
    """
    t0 = time.monotonic()

    # Step 1: Search
    search_result = await _run_in_thread(_execute_search, body.query)
    links = search_result.get('links', [])

    # Step 2: Parse top results for deeper context
    parsed_results = []
    if body.parse_top > 0 and links:
        urls_to_parse = links[:body.parse_top]
        if body.academic_only:
            # Filter to academic domains
            academic_domains = [d.strip() for d in ACADEMIC_FILTER.split(',')]
