import os
import gzip
import time
import random
import configparser
import hashlib
import http.cookiejar
import urllib.request
import urllib.parse
import urllib.error
import socket
from utils.helper import split_url, dir_exist, file_exist, random_agent, decode_bytes
from utils.static import config


def fetch_url(url, method='GET', headers=None, data=None, timeout=10, cookie_file=None):
    """
    Fetches a URL using urllib.request.urlopen with retry logic and specific error handling.
    """
    socket.setdefaulttimeout(10)

    if headers is None:
        headers = {}

    # Cookie handling
    cookie = None
    opener = None
    if cookie_file:
        if file_exist(cookie_file):
            cookie = http.cookiejar.MozillaCookieJar()
            cookie.load(cookie_file, ignore_discard=True, ignore_expires=True)
        else:
            cookie = http.cookiejar.MozillaCookieJar(cookie_file)

        handler = urllib.request.HTTPCookieProcessor(cookie)
        opener = urllib.request.build_opener(handler)
        urllib.request.install_opener(opener)

    req = urllib.request.Request(url, method=method)

    for k, v in headers.items():
        req.add_header(k, v)

    if data:
        if isinstance(data, dict):
            req.data = urllib.parse.urlencode(data).encode()
        elif isinstance(data, str):
            req.data = data.encode()
        elif isinstance(data, bytes):
            req.data = data

    retry_count = 0
    max_retries = 3

    while retry_count < max_retries:
        try:
            response = urllib.request.urlopen(req, timeout=timeout)

            if cookie and cookie_file:
                cookie.save(cookie_file, ignore_discard=True, ignore_expires=True)

            return response

        except (ConnectionResetError, urllib.error.URLError, socket.timeout) as e:
            retry_count += 1
            print(f"[!] Error fetching {url}: {e}. Retrying ({retry_count}/{max_retries})...")
        except Exception as e:
            print(f"[!] Unexpected error fetching {url}: {e}")
            break

    return None


class FetchRequest:
    def __init__(self, **kwargs):
        self.debug = kwargs.get('debug') or False
        self.user_agent = kwargs.get('user_agent') or random_agent()
        self.timeout = kwargs.get('timeout') or config.getint('DEFAULT', 'timeout')
        self.cookie_dir = kwargs.get('cookie_dir') or 'cookie'
        self.cookie_ext = kwargs.get('cookie_ext') or '_cookie'
        self.cookie_file = None
        self.cookie = None

        self.jitter_min = 1
        self.jitter_max = 5
        self._load_config()

    def _load_config(self):
        config = configparser.ConfigParser()
        config_path = 'config.ini'
        if os.path.exists(config_path):
            config.read(config_path)
            if 'settings' in config:
                try:
                    self.jitter_min = float(config.get('settings', 'jitter_min', fallback=1))
                    self.jitter_max = float(config.get('settings', 'jitter_max', fallback=5))
                except ValueError:
                    pass

    def set_cookie_file(self, url):
        cookieStr = self.cookie_file

        spliturl = split_url(url)
        if spliturl.get('url'):
            cookieStr = '%s%s' % (spliturl.get('scheme'), spliturl.get('domain'))

        # Fallback if cookieStr is still None to avoid AttributeError on encode
        if cookieStr is None:
            cookieStr = url

        cookieName = hashlib.md5(cookieStr.encode()).hexdigest()
        cookieFile = '%s%s' % (cookieName, self.cookie_ext)

        if file_exist(self.cookie_dir):
            os.remove(self.cookie_dir)

        if not dir_exist(self.cookie_dir):
            os.mkdir(self.cookie_dir)

        self.cookie_file = os.path.join(self.cookie_dir, cookieFile)

    def get(self, url, headers=None):
        response = self.request(url=url, method='GET', headers=headers)
        return self.get_response(response)

    def post(self, url, headers=None, data=None):
        response = self.request(url=url, method='POST', headers=headers, data=data)
        return self.get_response(response)

    def request(self, url, **kwargs):
        # Jitter delay
        if self.jitter_max > 0:
            sleep_time = random.uniform(self.jitter_min, self.jitter_max)
            if self.debug:
                print(f'[DEBUG] Sleeping for {sleep_time:.2f} seconds')
            time.sleep(sleep_time)

        method = kwargs.get('method') or 'GET'
        headers = kwargs.get('headers') or {}
        data = kwargs.get('data') or {}

        # Ensure User-Agent
        if not any(k.lower() == 'user-agent' for k in headers):
            if self.user_agent:
                headers['User-Agent'] = self.user_agent

        self.set_cookie_file(url)

        return fetch_url(
            url=url,
            method=method,
            headers=headers,
            data=data,
            timeout=self.timeout,
            cookie_file=self.cookie_file
        )

    @staticmethod
    def get_response(response):
        if response:
            try:
                content_encoding = response.getheader('Content-Encoding')
                if content_encoding and content_encoding.lower() == 'gzip':
                    result, _ = decode_bytes(gzip.decompress(response.read()))
                else:
                    result, _ = decode_bytes(response.read())

                return result
            except Exception as err:
                print('_response error', err)

        return
