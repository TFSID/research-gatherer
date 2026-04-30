#!/usr/bin/env python3
"""
Research Gatherer - Deep Research Source Gathering Tool
Combines search engine capabilities with Jina AI parser for comprehensive research

Workflow:
1. Search by keywords or wordlist
2. Gather links from search results
3. Parse links with Jina parser
4. Organize parsed content into structured files & folders

Quoted-phrase support:
  Queries may contain double-quote (") characters for exact-phrase searches,
  e.g.  site:example.com "exact phrase" filetype:pdf
  Pass them on the CLI with -k (shell quoting is handled automatically) or
  place them verbatim in a keyword-list file used with -l.
"""

import os
import sys
import argparse
import threading
import importlib
import pkgutil
import inspect
import requests
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Optional, Dict
from logging import DEBUG
from datetime import datetime

# Add parent directories to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'engines'))

from helper import setup_logger
from image_gatherer import ImageGatherer

logger = setup_logger()


class JinaParser:
    """Jina AI Parser for converting URLs to markdown"""

    def __init__(self, rate_limit_delay=0.5, request_timeout=30, max_retries=2):
        self.rate_limit_delay = rate_limit_delay
        self.request_timeout = request_timeout
        self.max_retries = max_retries

    def parse_url(self, url: str) -> Optional[str]:
        """
        Parse URL using Jina AI Reader API with exponential backoff on 429.

        Returns markdown string or None if all retries failed.
        """
        jina_url = f"https://r.jina.ai/{url}"

        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(f"Parsing with Jina: {url} (attempt {attempt + 1})")
                response = requests.get(jina_url, timeout=self.request_timeout)

                # Rate-limited by Jina — back off and retry
                if response.status_code == 429 and attempt < self.max_retries:
                    backoff = 2 ** attempt + 1.0  # 2s, 3s, 5s
                    logger.warning(
                        f"Jina 429 on {url}, backing off {backoff:.1f}s "
                        f"(attempt {attempt + 1}/{self.max_retries + 1})"
                    )
                    time.sleep(backoff)
                    continue

                response.raise_for_status()
                if self.rate_limit_delay > 0:
                    time.sleep(self.rate_limit_delay)
                return response.text
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries:
                    backoff = 1.5 ** attempt + 0.5
                    logger.warning(
                        f"Jina error on {url}: {e} — retry in {backoff:.1f}s"
                    )
                    time.sleep(backoff)
                    continue
                logger.error(f"Error parsing {url}: {e}")
                return None
        return None
    
    def extract_title(self, markdown_content: str) -> Optional[str]:
        """Extract title from markdown content"""
        # Try "Title: " format first
        match = re.search(r'^Title:\s*(.+)$', markdown_content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        # Fallback: first H1 heading
        match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def sanitize_filename(self, title: str, max_length: int = 80) -> str:
        """Clean title for valid filename.

        max_length defaults to 80 so that even with deep parent paths we stay
        well under Windows' 260-char MAX_PATH limit.
        """
        sanitized = re.sub(r'[<>:"/\\|?*]', '', title)
        sanitized = re.sub(r'\s+', ' ', sanitized)
        sanitized = sanitized.strip()[:max_length]
        return f"{sanitized}.md"


# Patterns that identify a "parsed" document as actually being a bot-check /
# paywall / access-denied stub rather than the real article content.
GARBAGE_TITLE_PATTERNS = [
    r'recaptcha',
    r'checking your browser',
    r'just a moment',
    r'access denied',
    r'attention required',
    r'cloudflare',
    r'403 forbidden',
    r'are you a robot',
    r'verify you are human',
    r'enable javascript',
]

GARBAGE_TITLE_RE = re.compile('|'.join(GARBAGE_TITLE_PATTERNS), re.IGNORECASE)


def is_garbage_parse(title: Optional[str], body: str, min_body_chars: int = 500) -> bool:
    """Return True if a Jina parse looks like a bot-wall / paywall stub."""
    if title and GARBAGE_TITLE_RE.search(title):
        return True
    if body is None:
        return True
    # Strip frontmatter/title lines for a cheap length check
    stripped = body.strip()
    if len(stripped) < min_body_chars:
        return True
    return False


class LinkManager:
    """Manages link collection and deduplication"""
    
    def __init__(self, storage_file='collected_links.txt'):
        self.storage_file = storage_file
        self.links = set()
        self.load_existing_links()
    
    def load_existing_links(self):
        """Load existing links from storage file"""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                self.links = set(line.strip() for line in f if line.strip())
            logger.info(f"Loaded {len(self.links)} existing links")
    
    def add_links(self, new_links: List[str]):
        """Add new links and save to file"""
        if not isinstance(new_links, list):
            return
        
        added_count = 0
        for link in new_links:
            if link and link not in self.links:
                self.links.add(link)
                with open(self.storage_file, 'a', encoding='utf-8') as f:
                    f.write(f'{link}\n')
                added_count += 1
        
        if added_count > 0:
            logger.info(f"Added {added_count} new links")
    
    def get_all_links(self) -> List[str]:
        """Get all collected links"""
        return list(self.links)


class SearchEngineLoader:
    """Dynamically loads search engines"""
    
    def __init__(self, engines_dir='engines', debug_mode=False):
        self.engines_dir = engines_dir
        self.debug_mode = debug_mode
        self.engines = []
    
    def load_engines(self):
        """Load all available search engines"""
        engines_path = os.path.join(os.path.dirname(__file__), self.engines_dir)
        
        if not os.path.exists(engines_path):
            logger.error(f"Engines directory not found: {engines_path}")
            return []
        
        # Import engines module
        sys.path.insert(0, engines_path)
        
        for filename in os.listdir(engines_path):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(module_name)
                    
                    # Find engine classes
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and hasattr(obj, 'search'):
                            try:
                                instance = obj(debug=self.debug_mode)
                                self.engines.append(instance)
                                logger.debug(f"Loaded engine: {name}")
                            except Exception as e:
                                logger.error(f"Failed to instantiate {name}: {e}")
                except Exception as e:
                    logger.error(f"Failed to load module {module_name}: {e}")
        
        logger.info(f"Loaded {len(self.engines)} search engines")
        return self.engines
    
    def search_all(self, keyword: str) -> List[str]:
        """Search using all loaded engines"""
        all_links = []
        threads = []
        results = {}
        
        def search_task(engine, keyword, results_dict):
            try:
                links = engine.search(keyword)
                if links:
                    results_dict[engine.__class__.__name__] = links
            except Exception as e:
                logger.error(f"Error in {engine.__class__.__name__}: {e}")
        
        for engine in self.engines:
            t = threading.Thread(target=search_task, args=(engine, keyword, results))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Collect all links
        for engine_name, links in results.items():
            all_links.extend(links)
            logger.info(f"{engine_name}: Found {len(links)} links")
        
        return all_links


class ResearchGatherer:
    """Main research gathering orchestrator"""

    def __init__(
        self,
        output_dir='research_output',
        debug_mode=False,
        parse_workers=1,
        jina_timeout=30,
        rate_limit_delay=0.5,
        max_parse=0,
        deadline=None,
    ):
        self.output_dir = output_dir
        self.debug_mode = debug_mode
        self.parse_workers = max(1, parse_workers)
        # When parsing in parallel, per-call rate limiting becomes counter-
        # productive — concurrency already paces the API. Drop the sleep.
        effective_delay = 0 if self.parse_workers > 1 else rate_limit_delay
        self.link_manager = LinkManager(os.path.join(output_dir, 'collected_links.txt'))
        self.jina_parser = JinaParser(
            rate_limit_delay=effective_delay,
            request_timeout=jina_timeout,
        )
        self.search_loader = SearchEngineLoader(debug_mode=debug_mode)
        self.max_parse = max_parse
        # Parse-phase wall-clock budget. Stored as a duration (seconds) and
        # converted to an absolute monotonic deadline lazily at parse start,
        # so that any time spent in the search phase does not eat into the
        # parse budget.
        self.parse_budget_seconds = deadline
        self.deadline = None

        # Create output directories
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        Path(os.path.join(output_dir, 'parsed_content')).mkdir(parents=True, exist_ok=True)

    def _budget_exhausted(self) -> bool:
        return self.deadline is not None and time.monotonic() >= self.deadline
    
    def search_and_collect(self, keywords: List[str]):
        """Search for keywords and collect links"""
        logger.info(f"Starting search for {len(keywords)} keyword(s)")
        
        # Load search engines
        engines = self.search_loader.load_engines()
        if not engines:
            logger.error("No search engines loaded!")
            return
        
        for idx, keyword in enumerate(keywords, 1):
            # Use repr() so that embedded double-quotes don't break log formatting
            logger.info("[%d/%d] Searching: %s", idx, len(keywords), repr(keyword))
            links = self.search_loader.search_all(keyword)
            self.link_manager.add_links(links)
            logger.info(f"Total unique links collected: {len(self.link_manager.links)}")
    
    def parse_collected_links(self, keyword_filter: Optional[str] = None):
        """Parse collected links with Jina (parallel, filterable, budgeted)."""
        # Start the parse-phase clock now (not at init) so search time doesn't
        # eat into the budget.
        if self.parse_budget_seconds and self.parse_budget_seconds > 0:
            self.deadline = time.monotonic() + self.parse_budget_seconds

        links = self.link_manager.get_all_links()

        if not links:
            logger.warning("No links to parse!")
            return

        # Multi-value filter: comma-separated list of substrings, OR semantics.
        # A link is kept if ANY substring matches (case-insensitive).
        if keyword_filter:
            substrs = [s.strip().lower() for s in keyword_filter.split(',') if s.strip()]
            if substrs:
                links = [l for l in links if any(s in l.lower() for s in substrs)]
                logger.info(
                    f"Filtered to {len(links)} links matching any of: {substrs}"
                )

        # Hard cap on how many URLs we're willing to parse this run
        if self.max_parse and len(links) > self.max_parse:
            logger.info(
                f"Capping parse set from {len(links)} to --max-parse={self.max_parse}"
            )
            links = links[: self.max_parse]

        total = len(links)
        if total == 0:
            logger.warning("No links left after filtering.")
            return

        save_lock = threading.Lock()
        file_counter = {'n': 0}
        success_count = 0
        failed_urls: List[str] = []

        def process(idx_url):
            idx, url = idx_url
            if self._budget_exhausted():
                return ('skip', url)
            logger.info(f"[{idx}/{total}] Parsing: {url}")
            markdown_content = self.jina_parser.parse_url(url)
            if not markdown_content:
                return ('fail', url)

            title = self.jina_parser.extract_title(markdown_content)

            # Quality gate: reject bot-walls, paywalls, and tiny stubs.
            if is_garbage_parse(title, markdown_content):
                logger.warning(
                    f"✗ Rejected garbage parse ({title or 'no title'}): {url}"
                )
                return ('fail', url)

            if title:
                filename = self.jina_parser.sanitize_filename(title)
            else:
                with save_lock:
                    file_counter['n'] += 1
                    filename = f"content_{file_counter['n']}.md"

            domain = self._extract_domain(url)
            category_dir = os.path.join(self.output_dir, 'parsed_content', domain)

            with save_lock:
                Path(category_dir).mkdir(parents=True, exist_ok=True)
                filepath = os.path.join(category_dir, filename)
                counter = 1
                original_filepath = filepath
                while os.path.exists(filepath):
                    name, ext = os.path.splitext(original_filepath)
                    filepath = f"{name}_{counter}{ext}"
                    counter += 1
                try:
                    metadata = (
                        "---\n"
                        f"source: {url}\n"
                        f"parsed_date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"domain: {domain}\n"
                        "---\n\n"
                    )
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(metadata + markdown_content)
                    logger.info(f"✓ Saved: {os.path.relpath(filepath, self.output_dir)}")
                    return ('ok', url)
                except Exception as e:
                    logger.error(f"✗ Error saving file: {e}")
                    return ('fail', url)

        workers = min(self.parse_workers, total)
        logger.info(
            f"Starting to parse {total} URLs with {workers} worker(s)"
            + (f" (deadline {max(0, int(self.deadline - time.monotonic()))}s away)"
               if self.deadline else "")
        )

        if workers == 1:
            for item in enumerate(links, 1):
                status, url = process(item)
                if status == 'ok':
                    success_count += 1
                elif status == 'fail':
                    failed_urls.append(url)
                elif status == 'skip':
                    logger.warning(f"Deadline reached — skipping remaining URLs")
                    break
        else:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {
                    pool.submit(process, item): item
                    for item in enumerate(links, 1)
                }
                for fut in as_completed(futures):
                    try:
                        status, url = fut.result()
                    except Exception as e:
                        logger.error(f"Worker crashed: {e}")
                        continue
                    if status == 'ok':
                        success_count += 1
                    elif status == 'fail':
                        failed_urls.append(url)

        logger.info("=" * 60)
        logger.info(f"Completed! {success_count}/{total} URLs successfully parsed")

        if failed_urls:
            failed_file = os.path.join(self.output_dir, 'failed_urls.txt')
            with open(failed_file, 'w', encoding='utf-8') as f:
                for url in failed_urls:
                    f.write(f"{url}\n")
            logger.info(f"Failed URLs saved to: {failed_file}")
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL for categorization"""
        match = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if match:
            domain = match.group(1)
            # Clean domain for folder name
            domain = re.sub(r'[<>:"/\\|?*]', '_', domain)
            return domain
        return 'uncategorized'
    
    def generate_summary(self):
        """Generate research summary report"""
        summary_file = os.path.join(self.output_dir, 'RESEARCH_SUMMARY.md')
        
        # Count files by category
        parsed_dir = os.path.join(self.output_dir, 'parsed_content')
        categories = {}
        
        if os.path.exists(parsed_dir):
            for category in os.listdir(parsed_dir):
                category_path = os.path.join(parsed_dir, category)
                if os.path.isdir(category_path):
                    file_count = len([f for f in os.listdir(category_path) if f.endswith('.md')])
                    categories[category] = file_count
        
        # Write summary
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"# Research Gathering Summary\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"## Statistics\n\n")
            f.write(f"- **Total Links Collected:** {len(self.link_manager.links)}\n")
            f.write(f"- **Total Categories:** {len(categories)}\n")
            f.write(f"- **Total Parsed Documents:** {sum(categories.values())}\n\n")
            f.write(f"## Categories\n\n")
            
            for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                f.write(f"- **{category}**: {count} documents\n")
            
            f.write(f"\n## Output Structure\n\n")
            f.write(f"```\n")
            f.write(f"{self.output_dir}/\n")
            f.write(f"├── collected_links.txt\n")
            f.write(f"├── RESEARCH_SUMMARY.md\n")
            f.write(f"└── parsed_content/\n")
            for category in sorted(categories.keys()):
                f.write(f"    ├── {category}/\n")
            f.write(f"```\n")
        
        logger.info(f"Summary report saved: {summary_file}")


def sanitize_query(query: str) -> str:
    """
    Normalise a search query string so that:
    - Leading/trailing whitespace is stripped.
    - Unicode \u201c/\u201d (\u201c\u201d) \u2018/\u2019 (\u2018\u2019) "smart" quotes are
      converted to plain ASCII double-quotes so search engines receive
      standard percent-encoded %22 tokens.
    - Internal double-quotes are preserved verbatim (they represent
      exact-phrase operators, e.g.  filetype:pdf "exact phrase").
    """
    # Normalise Unicode curly/smart quote pairs -> straight ASCII "
    for lq, rq in (('\u201c', '\u201d'), ('\u2018', '\u2019'),
                   ('\u00ab', '\u00bb'), ('\u2039', '\u203a')):
        query = query.replace(lq, '"').replace(rq, '"')
    return query.strip()


def main():
    parser = argparse.ArgumentParser(
        description='Research Gatherer - Deep Research Source Gathering Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=r"""
Examples:
  # Search and collect links (simple keyword)
  python research_gatherer.py -k "machine learning" -o ml_research

  # Quoted-phrase / dork query  (quotes are preserved):
  python research_gatherer.py -k "site:researchgate.net \"DDoS\" filetype:pdf" -o ddos_research
  # Or use a keyword-list file (quotes are carried through verbatim):
  #   queries.txt contents:  site:researchgate.net "DDoS" filetype:pdf
  python research_gatherer.py -l queries.txt -o ddos_research

  # Search from keyword list
  python research_gatherer.py -l keywords.txt -o research_output

  # Parse collected links
  python research_gatherer.py --parse-only -o research_output

  # Full workflow: search + parse
  python research_gatherer.py -k "cybersecurity" --auto-parse
        """
    )
    
    parser.add_argument('-k', '--keyword',
                        dest='keyword',
                        nargs='+',
                        help=(
                            'Keyword / query to search. Multiple tokens are joined '
                            'into a single query string, so quoted phrases work '
                            'naturally: -k site:example.com "exact phrase" filetype:pdf'
                        ))
    parser.add_argument('-l', '--keyword-list',
                        dest='keyword_list',
                        help='File containing keywords (one per line)')
    parser.add_argument('-o', '--output',
                        dest='output_dir',
                        help='Output directory (default: research_output)',
                        default='research_output')
    parser.add_argument('--parse-only',
                        dest='parse_only',
                        action='store_true',
                        help='Only parse previously collected links')
    parser.add_argument('--auto-parse',
                        dest='auto_parse',
                        action='store_true',
                        help='Automatically parse after collecting links')
    parser.add_argument('--images',
                        dest='gather_images',
                        action='store_true',
                        help='Search and download presentation-quality images for the keywords')
    parser.add_argument('--images-min-size',
                        dest='images_min_size',
                        type=int,
                        default=300,
                        metavar='PX',
                        help='Minimum image dimension in pixels (default: 300). Use 0 to download all sizes including icons/assets.')
    parser.add_argument('--filter',
                        dest='filter',
                        help=(
                            'Filter links when parsing. Comma-separated list of '
                            'substrings with OR semantics, e.g. '
                            '--filter "ncbi.nlm.nih.gov,apa.org,sciencedirect.com"'
                        ))
    parser.add_argument('--parse-workers',
                        dest='parse_workers',
                        type=int,
                        default=1,
                        help='Parallel Jina parse workers (default: 1). '
                             'Recommended 5-8 for time-budgeted runs.')
    parser.add_argument('--jina-timeout',
                        dest='jina_timeout',
                        type=int,
                        default=30,
                        help='Per-URL Jina HTTP timeout in seconds (default: 30). '
                             'Lower for stricter time budgets.')
    parser.add_argument('--rate-limit',
                        dest='rate_limit',
                        type=float,
                        default=0.5,
                        help='Sequential-mode rate-limit sleep between Jina calls '
                             '(default: 0.5s). Ignored when --parse-workers > 1.')
    parser.add_argument('--max-parse',
                        dest='max_parse',
                        type=int,
                        default=0,
                        help='Hard cap on number of URLs to parse this run '
                             '(0 = no cap). Applied after --filter.')
    parser.add_argument('--max-runtime',
                        dest='max_runtime',
                        type=int,
                        default=0,
                        help='Overall wall-clock budget in seconds for the parse '
                             'phase. When exhausted, in-flight parses finish but '
                             'no new ones are scheduled. 0 = no budget.')
    parser.add_argument('--academic',
                        dest='academic',
                        action='store_true',
                        help='Shortcut: sets --filter to a curated list of '
                             'academic/peer-reviewed domains (PMC, PubMed, APA, '
                             'ScienceDirect, Nature, arXiv, ResearchGate, '
                             'Frontiers, Springer, Wiley, SAGE, JSTOR).')
    parser.add_argument('-d', '--debug',
                        dest='debug_mode',
                        action='store_true',
                        help='Enable debug mode')
    
    args = parser.parse_args()
    
    if not any([args.keyword, args.keyword_list, args.parse_only, args.gather_images]):
        parser.print_help()
        sys.exit(1)

    # ------------------------------------------------------------------
    # Normalise keyword argument
    # When -k is given, argparse (with nargs='+') splits on spaces that
    # the shell already handled.  We rejoin all tokens so that a call like
    #   -k site:example.com "exact phrase" filetype:pdf
    # arrives here as the single string:
    #   'site:example.com exact phrase filetype:pdf'
    # with the shell having stripped the surrounding quotes.  To preserve
    # the exact-phrase intent the user should either:
    #   a) wrap the whole query in an extra set of quotes on the shell, OR
    #   b) use a -l keyword-list file where quotes are stored verbatim.
    # Either way we normalise smart/curly quotes -> straight ASCII quotes.
    # ------------------------------------------------------------------
    
    # Setup logging
    if args.debug_mode:
        logger.setLevel(DEBUG)

    # --academic expands to a curated domain allow-list unless the user
    # already provided an explicit --filter
    if args.academic and not args.filter:
        args.filter = (
            "pmc.ncbi.nlm.nih.gov,pubmed.ncbi.nlm.nih.gov,ncbi.nlm.nih.gov,"
            "apa.org,sciencedirect.com,nature.com,arxiv.org,researchgate.net,"
            "frontiersin.org,springer.com,link.springer.com,onlinelibrary.wiley.com,"
            "journals.sagepub.com,jstor.org,tandfonline.com,cambridge.org,"
            "oxfordacademic.com,academic.oup.com"
        )

    # Initialize gatherer. --max-runtime is passed as a DURATION; the
    # gatherer converts it to a monotonic deadline at parse start.
    gatherer = ResearchGatherer(
        output_dir=args.output_dir,
        debug_mode=args.debug_mode,
        parse_workers=args.parse_workers,
        jina_timeout=args.jina_timeout,
        rate_limit_delay=args.rate_limit,
        max_parse=args.max_parse,
        deadline=args.max_runtime if args.max_runtime and args.max_runtime > 0 else None,
    )
    
    # Parse-only mode
    if args.parse_only:
        logger.info("Parse-only mode: Processing collected links")
        gatherer.parse_collected_links(keyword_filter=args.filter)
        gatherer.generate_summary()
        return
    
    # Collect keywords
    keywords = []
    if args.keyword:
        # nargs='+' gives us a list; rejoin into a single query string so
        # that the user can write:  -k site:x.com "phrase" filetype:pdf
        # The shell strips the inner quotes around "phrase", but everything
        # is rejoined here as one coherent query string.
        raw_query = ' '.join(args.keyword)
        keywords.append(sanitize_query(raw_query))
    elif args.keyword_list:
        if os.path.exists(args.keyword_list):
            # utf-8-sig strips an optional BOM that Windows editors add.
            with open(args.keyword_list, 'r', encoding='utf-8-sig') as f:
                keywords = [
                    sanitize_query(line)
                    for line in f
                    if line.strip() and not line.lstrip().startswith('#')
                ]
            logger.info(f"Loaded {len(keywords)} keywords from {args.keyword_list}")
        else:
            logger.error(f"Keyword list file not found: {args.keyword_list}")
            sys.exit(1)
    
    # Search and collect
    gatherer.search_and_collect(keywords)
    
    # Auto-parse if requested
    if args.auto_parse:
        logger.info("\nStarting auto-parse...")
        gatherer.parse_collected_links(keyword_filter=args.filter)
        gatherer.generate_summary()
    else:
        logger.info("\nSearch complete! To parse collected links, run:")
        logger.info(f"  python {sys.argv[0]} --parse-only -o {args.output_dir}")

    # Image gathering (runs independently of text parse; works with or without --auto-parse)
    if args.gather_images:
        if not keywords:
            logger.error("--images requires keywords (-k or -l)")
            sys.exit(1)
        logger.info("\nStarting image gathering...")
        image_gatherer = ImageGatherer(
            output_dir=args.output_dir,
            debug_mode=args.debug_mode,
            min_image_size=args.images_min_size,
        )
        image_gatherer.gather(keywords)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
