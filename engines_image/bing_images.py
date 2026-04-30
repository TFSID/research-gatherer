import re
import json
import sys
import os
import html as html_module
from logging import DEBUG
from urllib.parse import urlencode, urljoin

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libs'))

from helper import setup_logger, validate_url, random_agent
from fetch import FetchRequest
from html_parser import NativeHTMLParser

logger = setup_logger(name='BingImages')

MAX_PAGES = 3
PAGE_SIZE = 35


class BingImages:
    base_url = 'https://www.bing.com'

    def __init__(self, debug=False):
        self.debug = debug
        self.fetch = FetchRequest()
        if self.debug:
            logger.setLevel(DEBUG)

    def search(self, keyword: str):
        results = []
        seen = set()

        for page in range(MAX_PAGES):
            first = page * PAGE_SIZE + 1
            url = self.build_query(keyword, first)
            headers = {
                'User-Agent': random_agent(),
                'Referer': self.base_url,
                'Accept-Language': 'en-US,en;q=0.9',
            }
            html = self.fetch.get(url, headers=headers)
            if not html:
                break

            urls = self.get_image_urls(html)
            if not urls:
                break

            added = 0
            for img_url in urls:
                if img_url not in seen:
                    seen.add(img_url)
                    results.append(img_url)
                    added += 1

            logger.debug(f'BingImages page {page + 1}: +{added} URLs')

            if added == 0:
                break

        logger.info(f'BingImages: {len(results)} image URLs found')
        return results

    def build_query(self, keyword: str, first: int = 1) -> str:
        params = {
            'q': keyword,
            'form': 'HDRSC2',
            'first': str(first),
            'tsc': 'ImageHoverTitle',
        }
        return f'{self.base_url}/images/search?{urlencode(params)}'

    def get_image_urls(self, html: str):
        results = []

        # Find all <a class="iusc"> elements
        matches = NativeHTMLParser.find_by_attr(html, 'a', 'class', r'iusc')

        for tag in matches:
            img_url = self._extract_murl(tag)
            if img_url:
                valid = validate_url(img_url)
                if valid:
                    results.append(valid)

        # Fallback: direct regex on murl in case NativeHTMLParser misses encoded tags
        if not results:
            for m in re.finditer(r'"murl"\s*:\s*"(https?://[^"]+)"', html):
                valid = validate_url(m.group(1))
                if valid and valid not in results:
                    results.append(valid)

        return list(dict.fromkeys(results))

    @staticmethod
    def _extract_murl(tag: str):
        # Extract the m attribute value (JSON blob)
        m = re.search(r'\bm\s*=\s*"(\{[^"]*\})"', tag)
        if not m:
            # Try with single quotes
            m = re.search(r"\bm\s*=\s*'(\{[^']*\})'", tag)
        if not m:
            return None

        raw = html_module.unescape(m.group(1))

        try:
            data = json.loads(raw)
            return data.get('murl')
        except (json.JSONDecodeError, ValueError):
            pass

        # Fallback: regex extract murl from the raw string
        murl_m = re.search(r'"murl"\s*:\s*"([^"]+)"', raw)
        if murl_m:
            return murl_m.group(1)

        return None


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('-k', '--keyword', required=True)
    p.add_argument('-d', '--debug', action='store_true')
    args = p.parse_args()

    eng = BingImages(debug=args.debug)
    res = eng.search(args.keyword)
    print(json.dumps(res, indent=2))
