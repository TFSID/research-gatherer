#!/usr/bin/env python3
"""
Image Gatherer - Visual source search and download module for Research Gatherer.

Searches multiple image search engines in parallel, downloads results,
validates them with Pillow, and records source attribution in a manifest.

Usage (standalone):
    python image_gatherer.py -k "F5 BIG-IP architecture" -o research_output
    python image_gatherer.py -k "network diagram" -o out --min-size 0   # all sizes
"""

import os
import re
import io
import sys
import json
import time
import random
import threading
import importlib
import inspect
import requests
from pathlib import Path
from typing import List, Optional, Tuple, Dict
from datetime import datetime
from urllib.parse import urlparse

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'utils'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'engines_image'))

from helper import setup_logger, random_agent

logger = setup_logger(name='ImageGatherer')

# Query suffix appended to every image search to bias toward diagrams/infographics
IMAGE_QUERY_SUFFIX = 'presentation diagram infographic'

# Default minimum dimension (px) to filter icons/tiny assets; 0 = no filter
DEFAULT_MIN_DIMENSION = 300

# Download rate limiting
DOWNLOAD_DELAY_MIN = 1.0
DOWNLOAD_DELAY_MAX = 3.0

# Pillow format → file extension mapping
_FORMAT_EXT = {
    'JPEG': '.jpg',
    'PNG': '.png',
    'GIF': '.gif',
    'WEBP': '.webp',
    'BMP': '.bmp',
    'TIFF': '.tiff',
    'ICO': '.ico',
}


# ---------------------------------------------------------------------------
# Value object
# ---------------------------------------------------------------------------

class ImageRecord:
    """Holds metadata about a discovered image URL."""

    __slots__ = ('image_url', 'source_page', 'alt_text', 'engine_name', 'found_date')

    def __init__(
        self,
        image_url: str,
        source_page: str = '',
        alt_text: str = '',
        engine_name: str = '',
        found_date: str = '',
    ):
        self.image_url = image_url
        self.source_page = source_page
        self.alt_text = alt_text
        self.engine_name = engine_name
        self.found_date = found_date or datetime.now().strftime('%Y-%m-%d %H:%M:%S')


# ---------------------------------------------------------------------------
# Image engine loader (mirrors SearchEngineLoader)
# ---------------------------------------------------------------------------

class ImageEngineLoader:
    """Dynamically loads image search engines from engines_image/."""

    def __init__(self, engines_dir: str = 'engines_image', debug_mode: bool = False):
        self.engines_dir = engines_dir
        self.debug_mode = debug_mode
        self.engines: List = []

    def load_engines(self) -> List:
        engines_path = os.path.join(os.path.dirname(__file__), self.engines_dir)
        if not os.path.exists(engines_path):
            logger.error(f'Image engines directory not found: {engines_path}')
            return []

        sys.path.insert(0, engines_path)

        for filename in os.listdir(engines_path):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(module_name)
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and hasattr(obj, 'search'):
                            try:
                                instance = obj(debug=self.debug_mode)
                                self.engines.append(instance)
                                logger.debug(f'Loaded image engine: {name}')
                            except Exception as e:
                                logger.error(f'Failed to instantiate {name}: {e}')
                except Exception as e:
                    logger.error(f'Failed to load image module {module_name}: {e}')

        logger.info(f'Loaded {len(self.engines)} image search engines')
        return self.engines

    def search_all(self, keyword: str) -> List[str]:
        """
        Run all engines in parallel with augmented keyword.
        Returns deduplicated list of image URLs.
        """
        augmented = f'{keyword} {IMAGE_QUERY_SUFFIX}'
        all_urls: List[str] = []
        results: Dict[str, List[str]] = {}
        threads: List[threading.Thread] = []
        lock = threading.Lock()

        def _task(engine, kw: str, out: dict):
            try:
                urls = engine.search(kw)
                if urls:
                    with lock:
                        out[engine.__class__.__name__] = urls
            except Exception as e:
                logger.error(f'Error in {engine.__class__.__name__}: {e}')

        for engine in self.engines:
            t = threading.Thread(target=_task, args=(engine, augmented, results))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        seen: set = set()
        for engine_name, urls in results.items():
            new_count = 0
            for url in urls:
                if url not in seen:
                    seen.add(url)
                    all_urls.append(url)
                    new_count += 1
            logger.info(f'{engine_name}: {new_count} unique image URLs')

        return all_urls


