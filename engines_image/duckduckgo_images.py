import re
import json
import sys
import os
from logging import DEBUG
from urllib.parse import urlencode, quote_plus

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'utils'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'libs'))

from helper import setup_logger, validate_url, random_agent
from fetch import FetchRequest

logger = setup_logger(name='DuckDuckGoImages')

MAX_PAGES = 3


class DuckDuckGoImages:
    base_url = 'https://duckduckgo.com'
    api_url = 'https://duckduckgo.com/i.js'

    def __init__(self, debug=False):
        self.debug = debug
        self.fetch = FetchRequest()
        if self.debug:
            logger.setLevel(DEBUG)

    def search(self, keyword: str):
        vqd = self._get_vqd(keyword)
        if not vqd:
            logger.warning('DuckDuckGoImages: could not obtain vqd token')
            return []
        return self._fetch_images_api(keyword, vqd)

    def _get_vqd(self, keyword: str):
        url = f'{self.base_url}/?{urlencode({"q": keyword, "iax": "images", "ia": "images"})}'
        headers = {
            'User-Agent': random_agent(),
            'Referer': self.base_url,
        }
        html = self.fetch.get(url, headers=headers)
        if not html:
            return None

        # Primary pattern: vqd=<digits-dashes>
        m = re.search(r'vqd=([\d\-]+)', html)
        if m:
            return m.group(1)

        # Fallback: JSON-encoded "vqd":"token"
        m = re.search(r'"vqd"\s*:\s*"([^"]+)"', html)
        if m:
            return m.group(1)

        logger.debug('DuckDuckGoImages: vqd pattern not found in page')
        return None

    def _fetch_images_api(self, keyword: str, vqd: str):
        results = []
        seen = set()
        next_token = ''
        page = 0

        while page < MAX_PAGES:
            params = {
                'q': keyword,
                'vqd': vqd,
                'o': 'json',
                'p': '1',
                'u': 'bing',
                'f': ',,,',
                'l': 'en-us',
            }
            if next_token:
                params['s'] = next_token

            url = f'{self.api_url}?{urlencode(params)}'
            headers = {
                'User-Agent': random_agent(),
                'Referer': self.base_url,
                'Accept': 'application/json',
                'X-Requested-With': 'XMLHttpRequest',
            }

            html = self.fetch.get(url, headers=headers)
            if not html:
                break

            try:
                data = json.loads(html)
            except (json.JSONDecodeError, ValueError):
                logger.debug(f'DuckDuckGoImages: JSON parse failed on page {page + 1}')
                break

            page_results = data.get('results', [])
            if not page_results:
                break

            added = 0
            for item in page_results:
                img_url = item.get('image', '')
                if img_url and img_url not in seen:
                    valid = validate_url(img_url)
                    if valid:
                        seen.add(img_url)
                        results.append(img_url)
                        added += 1

            logger.debug(f'DuckDuckGoImages page {page + 1}: +{added} URLs')

            next_token = data.get('next', '')
            if not next_token:
                break
            page += 1

        logger.info(f'DuckDuckGoImages: {len(results)} image URLs found')
        return results


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('-k', '--keyword', required=True)
    p.add_argument('-d', '--debug', action='store_true')
    args = p.parse_args()

    eng = DuckDuckGoImages(debug=args.debug)
    res = eng.search(args.keyword)
    print(json.dumps(res, indent=2))
