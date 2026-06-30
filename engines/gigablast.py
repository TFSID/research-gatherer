import re
from logging import DEBUG
from urllib.parse import urljoin
from utils.blacklist import is_blacklisted
from utils.helper import setup_logger, validate_url
from libs.html_parser import NativeHTMLParser
from libs.fetch import FetchRequest

logger = setup_logger(name='Gigablast')


class Gigablast:
    base_url = 'https://gigablast.org'

    def __init__(self, debug=False):
        self.debug = debug
        self.fetch = FetchRequest()
        self.query = {}
        self.filtering = True

        if self.debug:
            logger.setLevel(DEBUG)

    def search(self, keyword):
        self.query.update({'s': str(keyword)})
        search_url = urljoin(self.base_url, 'web')
        return self.search_run(search_url, method='POST')

    def search_run(self, url, method='GET'):
        result = []
        if not url:
            return result

        duplicate_page = 0
        empty_page = 0
        headers = {'Referer': self.base_url}
        page = 1
        while True:
            if self.debug:
                logger.debug('Page: %s %s' % (page, url))
            else:
                logger.info('Page: %s' % page)

            if method == 'POST':
                html = self.fetch.post(url, data=self.query, headers=headers)
            else:
                html = self.fetch.get(url, headers=headers)

            links = self.get_links(html)

            if not links:
                empty_page += 1
                if page > 1:
                    break
            else:
                duplicate = True
                for link in links:
                    if self.filtering:
                        if is_blacklisted(link):
                            logger.debug('[BLACKLIST] %s' % link)
                            continue

                    if link not in result:
                        duplicate = False
                        logger.info(link)
                        result.append(link)
                    else:
                        logger.debug('[EXIST] %s' % link)

                if duplicate:
                    duplicate_page += 1

            if duplicate_page >= 3:
                break

            if empty_page >= 2:
                break

            next_page = self.get_next_page(html)
            if next_page and next_page != url:
                headers.update({'Referer': url})
                url = next_page
                method = 'GET' # Next page links are usually GET requests
            else:
                break
            page += 1

        result = list(dict.fromkeys(result))
        logger.info('Total links: %d' % len(result))

        return result

    def get_links(self, html=None):
        result = []
        if not html:
            return result

        _parser = NativeHTMLParser()
        _parser.feed(str(html))
        _parser.close()

        if _parser.root is None:
            return result

        # Find all divs with class "text-result"
        results = _parser.root.findall('.//div[@class="text-result"]')
        for res in results:
            link = res.find('.//a[@class="hover"]')
            if link is not None:
                _href = link.get('href')
                valid_url = validate_url(_href)
                if valid_url:
                    if not re.search(r'^(.*\.)?gigablast\.org', valid_url, re.I):
                        result.append(valid_url)

        if result:
            result = list(dict.fromkeys(result))

        return result

    def get_next_page(self, html):
        next_page = ''
        if not html:
            return next_page

        _parser = NativeHTMLParser()
        _parser.feed(str(html))
        _parser.close()

        if _parser.root is None:
            return next_page

        # Find the next page link
        next_link = _parser.root.find('.//a[@class="next"]')
        if next_link is not None:
            next_href = next_link.get('href')
            if next_href:
                next_page = validate_url(urljoin(self.base_url, next_href))

        return next_page


if __name__ == '__main__':
    import sys
    import argparse
    import json
    try:
        parser = argparse.ArgumentParser(usage='%(prog)s [options]')
        # noinspection PyProtectedMember
        parser._optionals.title = 'Options'
        parser.add_argument('-k', '--keyword',
                            dest='keyword',
                            help='Keyword to search',
                            action='store')
        parser.add_argument('-s', '--save',
                            dest='save_output',
                            help='Save Output results',
                            action='store_true')
        parser.add_argument('-o', '--output',
                            dest='output_file',
                            help='Output results (default gigablast_results.txt)',
                            default='gigablast_results.txt',
                            action='store')

        args = parser.parse_args()
        if not args.keyword:
            parser.print_help()
            sys.exit('[!] Keyword required')

        eng = Gigablast()
        res = eng.search(args.keyword)

        if args.save_output:
            if res:
                for rlink in res:
                    with open(args.output_file, 'a', encoding='utf-8', errors='replace') as f:
                        try:
                            f.write('%s\n' % rlink)
                        except UnicodeEncodeError:
                            logger.error(rlink)
        else:
            print(json.dumps(res, indent=2, default=str))
    except KeyboardInterrupt:
        sys.exit('KeyboardInterrupt')