# ---------------------------------------------------------------------------
# Image validator (Pillow)
# ---------------------------------------------------------------------------

class ImageValidator:
    """Validates downloaded image bytes using Pillow."""

    def __init__(self, min_dimension: int = DEFAULT_MIN_DIMENSION):
        self.min_dimension = min_dimension
        self._pillow_available = self._check_pillow()

    @staticmethod
    def _check_pillow() -> bool:
        try:
            from PIL import Image  # noqa: F401
            return True
        except ImportError:
            logger.warning('Pillow not installed — image validation disabled. Run: pip install Pillow')
            return False

    def validate(self, image_bytes: bytes) -> Tuple[bool, int, int]:
        """
        Returns (is_valid, width, height).
        is_valid=True when bytes are a valid image AND both dimensions >= min_dimension
        (or min_dimension == 0, in which case size is not checked).
        """
        if not self._pillow_available:
            # Without Pillow, accept everything (can't validate)
            return True, 0, 0

        try:
            from PIL import Image, UnidentifiedImageError
            img = Image.open(io.BytesIO(image_bytes))
            w, h = img.size

            if self.min_dimension > 0 and (w < self.min_dimension or h < self.min_dimension):
                return False, w, h

            return True, w, h
        except Exception:
            return False, 0, 0

    def get_format(self, image_bytes: bytes) -> Optional[str]:
        """Returns Pillow format string ('JPEG', 'PNG', etc.) or None."""
        if not self._pillow_available:
            return None
        try:
            from PIL import Image
            img = Image.open(io.BytesIO(image_bytes))
            return img.format
        except Exception:
            return None


# ---------------------------------------------------------------------------
# Image downloader
# ---------------------------------------------------------------------------

