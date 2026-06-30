import re
import json
import sys
import os
from logging import DEBUG
from urllib.parse import urlencode, urljoin, quote

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libs'))

from helper import setup_logger, validate_url, random_agent
from fetch import FetchRequest
from html_parser import NativeHTMLParser

logger = setup_logger(name='GoogleImages')

MAX_PAGES = 2

# Desktop Chrome UA for more complete page rendering
_CHROME_UA = (
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/122.0.0.0 Safari/537.36'
)


class GoogleImages:
    base_url = 'https://www.google.com'

    def __init__(self, debug=False):
        self.debug = debug
        self.fetch = FetchRequest()
        if self.debug:
            logger.setLevel(DEBUG)

    def search(self, keyword: str):
        url = self.build_query(keyword)
        return self.search_run(url)

    def build_query(self, keyword: str) -> str:
        params = {
            'q': keyword,
            'tbm': 'isch',
            'safe': 'off',
            'hl': 'en',
            'gl': 'us',
        }
        return f'{self.base_url}/search?{urlencode(params, quote_via=quote)}'

    def search_run(self, start_url: str):
        results = []
        seen = set()
        url = start_url
        page = 0

        while url and page < MAX_PAGES:
            headers = {
                'User-Agent': _CHROME_UA,
                'Referer': self.base_url,
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            }
            html = self.fetch.get(url, headers=headers)
            if not html:
                break

            # Guard: detect captcha / block page
            if self._is_blocked(html):
                logger.warning('GoogleImages: blocked by Google (captcha/rate-limit), stopping')
                break

            urls = self.get_image_urls(html)
            if not urls:
                logger.debug(f'GoogleImages page {page + 1}: no URLs extracted')
                break

            added = 0
            for img_url in urls:
                if img_url not in seen:
                    seen.add(img_url)
                    results.append(img_url)
                    added += 1

            logger.debug(f'GoogleImages page {page + 1}: +{added} URLs')

            next_url = self.get_next_page(html, url)
            if next_url and next_url != url:
                url = next_url
            else:
                break
            page += 1

        logger.info(f'GoogleImages: {len(results)} image URLs found')
        return results

    def get_image_urls(self, html: str):
        results = []

        # Primary: "ou":"url" pattern in Google's embedded JSON data
        for m in re.finditer(r'"ou"\s*:\s*"(https?://[^"]+)"', html):
            valid = validate_url(m.group(1))
            if valid and valid not in results:
                results.append(valid)

        # Fallback: data-src on img elements (thumbnails only, lower quality)
        if not results:
            img_tags = NativeHTMLParser.find_by_attr(html, 'img', 'data-src', r'https?://')
            for tag in img_tags:
                m = re.search(r'data-src\s*=\s*"([^"]+)"', tag, re.I)
                if m:
                    valid = validate_url(m.group(1))
                    if valid and valid not in results:
                        results.append(valid)

        return list(dict.fromkeys(results))

    def get_next_page(self, html: str, current_url: str):
        # Google Images "More results" button — look for a link with tbm=isch and start= param
        matches = NativeHTMLParser.find_by_attr(html, 'a', 'href', r'/search\?.*tbm=isch.*start=')
        pattern_href = r'href\s*=\s*(?:"([^"]+)"|\'([^\']+)\')'

        for tag in matches:
            m = re.search(pattern_href, tag, re.I)
            if m:
                path = m.group(1) or m.group(2)
                if path:
                    full = urljoin(self.base_url, path)
                    valid = validate_url(full)
                    if valid and valid != current_url:
                        return valid

        return None

    @staticmethod
    def _is_blocked(html: str) -> bool:
        blocked_signals = ['recaptcha', 'detected unusual traffic', 'please prove']
        lower = html.lower()
        return any(sig in lower for sig in blocked_signals)


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('-k', '--keyword', required=True)
    p.add_argument('-d', '--debug', action='store_true')
    args = p.parse_args()

    eng = GoogleImages(debug=args.debug)
    res = eng.search(args.keyword)
    print(json.dumps(res, indent=2))
