import re
import json
import sys
import os
from logging import DEBUG
from urllib.parse import urlencode, unquote, urljoin

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libs'))

from helper import setup_logger, validate_url, random_agent
from fetch import FetchRequest
from html_parser import NativeHTMLParser

logger = setup_logger(name='YahooImages')

MAX_PAGES = 3


class YahooImages:
    base_url = 'https://images.search.yahoo.com'

    def __init__(self, debug=False):
        self.debug = debug
        self.fetch = FetchRequest()
        if self.debug:
            logger.setLevel(DEBUG)

    def search(self, keyword: str):
        url = self.build_query(keyword)
        return self.search_run(url)

    def build_query(self, keyword: str) -> str:
        params = {'p': keyword, 'fr': 'yfp-t', 'fr2': 'p%3As%2Cv%3Ai'}
        return f'{self.base_url}/search/images;_ylt=?{urlencode(params)}'

    def search_run(self, start_url: str):
        results = []
        seen = set()
        url = start_url
        page = 0

        while url and page < MAX_PAGES:
            headers = {
                'User-Agent': random_agent(),
                'Referer': self.base_url,
                'Accept-Language': 'en-US,en;q=0.9',
            }
            html = self.fetch.get(url, headers=headers)
            if not html:
                break

            urls = self.get_image_urls(html)
            added = 0
            for img_url in urls:
                if img_url not in seen:
                    seen.add(img_url)
                    results.append(img_url)
                    added += 1

            logger.debug(f'YahooImages page {page + 1}: +{added} URLs')

            if added == 0:
                break

            next_url = self.get_next_page(html)
            if next_url and next_url != url:
                url = next_url
            else:
                break
            page += 1

        logger.info(f'YahooImages: {len(results)} image URLs found')
        return results

    def get_image_urls(self, html: str):
        results = []

        # Primary: Yahoo redirect pattern /RU=<encoded-url>/RK=
        for m in re.finditer(r'/RU=(https?[^/]+)/RK=', html):
            raw = unquote(m.group(1))
            valid = validate_url(raw)
            if valid and valid not in results:
                results.append(valid)

        # Fallback: "iurl":"url" JSON fragment
        if not results:
            for m in re.finditer(r'"iurl"\s*:\s*"([^"]+)"', html):
                valid = validate_url(m.group(1))
                if valid and valid not in results:
                    results.append(valid)

        # Second fallback: data-src on img tags inside result containers
        if not results:
            img_tags = NativeHTMLParser.find_by_attr(html, 'img', 'data-src', r'https?://')
            for tag in img_tags:
                m = re.search(r'data-src\s*=\s*"([^"]+)"', tag, re.I)
                if m:
                    valid = validate_url(m.group(1))
                    if valid and valid not in results:
                        results.append(valid)

        return list(dict.fromkeys(results))

    def get_next_page(self, html: str):
        # Look for <a class="next"> or pagination link with "more" text
        matches = NativeHTMLParser.find_by_attr(html, 'a', 'class', r'next')
        pattern_href = r'href\s*=\s*(?:"([^"]+)"|\'([^\']+)\')'

        for tag in matches:
            m = re.search(pattern_href, tag, re.I)
            if m:
                path = m.group(1) or m.group(2)
                if path:
                    full = urljoin(self.base_url, path)
                    return validate_url(full)

        return None


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('-k', '--keyword', required=True)
    p.add_argument('-d', '--debug', action='store_true')
    args = p.parse_args()

    eng = YahooImages(debug=args.debug)
    res = eng.search(args.keyword)
    print(json.dumps(res, indent=2))