class ImageDownloader:
    """Downloads, validates, saves images and maintains the attribution manifest."""

    def __init__(
        self,
        output_dir: str,
        min_dimension: int = DEFAULT_MIN_DIMENSION,
        delay_range: Tuple[float, float] = (DOWNLOAD_DELAY_MIN, DOWNLOAD_DELAY_MAX),
    ):
        self.output_dir = output_dir
        self.delay_range = delay_range
        self.validator = ImageValidator(min_dimension)
        self.images_dir = os.path.join(output_dir, 'images')
        self.download_dir = os.path.join(self.images_dir, 'downloaded')
        self.manifest_path = os.path.join(self.images_dir, 'images_manifest.md')
        self.failed_path = os.path.join(output_dir, 'failed_images.txt')
        self._manifest_header_written = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def download(self, record: ImageRecord, index: int) -> Optional[str]:
        """
        Download one image, validate, save, update manifest.
        Returns relative path from output_dir on success, None on failure.
        """
        self._ensure_dirs()
        self._ensure_manifest_header()

        # Rate limiting
        time.sleep(random.uniform(*self.delay_range))

        try:
            headers = {
                'User-Agent': random_agent(),
                'Referer': record.source_page or record.image_url,
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            }
            resp = requests.get(record.image_url, headers=headers, timeout=20, stream=True)
            resp.raise_for_status()

            # Read up to 20 MB
            image_bytes = b''
            max_bytes = 20 * 1024 * 1024
            for chunk in resp.iter_content(chunk_size=8192):
                image_bytes += chunk
                if len(image_bytes) > max_bytes:
                    logger.debug(f'Skipping {record.image_url}: exceeds 20 MB')
                    return None

            is_valid, w, h = self.validator.validate(image_bytes)
            if not is_valid:
                logger.debug(
                    f'Skipping {record.image_url}: '
                    f'{"invalid image" if w == 0 else f"dimensions {w}x{h} below threshold"}'
                )
                return None

            fmt = self.validator.get_format(image_bytes)
            domain = self._extract_domain(record.image_url)
            domain_dir = os.path.join(self.download_dir, domain)
            Path(domain_dir).mkdir(parents=True, exist_ok=True)

            filename = self._build_filename(record.image_url, index, fmt)
            filepath = os.path.join(domain_dir, filename)
            filepath = self._resolve_collision(filepath)

            with open(filepath, 'wb') as f:
                f.write(image_bytes)

            rel_path = os.path.relpath(filepath, self.output_dir).replace('\\', '/')
            size_info = f'{w}x{h}' if w else 'unknown size'
            logger.info(f'Downloaded ({size_info}): {rel_path}')

            self._append_manifest(rel_path, record, w, h)
            return rel_path

        except requests.exceptions.RequestException as e:
            logger.error(f'Failed to download {record.image_url}: {e}')
            self._append_failed(record.image_url)
            return None
        except Exception as e:
            logger.error(f'Unexpected error downloading {record.image_url}: {e}')
            self._append_failed(record.image_url)
            return None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_dirs(self):
        Path(self.download_dir).mkdir(parents=True, exist_ok=True)

    def _ensure_manifest_header(self):
        if self._manifest_header_written:
            return
        # Only write header if file doesn't already exist (safe for re-runs)
        if not os.path.exists(self.manifest_path):
            with open(self.manifest_path, 'w', encoding='utf-8') as f:
                f.write('# Image Manifest\n\n')
                f.write(f'**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n\n')
                f.write('| File | Dimensions | Alt Text | Source Page | Image URL | Found Date |\n')
                f.write('|------|------------|----------|-------------|-----------|------------|\n')
        self._manifest_header_written = True

    def _append_manifest(self, rel_path: str, record: ImageRecord, w: int, h: int):
        dim = f'{w}x{h}' if w else '—'
        alt = record.alt_text.replace('|', '/').strip() if record.alt_text else '—'
        source = record.source_page or '—'
        img_url = record.image_url

        def _link(url: str, max_display: int = 70) -> str:
            if url == '—':
                return url
            display = url if len(url) <= max_display else url[:max_display] + '…'
            return f'[{display}]({url})'

        row = (
            f'| `{rel_path}` '
            f'| {dim} '
            f'| {alt} '
            f'| {_link(source)} '
            f'| {_link(img_url)} '
            f'| {record.found_date} |\n'
        )
        with open(self.manifest_path, 'a', encoding='utf-8') as f:
            f.write(row)

    def _append_failed(self, url: str):
        with open(self.failed_path, 'a', encoding='utf-8') as f:
            f.write(f'{url}\n')

    @staticmethod
    def _extract_domain(url: str) -> str:
        m = re.search(r'https?://(?:www\.)?([^/]+)', url)
        if m:
            return re.sub(r'[<>:"/\\|?*]', '_', m.group(1))
        return 'uncategorized'

    @staticmethod
    def _build_filename(image_url: str, index: int, fmt: Optional[str]) -> str:
        parsed = urlparse(image_url)
        basename = os.path.basename(parsed.path).split('?')[0]
        name, ext = os.path.splitext(basename)

        # Prefer Pillow-detected format for accurate extension
        if fmt and fmt in _FORMAT_EXT:
            ext = _FORMAT_EXT[fmt]
        elif not ext:
            ext = '.jpg'

        # Sanitize name
        name = re.sub(r'[<>:"/\\|?*\s]', '_', name) if name else f'img_{index:04d}'
        name = name[:100]  # cap filename length

        return f'{name}{ext}'

    @staticmethod
    def _resolve_collision(filepath: str) -> str:
        if not os.path.exists(filepath):
            return filepath
        base, ext = os.path.splitext(filepath)
        counter = 1
        while True:
            candidate = f'{base}_{counter}{ext}'
            if not os.path.exists(candidate):
                return candidate
            counter += 1


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

