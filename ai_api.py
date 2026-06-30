#!/usr/bin/env python3
"""
Research Gatherer — OpenAI-Compatible API Server

Exposes the research-gatherer tool as a third-party search engine with
OpenAI-compatible chat completions endpoint, tool-calling integration,
and direct REST endpoints.

Run:
  python ai_api.py                          # defaults: localhost:8000
  python ai_api.py --port 9000 --host 0.0.0.0
  uvicorn ai_api:app --reload --port 8000

Environment variables:
  RESEARCH_API_KEY          API key for authentication (default: none = open)
  LLM_API_BASE              Base URL for OpenAI-compatible LLM (default: none)
  LLM_API_KEY               API key for LLM provider (default: none)
  LLM_MODEL                 Model name for LLM (default: gpt-4o)
  RESEARCH_OUTPUT_DIR       Default output directory (default: research_output)
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
from enum import Enum
from typing import (
    Any, AsyncGenerator, Callable, Dict, List, Literal, Optional, Set, Union,
)
from contextlib import asynccontextmanager

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
# Configuration
# ===================================================================

API_KEY = os.environ.get('RESEARCH_API_KEY', '')
LLM_API_BASE = os.environ.get('LLM_API_BASE', '').rstrip('/')
API_KEYS = [
    k.strip() for k in os.environ.get('LLM_API_KEY', '').split(',')
    if k.strip()
]
# Legacy single-key fallback
if not API_KEYS:
    single = os.environ.get('LLM_API_KEY', '')
    if single.strip():
        API_KEYS = [single.strip()]
LLM_MODEL = os.environ.get('LLM_MODEL', 'gpt-4o')
DEFAULT_OUTPUT_DIR = os.environ.get('RESEARCH_OUTPUT_DIR', 'research_output')

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
    include_content: Optional[bool] = False


class ParseResponseItem(BaseModel):
    url: str
    title: Optional[str] = None
    markdown_length: int
    saved: bool
    filepath: Optional[str] = None
    error: Optional[str] = None
    content: Optional[str] = None


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
    parser = JinaParser(rate_limit_delay=0.5, request_timeout=30)
    t0 = time.monotonic()
    md = parser.parse_url(url)
    elapsed = time.monotonic() - t0
    if md:
        title = parser.extract_title(md)
        return {
            'url': url,
            'title': title,
            'content': md,
            'markdown_length': len(md),
            'elapsed_seconds': round(elapsed, 2),
        }
    return {'url': url, 'error': 'Failed to parse', 'elapsed_seconds': round(elapsed, 2)}


def _execute_parse_urls(urls: list, max_items: int = 10) -> dict:
    """Parse multiple URLs via Jina (sequential, capped)."""
    urls = urls[:max_items]
    t0 = time.monotonic()
    parser = JinaParser(rate_limit_delay=0.5, request_timeout=30)
    results = []
    success = 0
    for url in urls:
        md = parser.parse_url(url)
        if md:
            title = parser.extract_title(md)
            results.append({
                'url': url, 'title': title,
                'content': md, 'markdown_length': len(md),
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
    # Check what was downloaded
    image_count = 0
    if os.path.exists(output_dir):
        for _, _, files in os.walk(output_dir):
            image_count += sum(1 for f in files if f.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')))
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
        parse_workers=4, rate_limit_delay=0.5,
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
# LLM Client
# ===================================================================

class LLMClient:
    """Async wrapper for any OpenAI-compatible chat completions API.

    Supports multiple API keys for rotation (set via comma-separated
    LLM_API_KEY env var). Automatically detects the provider from the
    base URL and applies the correct auth header.

    Configure via .env:
      LLM_API_BASE  = https://api.openai.com/v1
      LLM_API_KEY   = sk-... (or key1,key2,key3 for rotation)
      LLM_MODEL     = gpt-4o
    """

    def __init__(self, base_url: str = '', api_keys: Optional[List[str]] = None, model: str = ''):
        self.base_url = base_url or LLM_API_BASE
        self._keys = api_keys if api_keys is not None else list(API_KEYS)
        self._key_index = 0
        self.model = model or LLM_MODEL
        self._provider = self._detect_provider()

    # -- provider detection ------------------------------------------

    @staticmethod
    def _detect_provider() -> str:
        base_lower = LLM_API_BASE.lower()
        if 'openai.com' in base_lower:
            return 'openai'
        if 'ollama' in base_lower or '11434' in base_lower:
            return 'ollama'
        if 'groq' in base_lower:
            return 'groq'
        if 'together' in base_lower:
            return 'together'
        if 'deepseek' in base_lower:
            return 'deepseek'
        if 'openrouter' in base_lower:
            return 'openrouter'
        if 'anthropic' in base_lower:
            return 'anthropic'
        if 'localai' in base_lower or '8080' in base_lower:
            return 'localai'
        if 'vllm' in base_lower or '8001' in base_lower:
            return 'vllm'
        return 'custom'

    # -- key management ----------------------------------------------

    @property
    def available(self) -> bool:
        return bool(self.base_url and self._keys)

    @property
    def current_key(self) -> str:
        """Return the current API key (rotates on failure)."""
        if not self._keys:
            return ''
        return self._keys[self._key_index % len(self._keys)]

    def _rotate_key(self) -> str:
        """Rotate to the next API key and return it."""
        if len(self._keys) > 1:
            self._key_index = (self._key_index + 1) % len(self._keys)
            logger.info(f"Rotated to API key index {self._key_index}")
        return self.current_key

    def _auth_headers(self) -> Dict[str, str]:
        """Build authorization headers based on provider."""
        key = self.current_key
        # Anthropic uses x-api-key instead of Bearer
        if self._provider == 'anthropic':
            return {
                'x-api-key': key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01',
            }
        return {
            'Authorization': f'Bearer {key}',
            'Content-Type': 'application/json',
        }

    @property
    def provider_info(self) -> dict:
        if not self.available:
            return {'configured': False}
        return {
            'configured': True,
            'provider': self._provider,
            'base_url': self.base_url,
            'model': self.model,
            'keys_count': len(self._keys),
        }

    # -- core API methods --------------------------------------------

    async def _request_with_retry(
        self, method: str, url: str, max_retries: int = 3, **kwargs,
    ) -> httpx.Response:
        """Make an HTTP request with automatic key rotation on 401/429."""
        last_error = None
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(timeout=120) as client:
                    resp = await client.request(
                        method, url,
                        headers=self._auth_headers(),
                        **kwargs,
                    )
                    # Rotate key on auth/rate-limit errors
                    if resp.status_code in (401, 403, 429) and len(self._keys) > 1:
                        logger.warning(
                            f"Got {resp.status_code} with key index {self._key_index}, "
                            f"rotating... (attempt {attempt + 1}/{max_retries})"
                        )
                        self._rotate_key()
                        continue
                    resp.raise_for_status()
                    return resp
            except httpx.HTTPStatusError as e:
                if e.response.status_code in (401, 403, 429) and len(self._keys) > 1:
                    self._rotate_key()
                    last_error = e
                    continue
                raise
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    import asyncio as _aio
                    await _aio.sleep(1.0 * (attempt + 1))
                    continue
                raise
        # All retries exhausted
        if last_error:
            raise last_error
        raise HTTPException(502, 'LLM API: all retries exhausted')

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

        resp = await self._request_with_retry(
            'POST', f'{self.base_url}/chat/completions', json=body,
        )
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
                headers=self._auth_headers(),
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
# Auto-Research Engine
# ===================================================================

def _extract_search_query(user_message: str) -> str:
    """Extract the core research query from a user message."""
    prefixes = [
        'search for', 'search about', 'search ', 'find ', 'find me ',
        'research ', 'look up ', 'look for ', 'tell me about ',
        'what is ', 'what are ', 'explain ', 'how does ', 'how do ',
        'why does ', 'why do ', 'can you research ', 'can you find ',
    ]
    q = user_message.lower()
    for prefix in sorted(prefixes, key=len, reverse=True):
        if q.startswith(prefix):
            return user_message[len(prefix):].strip().rstrip('?!.')
    return user_message.strip().rstrip('?.')


async def _auto_research(query: str, parse_top: int = 3) -> str:
    """Search → parse → synthesize pipeline. Returns citation-aware answer."""
    t0 = time.monotonic()
    logger.info(f"[AutoResearch] Searching: {repr(query)}")
    search_result = await _run_in_thread(_execute_search, query)
    links = search_result.get('links', [])
    count = search_result.get('count', 0)
    logger.info(f"[AutoResearch] Found {count} results in {search_result.get('elapsed_seconds', 0)}s")

    parsed_results = []
    if parse_top > 0 and links:
        urls_to_parse = links[:parse_top]
        logger.info(f"[AutoResearch] Parsing {len(urls_to_parse)} top results...")
        parse_result = await _run_in_thread(
            _execute_parse_urls, urls_to_parse, len(urls_to_parse),
        )
        parsed_results = parse_result.get('results', [])
        logger.info(
            f"[AutoResearch] Parsed {parse_result.get('success_count', 0)}/"
            f"{len(urls_to_parse)} in {parse_result.get('elapsed_seconds', 0)}s"
        )

    if llm.available:
        context = _build_research_context(search_result, parsed_results)
        messages = [
            {'role': 'system', 'content': SYSTEM_PROMPT},
            {'role': 'user', 'content': (
                f"User question: {query}\n\n"
                f"Research context ({count} search results, {len(parsed_results)} parsed):\n"
                f"{context}"
            )},
        ]
        logger.info(f"[AutoResearch] Sending to LLM ({llm.model}) for synthesis...")
        resp_data = await llm.chat(messages=messages, temperature=0.3, max_tokens=4096)
        answer = resp_data.get('choices', [{}])[0].get('message', {}).get('content', '')
        elapsed = time.monotonic() - t0
        logger.info(f"[AutoResearch] LLM synthesis complete in {round(elapsed, 1)}s")
        return answer
    else:
        return _raw_synthesis(query, search_result, parsed_results)


async def _auto_research_stream(query: str, parse_top: int = 3) -> AsyncGenerator[str, None]:
    """Streaming variant of auto-research."""
    stream_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"
    yield f"data: {json.dumps({'id': stream_id, 'object': 'chat.completion.chunk', 'model': 'research-assistant', 'choices': [{'delta': {'role': 'assistant'}, 'index': 0}]})}\n\n"
    try:
        answer = await _auto_research(query, parse_top=parse_top)
        for i in range(0, len(answer), 20):
            chunk = answer[i:i + 20]
            yield f"data: {json.dumps({'id': stream_id, 'object': 'chat.completion.chunk', 'choices': [{'delta': {'content': chunk}, 'index': 0}]})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'id': stream_id, 'object': 'chat.completion.chunk', 'choices': [{'delta': {'content': f'Research error: {str(e)}'}, 'index': 0}]})}\n\n"
    yield f"data: {json.dumps({'id': stream_id, 'object': 'chat.completion.chunk', 'choices': [{'delta': {}, 'finish_reason': 'stop', 'index': 0}]})}\n\n"
    yield "data: [DONE]\n\n"


def _build_research_context(search_result: dict, parsed_results: list) -> str:
    """Build context block from search + parse results for the LLM."""
    parts = []
    links = search_result.get('links', [])
    source_map = {}
    for idx, url in enumerate(links, 1):
        source_map[idx] = url
        parts.append(f"[{idx}] {url}")
    if parsed_results:
        parts.append("\n=== PARSED CONTENT ===")
        for pr in parsed_results:
            if pr.get('error'):
                continue
            url = pr.get('url', '')
            title = pr.get('title', 'Untitled')
            content = pr.get('content', '')
            src_num = next((k for k, v in source_map.items() if v == url), '?')
            parts.append(f"\n--- Source [{src_num}] {title} ---")
            parts.append(f"URL: {url}")
            parts.append(content[:6000])
            parts.append("---")
    return "\n".join(parts)


def _raw_synthesis(query: str, search_result: dict, parsed_results: list) -> str:
    """Fallback: synthesize answer directly from search results (no LLM)."""
    links = search_result.get('links', [])
    count = search_result.get('count', 0)
    parts = [
        f"**Research results for:** {query}\n",
        f"Found **{count}** results across multiple search engines.\n",
        "## Top Sources\n",
    ]
    for idx, url in enumerate(links[:10], 1):
        parsed = next((p for p in parsed_results if p.get('url') == url), None)
        title = parsed.get('title') if parsed else None
        snippet = None
        if parsed and parsed.get('content'):
            lines = [l.strip() for l in parsed['content'].split('\n')
                     if l.strip() and not l.startswith('#') and not l.startswith('---')]
            snippet = lines[0][:300] if lines else None
        parts.append(f"[{idx}] **{title or url}**")
        parts.append(f"    {url}")
        if snippet:
            parts.append(f"    > {snippet}")
        parts.append("")
    parts.append("\n*Note: No LLM configured. Set LLM_API_BASE and LLM_API_KEY in .env for AI-powered synthesis.*")
    return "\n".join(parts)


# ===================================================================
# System Prompt — auto-research citation mode
# ===================================================================

SYSTEM_PROMPT = """\
You are ResearchGPT, an expert AI research assistant. You have been \
given pre-fetched search results and parsed content from the web. \
Your task is to synthesize a comprehensive, accurate answer using \
the provided sources.

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
..."""


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
    logger.info('Research Gatherer API starting up...')
    logger.info(f'LLM backend: {LLM_API_BASE or "(not configured)"}')
    logger.info(f'Auth: {"enabled" if API_KEY else "disabled (set RESEARCH_API_KEY to enable)"}')
    yield
    logger.info('Research Gatherer API shutting down.')


app = FastAPI(
    title='Research Gatherer API',
    description=(
        'OpenAI-compatible API for multi-engine web research with LLM tool-calling integration.\n\n'
        'Endpoints:\n'
        '- `/v1/chat/completions` — OpenAI-compatible chat with tool calling\n'
        '- `/v1/models` — List available models\n'
        '- `/v1/search` — Direct search endpoint\n'
        '- `/v1/parse` — Direct URL parsing\n'
        '- `/v1/images` — Direct image gathering\n'
        '- `/v1/research` — Full research pipeline\n'
        '- `/v1/sessions` — Manage conversation sessions\n'
        '- `/health` — Health check'
    ),
    version='1.0.0',
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
        'llm_configured': llm.available,
        'engines_loaded': True,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }


@app.get('/v1/models', response_model=ModelListResponse)
async def list_models():
    models = [
        ModelObject(id='research-assistant', owned_by='research-gatherer'),
    ]
    if llm.available:
        models.append(
            ModelObject(id=llm.model, owned_by='llm-provider')
        )
    return ModelListResponse(data=models)


# ===================================================================
# OpenAI-Compatible Chat Completions — AUTO-RESEARCH MODE
# ===================================================================

@app.post('/v1/chat/completions')
async def chat_completions(
    request: ChatCompletionRequest,
    _: None = Depends(verify_api_key),
):
    """Auto-research chat completions.

    Every request automatically:
    1. Extracts the research query from the user's message
    2. Searches across 13+ engines via SearchEngineLoader
    3. Parses the top 3 results via Jina AI Reader
    4. Sends all context to the LLM for citation-aware synthesis
    5. Returns the answer with inline [1][2][3] citations
    """
    user_message = ''
    for msg in reversed(request.messages):
        if msg.role == 'user' and msg.content:
            user_message = msg.content
            break
    if not user_message:
        user_message = 'general research'

    query = _extract_search_query(user_message)
    logger.info(f"[ChatCompletions] Auto-research: {repr(query)}")

    if request.tools:
        return await _tool_calling_mode(request)

    if request.stream:
        return StreamingResponse(
            _auto_research_stream(query, parse_top=3),
            media_type='text/event-stream',
        )

    answer = await _auto_research(query, parse_top=3)
    return ChatCompletionResponse(
        model=request.model,
        choices=[Choice(
            message=ChatMessage(role='assistant', content=answer),
            finish_reason='stop',
        )],
    )


async def _tool_calling_mode(request: ChatCompletionRequest) -> ChatCompletionResponse:
    """Traditional tool-calling mode (when client sends custom tools)."""
    messages: List[Dict[str, Any]] = [{'role': 'system', 'content': (
        'You are ResearchGPT with access to search and parse tools. '
        'Use them to research topics and always cite sources with [1][2][3].'
    )}]
    for msg in request.messages:
        m: Dict[str, Any] = {'role': msg.role}
        if msg.content:
            m['content'] = msg.content
        if msg.tool_calls:
            m['tool_calls'] = [{'id': tc.id, 'type': 'function', 'function': {'name': tc.function.name, 'arguments': tc.function.arguments}} for tc in msg.tool_calls]
        if msg.tool_call_id:
            m['tool_call_id'] = msg.tool_call_id
        messages.append(m)

    tools_payload = [t.model_dump() for t in RESEARCH_TOOLS]
    resp_data = {}
    for _ in range(5):
        resp_data = await llm.chat(messages=messages, tools=tools_payload, tool_choice=request.tool_choice or 'auto', temperature=request.temperature or 0.3, max_tokens=request.max_tokens or 4096)
        choice = resp_data.get('choices', [{}])[0]
        msg = choice.get('message', {})
        tc_raw = msg.get('tool_calls')
        if not tc_raw or choice.get('finish_reason') != 'tool_calls':
            break
        messages.append(msg)
        for tc in tc_raw:
            fn = tc.get('function', {})
            try:
                fn_args = json.loads(fn.get('arguments', '{}'))
            except json.JSONDecodeError:
                fn_args = {}
            executor = TOOL_EXECUTORS.get(fn.get('name', ''))
            result = await _run_in_thread(executor, fn_args) if executor else {'error': 'Unknown tool'}
            messages.append({'role': 'tool', 'tool_call_id': tc['id'], 'content': json.dumps(result, default=str)[:16000]})

    choice_data = resp_data.get('choices', [{}])[0]
    msg_data = choice_data.get('message', {})
    usage_data = resp_data.get('usage', {})
    return ChatCompletionResponse(
        model=request.model,
        choices=[Choice(message=ChatMessage(role='assistant', content=msg_data.get('content', '')), finish_reason=choice_data.get('finish_reason', 'stop'))],
        usage=Usage(prompt_tokens=usage_data.get('prompt_tokens', 0), completion_tokens=usage_data.get('completion_tokens', 0), total_tokens=usage_data.get('total_tokens', 0)),
    )

# ===================================================================
    for msg in request.messages:
        m: Dict[str, Any] = {'role': msg.role}
        if msg.content:
            m['content'] = msg.content
        if msg.tool_calls:
            m['tool_calls'] = [
                {
                    'id': tc.id,
                    'type': 'function',
                    'function': {
                        'name': tc.function.name,
                        'arguments': tc.function.arguments,
                    },
                }
                for tc in msg.tool_calls
            ]
        if msg.tool_call_id:
            m['tool_call_id'] = msg.tool_call_id
        messages.append(m)

    # Prepare tools for LLM
    tools_payload = None
    if request.tools is not None:
        tools_payload = [t.model_dump() for t in request.tools]
    else:
        tools_payload = [t.model_dump() for t in RESEARCH_TOOLS]

    tool_choice = request.tool_choice or 'auto'

    # ---- Tool-calling loop ----
    MAX_TOOL_ROUNDS = 5
    all_tool_results = []

    for round_idx in range(MAX_TOOL_ROUNDS):
        try:
            if request.stream:
                # For streaming with tool calling: do the loop non-streaming,
                # then stream the final answer.
                resp_data = await llm.chat(
                    messages=messages, tools=tools_payload,
                    tool_choice=tool_choice,
                    temperature=request.temperature or 0.7,
                    max_tokens=request.max_tokens or 2048,
                )
            else:
                resp_data = await llm.chat(
                    messages=messages, tools=tools_payload,
                    tool_choice=tool_choice,
                    temperature=request.temperature or 0.7,
                    max_tokens=request.max_tokens or 2048,
                )
        except httpx.HTTPStatusError as e:
            raise HTTPException(502, f'LLM API error: {e.response.status_code} — {e.response.text[:500]}')
        except Exception as e:
            raise HTTPException(502, f'LLM API error: {str(e)}')

        choice = resp_data.get('choices', [{}])[0]
        msg = choice.get('message', {})
        finish = choice.get('finish_reason')

        # Check for tool calls
        tool_calls_raw = msg.get('tool_calls')
        if not tool_calls_raw or finish != 'tool_calls':
            # No more tool calls — return final answer
            break

        # Append the assistant's tool-call message
        messages.append(msg)

        # Execute each tool call
        for tc in tool_calls_raw:
            fn = tc.get('function', {})
            fn_name = fn.get('name', '')
            fn_args_str = fn.get('arguments', '{}')
            tc_id = tc.get('id', f'call_{uuid.uuid4().hex[:24]}')

            try:
                fn_args = json.loads(fn_args_str) if isinstance(fn_args_str, str) else fn_args_str
            except json.JSONDecodeError:
                fn_args = {}

            logger.info(f'[Tool call] {fn_name}({json.dumps(fn_args)[:200]})')

            executor = TOOL_EXECUTORS.get(fn_name)
            if executor:
                try:
                    result = await _run_in_thread(executor, fn_args)
                except Exception as exc:
                    result = {'error': str(exc), 'traceback': traceback.format_exc()}
            else:
                result = {'error': f'Unknown tool: {fn_name}'}

            result_str = json.dumps(result, default=str)
            all_tool_results.append({'tool': fn_name, 'arguments': fn_args, 'result': result})

            # Append tool result message
            messages.append({
                'role': 'tool',
                'tool_call_id': tc_id,
                'content': result_str[:16000],  # Truncate to avoid token overflow
            })

    # Build response
    if request.stream:
        return await _build_stream_response(messages, request.model, all_tool_results)
    else:
        return _build_sync_response(messages, resp_data, request.model, all_tool_results)


def _build_sync_response(
    messages: list, resp_data: dict, model: str, tool_results: list,
) -> ChatCompletionResponse:
    """Build a non-streaming ChatCompletionResponse."""
    choice_data = resp_data.get('choices', [{}])[0]
    msg_data = choice_data.get('message', {})
    finish = choice_data.get('finish_reason', 'stop')
    usage_data = resp_data.get('usage', {})

    content = msg_data.get('content', '')
    # If no content but tool results exist, summarize
    if not content and tool_results:
        summaries = []
        for tr in tool_results:
            if tr['result'] and not tr['result'].get('error'):
                if tr['tool'] == 'search':
                    summaries.append(f"Found {tr['result'].get('count', 0)} results for '{tr['result'].get('query', '')}'")
                elif tr['tool'] in ('parse_url', 'parse_urls'):
                    summaries.append(f"Parsed content from {tr['result'].get('url', 'URL')}")
                elif tr['tool'] == 'deep_research':
                    summaries.append(
                        f"Research complete: {tr['result'].get('links_collected', 0)} links, "
                        f"{tr['result'].get('documents_parsed', 0)} documents"
                    )
        content = '\n'.join(summaries) if summaries else 'Tool execution completed.'

    # Build tool_calls from resp if present
    tc_raw = msg_data.get('tool_calls')
    tool_calls_out = None
    if tc_raw:
        tool_calls_out = [
            ToolCallMessage(
                id=tc.get('id', ''),
                function=ToolCallFunction(
                    name=tc['function']['name'],
                    arguments=tc['function']['arguments'],
                ),
            )
            for tc in tc_raw
        ]

    assistant_msg = ChatMessage(
        role='assistant',
        content=content,
        tool_calls=tool_calls_out,
    )

    return ChatCompletionResponse(
        model=model,
        choices=[Choice(message=assistant_msg, finish_reason=finish)],
        usage=Usage(
            prompt_tokens=usage_data.get('prompt_tokens', 0),
            completion_tokens=usage_data.get('completion_tokens', 0),
            total_tokens=usage_data.get('total_tokens', 0),
        ),
    )


async def _build_stream_response(
    messages: list, model: str, tool_results: list,
) -> StreamingResponse:
    """Build a streaming SSE response. After tool-calling loop, stream the final LLM answer."""
    stream_id = f"chatcmpl-{uuid.uuid4().hex[:12]}"

    async def event_generator():
        # Send role delta
        role_chunk = ChatCompletionChunk(
            id=stream_id, model=model,
            choices=[StreamChoice(delta={'role': 'assistant'}, finish_reason=None)],
        )
        yield f"data: {role_chunk.model_dump_json()}\n\n"

        # Get final content from LLM (streaming)
        messages_for_stream = messages.copy()
        try:
            async for sse_line in llm.chat_stream(
                messages=messages_for_stream,
                tools=[t.model_dump() for t in RESEARCH_TOOLS],
                tool_choice='auto',
                temperature=0.7,
                max_tokens=2048,
            ):
                yield sse_line
        except Exception:
            # Fallback: construct a summary from tool results
            content = _summarize_tool_results(tool_results)
            content_chunk = ChatCompletionChunk(
                id=stream_id, model=model,
                choices=[StreamChoice(delta={'content': content}, finish_reason=None)],
            )
            yield f"data: {content_chunk.model_dump_json()}\n\n"

        # Send finish
        finish_chunk = ChatCompletionChunk(
            id=stream_id, model=model,
            choices=[StreamChoice(delta={}, finish_reason='stop')],
        )
        yield f"data: {finish_chunk.model_dump_json()}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type='text/event-stream')


def _summarize_tool_results(tool_results: list) -> str:
    """Summarize tool results into a readable text."""
    parts = []
    for tr in tool_results:
        name = tr['tool']
        res = tr.get('result', {})
        if res.get('error'):
            parts.append(f"**{name}** failed: {res['error']}")
            continue
        if name == 'search':
            links = res.get('links', [])
            query = res.get('query', '')
            parts.append(f"Search for **{query}** returned {len(links)} results.")
            if links:
                parts.append("Top results:")
                for url in links[:5]:
                    parts.append(f"- {url}")
        elif name == 'parse_url':
            parts.append(f"Parsed **{res.get('url', 'URL')}** — {res.get('markdown_length', 0)} chars")
        elif name == 'parse_urls':
            parts.append(f"Parsed {res.get('success_count', 0)} / {res.get('success_count', 0) + res.get('fail_count', 0)} URLs")
        elif name == 'deep_research':
            parts.append(
                f"Deep research completed: {res.get('links_collected', 0)} links, "
                f"{res.get('documents_parsed', 0)} documents parsed.\n"
                f"Summary: {res.get('summary_path', 'N/A')}"
            )
        elif name == 'gather_images':
            parts.append(f"Gathered {res.get('images_found', 0)} images → {res.get('output_dir', '')}")
    return '\n\n'.join(parts) if parts else 'All tools executed successfully.'


# ===================================================================
# Direct REST Endpoints
# ===================================================================

@app.get('/v1/search', response_model=SearchResponse)
async def search_links(
    q: str = Query(..., description='Search query'),
    _: None = Depends(verify_api_key),
):
    """Search across multiple engines and return deduplicated URLs."""
    result = await _run_in_thread(_execute_search, q)
    return SearchResponse(**result)


@app.post('/v1/search', response_model=SearchResponse)
async def search_links_post(
    body: SearchRequest,
    _: None = Depends(verify_api_key),
):
    """Search across multiple engines (POST)."""
    result = await _run_in_thread(_execute_search, body.query)
    return SearchResponse(**result)


@app.post('/v1/parse', response_model=ParseResponse)
async def parse_urls_endpoint(
    body: ParseRequest,
    _: None = Depends(verify_api_key),
):
    """Parse URLs into markdown content via Jina AI Reader."""
    max_items = min(len(body.urls), 20)
    urls = body.urls[:max_items]
    t0 = time.monotonic()
    parser = JinaParser(rate_limit_delay=0.5, request_timeout=30)
    results: List[ParseResponseItem] = []
    success = 0

    for url in urls:
        try:
            md = await _run_in_thread(parser.parse_url, url)
            if md:
                title = parser.extract_title(md)
                results.append(ParseResponseItem(
                    url=url, title=title,
                    markdown_length=len(md), saved=False,
                    content=md[:8000] if body.include_content else None,
                ))
                success += 1
            else:
                results.append(ParseResponseItem(
                    url=url, markdown_length=0, saved=False,
                    error='Parse failed',
                ))
        except Exception as e:
            results.append(ParseResponseItem(
                url=url, markdown_length=0, saved=False, error=str(e),
            ))

    elapsed = time.monotonic() - t0
    return ParseResponse(
        results=results, success_count=success,
        fail_count=len(urls) - success,
        elapsed_seconds=round(elapsed, 2),
    )


@app.post('/v1/images', response_model=ImageResponse)
async def gather_images_endpoint(
    body: ImageRequest,
    _: None = Depends(verify_api_key),
):
    """Search and download images for given keywords."""
    result = await _run_in_thread(
        _execute_gather_images, body.keywords, body.min_size,
    )
    return ImageResponse(
        keywords=result['keywords'],
        output_dir=result['output_dir'],
        elapsed_seconds=result['elapsed_seconds'],
    )


@app.post('/v1/research', response_model=DeepResearchResponse)
async def deep_research_endpoint(
    body: DeepResearchRequest,
    _: None = Depends(verify_api_key),
):
    """Full research pipeline: search → parse → summarize."""
    result = await _run_in_thread(
        _execute_deep_research,
        body.query, body.academic, body.max_parse,
    )
    return DeepResearchResponse(
        query=result['query'],
        links_collected=result['links_collected'],
        documents_parsed=result['documents_parsed'],
        summary_path=result.get('summary_path'),
        elapsed_seconds=result['elapsed_seconds'],
    )


# ===================================================================
# Session Management
# ===================================================================

@app.get('/v1/sessions')
async def list_sessions(_: None = Depends(verify_api_key)):
    """List active conversation sessions."""
    return {'sessions': conversations.list_sessions()}


@app.get('/v1/sessions/{session_id}/messages')
async def get_session_messages(session_id: str, _: None = Depends(verify_api_key)):
    """Get messages for a conversation session."""
    msgs = conversations.get(session_id)
    if not msgs:
        raise HTTPException(404, 'Session not found')
    return {'session_id': session_id, 'messages': [m.model_dump() for m in msgs]}


@app.delete('/v1/sessions/{session_id}')
async def delete_session(session_id: str, _: None = Depends(verify_api_key)):
    """Delete a conversation session."""
    conversations.delete(session_id)
    return {'deleted': session_id}


# ===================================================================
# CLI Entry Point
# ===================================================================

def main():
    parser = argparse.ArgumentParser(description='Research Gatherer API Server')
    parser.add_argument('--host', default='127.0.0.1', help='Bind host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000, help='Bind port (default: 8000)')
    parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    args = parser.parse_args()

    import uvicorn
    uvicorn.run(
        'ai_api:app',
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level='info',
    )


if __name__ == '__main__':
    main()