class ImageGatherer:
    """Orchestrates image search, download, and manifest generation."""

    def __init__(
        self,
        output_dir: str = 'research_output',
        debug_mode: bool = False,
        min_image_size: int = DEFAULT_MIN_DIMENSION,
    ):
        self.output_dir = output_dir
        self.debug_mode = debug_mode
        self.min_image_size = min_image_size
        self.engine_loader = ImageEngineLoader(debug_mode=debug_mode)
        self.downloader = ImageDownloader(output_dir=output_dir, min_dimension=min_image_size)
        self._seen_urls: set = set()

    def gather(self, keywords: List[str]):
        """
        Full pipeline:
        1. Load image engines.
        2. Search all engines in parallel for each keyword.
        3. Download and validate each unique image.
        4. Log summary.
        """
        engines = self.engine_loader.load_engines()
        if not engines:
            logger.error('No image engines loaded!')
            return

        size_note = (
            f'(min {self.min_image_size}px)' if self.min_image_size > 0 else '(all sizes)'
        )
        logger.info(f'Image gathering started — {len(keywords)} keyword(s), {size_note}')

        # Collect all unique image URLs across keywords
        all_records: List[ImageRecord] = []

        for idx, keyword in enumerate(keywords, 1):
            logger.info(f'[{idx}/{len(keywords)}] Searching images: {repr(keyword)}')
            urls = self.engine_loader.search_all(keyword)
            for url in urls:
                if url not in self._seen_urls:
                    self._seen_urls.add(url)
                    all_records.append(ImageRecord(image_url=url))

        logger.info(f'Total unique image URLs discovered: {len(all_records)}')

        if not all_records:
            logger.warning('No image URLs found — nothing to download')
            return

        # Download
        success = 0
        for i, record in enumerate(all_records, 1):
            logger.info(f'[{i}/{len(all_records)}] Downloading: {record.image_url}')
            result = self.downloader.download(record, index=i)
            if result:
                success += 1

        # Summary
        logger.info('=' * 60)
        logger.info(f'Images: {success}/{len(all_records)} downloaded successfully')
        if success > 0:
            logger.info(f'Manifest: {self.downloader.manifest_path}')
            logger.info(f'Directory: {self.downloader.download_dir}')
        if os.path.exists(self.downloader.failed_path):
            failed_count = sum(1 for _ in open(self.downloader.failed_path, encoding='utf-8'))
            if failed_count:
                logger.info(f'Failed: {failed_count} URLs saved to {self.downloader.failed_path}')


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Image Gatherer — search and download presentation-quality images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python image_gatherer.py -k "F5 BIG-IP architecture" -o research_output
  python image_gatherer.py -k "network packet flow" -o out --min-size 0
  python image_gatherer.py -l keywords.txt -o out --min-size 150
        """
    )
    parser.add_argument('-k', '--keyword', dest='keyword', nargs='+',
                        help='Keyword(s) to search images for')
    parser.add_argument('-l', '--keyword-list', dest='keyword_list',
                        help='File with keywords (one per line)')
    parser.add_argument('-o', '--output', dest='output_dir', default='research_output',
                        help='Output directory (default: research_output)')
    parser.add_argument('--min-size', dest='min_size', type=int, default=DEFAULT_MIN_DIMENSION,
                        help=f'Minimum image dimension in pixels (default: {DEFAULT_MIN_DIMENSION}). Use 0 for all.')
    parser.add_argument('-d', '--debug', dest='debug_mode', action='store_true',
                        help='Enable debug logging')

    args = parser.parse_args()

    if not any([args.keyword, args.keyword_list]):
        parser.print_help()
        sys.exit(1)

    from logging import DEBUG as LOG_DEBUG
    if args.debug_mode:
        logger.setLevel(LOG_DEBUG)

    keywords = []
    if args.keyword:
        keywords = [' '.join(args.keyword)]
    elif args.keyword_list:
        if not os.path.exists(args.keyword_list):
            logger.error(f'Keyword list not found: {args.keyword_list}')
            sys.exit(1)
        with open(args.keyword_list, 'r', encoding='utf-8-sig') as f:
            keywords = [
                line.strip() for line in f
                if line.strip() and not line.lstrip().startswith('#')
            ]

    gatherer = ImageGatherer(
        output_dir=args.output_dir,
        debug_mode=args.debug_mode,
        min_image_size=args.min_size,
    )
    gatherer.gather(keywords)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('\nInterrupted by user')
        sys.exit(0)
    except Exception as e:
        logger.error(f'Fatal error: {e}', exc_info=True)
        sys.exit(1)
