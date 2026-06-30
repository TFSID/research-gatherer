"""
debug_google.py — Standalone debug script for google.py parsing logic

Menguji method get_links() dan get_next_page() dengan sample HTML
tanpa dependensi proyek (FetchRequest, NativeHTMLParser, dll).

Usage:
    python debug_google.py
"""

import re
from urllib.parse import urljoin, parse_qs

# ──────────────────────────────────────────────
# Sample HTML — tiruan Google Search hasil parsing
# ──────────────────────────────────────────────

SAMPLE_HTML_FULL = """<!DOCTYPE html>
<html>
<body>
<div id="search">
<div class="g">
<h3><a href="/url?q=https://www.example.com/page1&sa=U&ved=2ahUKEwj48sz10pmHAxWUk1YBHbtTAfgQFnoECAkQAw"
data-ved="2ahUKEwj48sz10pmHAxWUk1YBHbtTAfgQFnoECAkQAw">Example Page 1</a></h3>
</div>
<div class="g">
<h3><a href="/url?q=https://en.wikipedia.org/wiki/Python_(programming_language)&sa=U&ved=2ahUKEwj48sz10pmHAxW"
data-ved="2ahUKEwj48sz10pmHAxW">Python Wiki</a></h3>
</div>
<div class="g">
<h3><a href="https://direct-link.org/docs/guide"
data-ved="2ahUKEwj48sz10pmHAxWUk1YBHbtTAfgQFnoECAkQAw">Direct Link</a></h3>
</div>
<div class="g">
<h3><a href="/url?q=https://webcache.googleusercontent.com/search%3Fq%3Dcache%3Ahttps%253A%252F%252Fgithub.com%252Fuser%252Frepo%252B%2526cd%253D1%2526hl%253Den%2526ct%253Dclnk%2526gl%253Dus&sa=U&ved=2ahUKEwj48sz10pmHAxWUk1YBHbtTAfgQFnoECAkQAw"
data-ved="2ahUKEwj48sz10pmHAxWUk1YBHbtTAfgQFnoECAkQAw">Cache Link (encoded, won't match regex)</a></h3>
</div>
<div class="g">
<h3><a data-ved="2ahUKEwj48sz10pmHAxWUk1YBHbtTAfgQFnoECAkQAw"
href="http://webcache.googleusercontent.com/search?q=cache:https://old-site.org/archive+&cd=2&hl=en&ct=clnk&gl=us">Old Site Cache</a></h3>
</div>
<div class="g">
<h3><a href="/url?q=https://blog.example.com/post&sa=U&ved=2ahUKEwj48sz10pmHAxWUk1YBHbtTAfgQFnoECAkQAw"
data-ved="2ahUKEwj48sz10pmHAxWUk1YBHbtTAfgQFnoECAkQAw">Blog Post</a></h3>
</div>
</div>
</body>
</html>"""

SAMPLE_HTML_NEXT = """<!DOCTYPE html>
<html>
<body>
<div id="search">
<div class="g">...</div>
<div class="g">...</div>
<div id="nav">
<table class="AaVjTc" style="...">
<tr>
<td class="d6cvqb"><a href="/search?q=test+keyword&start=0" class="fl">1</a></td>
<td class="d6cvqb"><a href="/search?q=test+keyword&start=10" class="fl">2</a></td>
<td class="d6cvqb"><a href="/search?q=test+keyword&start=20" class="fl">3</a></td>
<td class="d6cvqb"><a href="/search?q=test+keyword&start=30" class="fl">4</a></td>
<td class="YyVfkd"><span class="SJajHc" style="...">...</span></td>
<td class="d6cvqb">
<a href="/search?q=test+keyword&start=10"
   id="pnnext"
   class="nBDE1b G5eFlf"><span class="oeN90d">Next</span></a>
</td>
</tr>
</table>
</div>
</div>
</body>
</html>"""

SAMPLE_HTML_NO_NEXT = """<!DOCTYPE html>
<html><body><div id="search"><div class="g">...</div></div></body></html>"""

SAMPLE_HTML_EMPTY = ""

SAMPLE_HTML_NO_LINKS = """<!DOCTYPE html>
<html><body><p>No results found for your query.</p></body></html>"""

# ──────────────────────────────────────────────
# Debug implementations (standalone)
# ──────────────────────────────────────────────


def debug_find_by_attr(html, tag, attr, value_regex):
    """Replikasi NativeHTMLParser.find_by_attr() via regex.
    Dua langkah: (1) cari semua opening tag <tag ...>,
    (2) filter yang memiliki attr dgn value cocok.
    """
    result = []
    # Step 1: semua <tag ...> opening tag (bisa multi-line)
    tag_pattern = rf'<{re.escape(tag)}\s[^>]*?>'
    for m in re.finditer(tag_pattern, html, re.I | re.S):
        tag_html = m.group(0)
        # Step 2: cek apakah attr="value" cocok
        attr_pattern = rf'\b{re.escape(attr)}\s*=\s*(["\'])(?:{value_regex})\1'
        if re.search(attr_pattern, tag_html, re.I):
            result.append(tag_html)
    return result


def debug_find_href(tag_html):
    """Replikasi regex patern_href dari google.py.
    Extract href value dari tag HTML.
    groups: (full_quote, double_quoted_val, single_quoted_val)
    """
    pattern = r'href[\s=]+((?:")(.*?)(?:")|(?:\')(.*?)(?:\'))'
    return re.search(pattern, tag_html, re.I)


def debug_validate_url(url):
    """Versi sederhana validate_url.
    1) Jika direct http/https URL, return as-is.
    2) Jika Google redirect (/url?q=URL&...), extract q param.
    """
    if not url:
        return ''
    url = url.strip()

    # Langsung valid http/https
    if url.startswith('http://') or url.startswith('https://'):
        return url

    # Google redirect pattern: /url?q=https://example.com&sa=U&ved=...
    if url.startswith('/url?'):
        qs = url.split('?', 1)[1]
        params = parse_qs(qs)
        if 'q' in params:
            q_val = params['q'][0]
            if q_val.startswith('http://') or q_val.startswith('https://'):
                print('      [validate_url] extracted q= from /url?: {}'.format(q_val))
                return q_val

    return ''


def debug_get_links(html):
    """Replikasi Google.get_links() — trace tiap step."""
    print('-' * 60)
    print('DEBUG: get_links()')
    print('-' * 60)

    result = []
    if not html:
        print('[SKIP] html kosong')
        return result

    # Step 1: find <a data-ved="...">
    print()
    print('[STEP 1] Mencari <a data-ved="..."> via debug_find_by_attr()...')
    matches = debug_find_by_attr(html, 'a', 'data-ved', r'.*')
    print('  Found {} match(es):'.format(len(matches)))
    for i, m in enumerate(matches):
        display = m[:120] + '...' if len(m) > 120 else m
        print('  [{}] {}'.format(i, display))

    if not matches:
        print('[RESULT] Tidak ada link ditemukan')
        return result

    # Step 2: regex href dari tiap tag
    pattern_href = r'href[\s=]+((?:")(.*?)(?:")|(?:\')(.*?)(?:\'))'
    pattern_cache = (
        r'(https?://)webcache\.googleusercontent\.[^\/]+/search\?q=cache:[^:]+:'
        r'(https?://)?(.+?)(\+?(&cd=[^&]+)(&hl=[^&]+)?(&ct=[^&]+)?(&gl=[^&]+)?.*)'
    )
    base_url = 'https://www.google.com'

    print()
    print('[STEP 2] Extracting href dari tiap match via regex:')
    for i, match in enumerate(matches):
        print()
        print('  --- Match [{}] ---'.format(i))
        display = match[:150] + '...' if len(match) > 150 else match
        print('  Raw: {}'.format(display))

        href = re.search(pattern_href, match, re.I)
        if href and len(href.groups()) >= 3:
            raw_val = href.group(3) or href.group(2)
            print('  patern_href match: YES')
            print('    group(0): {}'.format(href.group(0)))
            print('    group(1): {}'.format(href.group(1)))
            g2 = href.group(2)
            print('    group(2): {}...'.format(g2[:80] if g2 else None))
            g3 = href.group(3)
            print('    group(3): {}...'.format(g3[:80] if g3 else None))
            print('    raw href val (group(3) or group(2)): {}'.format(raw_val))

            # validate_url
            valid_url = debug_validate_url(raw_val)
            print('    validate_url(): {}'.format(valid_url))

            if valid_url:
                # Check Google Cache pattern
                cache_link = re.search(pattern_cache, valid_url, re.I)
                if cache_link:
                    final = '{}{}'.format(cache_link.group(1), cache_link.group(3))
                    print('    -> GOOGLE CACHE detected!')
                    print('      group(1) scheme: {}'.format(cache_link.group(1)))
                    print('      group(2) optional http: {}'.format(cache_link.group(2)))
                    print('      group(3) actual domain+path: {}'.format(cache_link.group(3)))
                    print('      group(4) trailing: {}'.format(cache_link.group(4)))
                    print('    -> FINAL CLEAN URL: {}'.format(final))
                    result.append(final)
                else:
                    print('    -> NOT a cache link')
                    print('    -> FINAL URL: {}'.format(valid_url))
                    result.append(valid_url)
            else:
                print('    -> validate_url() returned empty - not a valid HTTP URL')
        else:
            print('  patern_href match: NO')
            if href:
                print('    groups count: {}'.format(len(href.groups())))
            else:
                print('    href regex returned None')

    # dedup
    old_count = len(result)
    result = list(dict.fromkeys(result))
    if len(result) < old_count:
        print()
        print('[INFO] Duplicates removed: {}'.format(old_count - len(result)))

    print()
    print('[RESULT] get_links() returned {} link(s):'.format(len(result)))
    for j, link in enumerate(result):
        print('  [{}] {}'.format(j, link))

    return result


def debug_get_next_page(html):
    """Replikasi Google.get_next_page() — trace tiap step."""
    print()
    print('-' * 60)
    print('DEBUG: get_next_page()')
    print('-' * 60)

    next_page = ''
    if not html:
        print('[SKIP] html kosong')
        return next_page

    base_url = 'https://www.google.com'

    # Step 1: find <a id="pnnext">
    print()
    print('[STEP 1] Mencari <a id="pnnext"> via debug_find_by_attr()...')
    matches = debug_find_by_attr(html, 'a', 'id', r'pnnext')
    print('  Found {} match(es):'.format(len(matches)))
    for i, m in enumerate(matches):
        print('  [{}] {}'.format(i, m))

    if not matches:
        print('[RESULT] Tidak ada link next page - return empty string')
        return next_page

    # Step 2: regex href dari match pertama
    pattern_href = r'href[\s=]+((?:")(.*?)(?:")|(?:\')(.*?)(?:\'))'
    print()
    print('[STEP 2] Extract href dari match[0]:')
    print('  Match[0]: {}'.format(matches[0]))

    href = re.search(pattern_href, matches[0], re.I)
    if href and len(href.groups()) >= 3:
        path = href.group(3) or href.group(2)
        print('  patern_href match: YES')
        print('    group(2): {}'.format(href.group(2)))
        print('    group(3): {}'.format(href.group(3)))
        print('    raw path: {}'.format(path))
        next_page = debug_validate_url(urljoin(base_url, path))
        print('    urljoin({}, {}) = {}'.format(base_url, path, next_page))
    else:
        print('  patern_href match: NO')
        if href:
            print('    groups count: {} (need >=3)'.format(len(href.groups())))

    print()
    print('[RESULT] get_next_page() = "{}"'.format(next_page))
    return next_page


# ──────────────────────────────────────────────
# Test runner
# ──────────────────────────────────────────────


def run_tests():
    passed = 0
    failed = 0
    total_links_expected = 6  # dari SAMPLE_HTML_FULL: 6 <a data-ved="...">
    total_cache_expected = 1  # hanya 1 dari 2 cache links yg match regex (satunya URL-encoded)

    # -- Test 1: get_links() --
    print()
    print('=' * 60)
    print('TEST 1: get_links() - Full sample HTML')
    print('=' * 60)
    links = debug_get_links(SAMPLE_HTML_FULL)
    if len(links) == total_links_expected:
        print()
        print('[PASS] Expected {} links, got {}'.format(total_links_expected, len(links)))
        passed += 1
    else:
        print()
        print('[FAIL] Expected {} links, got {}'.format(total_links_expected, len(links)))
        failed += 1

    # -- Test 2: get_links() with empty HTML --
    print()
    print('=' * 60)
    print('TEST 2: get_links() - Empty HTML')
    print('=' * 60)
    empty_links = debug_get_links(SAMPLE_HTML_EMPTY)
    if len(empty_links) == 0:
        print()
        print('[PASS] Expected 0 links, got {}'.format(len(empty_links)))
        passed += 1
    else:
        print()
        print('[FAIL] Expected 0 links, got {}'.format(len(empty_links)))
        failed += 1

    # -- Test 3: get_links() with no result links --
    print()
    print('=' * 60)
    print('TEST 3: get_links() - No links HTML')
    print('=' * 60)
    no_links = debug_get_links(SAMPLE_HTML_NO_LINKS)
    if len(no_links) == 0:
        print()
        print('[PASS] Expected 0 links, got {}'.format(len(no_links)))
        passed += 1
    else:
        print()
        print('[FAIL] Expected 0 links, got {}'.format(len(no_links)))
        failed += 1

    # -- Test 4: get_next_page() with pnnext --
    print()
    print('=' * 60)
    print('TEST 4: get_next_page() - With pnnext link')
    print('=' * 60)
    next_url = debug_get_next_page(SAMPLE_HTML_NEXT)
    expected_next = 'https://www.google.com/search?q=test+keyword&start=10'
    if next_url == expected_next:
        print()
        print('[PASS] Expected "{}"'.format(expected_next))
        passed += 1
    else:
        print()
        print('[FAIL] Expected "{}"'.format(expected_next))
        print('         Got      "{}"'.format(next_url))
        failed += 1

    # -- Test 5: get_next_page() with no pnnext --
    print()
    print('=' * 60)
    print('TEST 5: get_next_page() - Without pnnext link')
    print('=' * 60)
    no_next = debug_get_next_page(SAMPLE_HTML_NO_NEXT)
    if no_next == '':
        print()
        print('[PASS] Expected empty string, got empty')
        passed += 1
    else:
        print()
        print('[FAIL] Expected empty string, got "{}"'.format(no_next))
        failed += 1

    # -- Test 6: get_next_page() with empty HTML --
    print()
    print('=' * 60)
    print('TEST 6: get_next_page() - Empty HTML')
    print('=' * 60)
    empty_next = debug_get_next_page(SAMPLE_HTML_EMPTY)
    if empty_next == '':
        print()
        print('[PASS] Expected empty string, got empty')
        passed += 1
    else:
        print()
        print('[FAIL] Expected empty string, got "{}"'.format(empty_next))
        failed += 1

    # -- Test 7: Google Cache URL extraction --
    print()
    print('=' * 60)
    print('TEST 7: Cache URL extraction count')
    print('=' * 60)
    cache_count = sum(1 for l in links if 'cache' in l)
    print('  Cache links found in get_links() result: {}'.format(cache_count))
    if cache_count == total_cache_expected:
        print('  [PASS] Expected {} cache links'.format(total_cache_expected))
        passed += 1
    else:
        print('  [FAIL] Expected {} cache links, got {}'.format(total_cache_expected, cache_count))
        failed += 1

    # -- Test 8: Duplikasi --
    print()
    print('=' * 60)
    print('TEST 8: Duplikasi removal')
    print('=' * 60)
    dedup_test = ['http://a.com', 'http://b.com', 'http://a.com', 'http://c.com']
    dedup_result = list(dict.fromkeys(dedup_test))
    print('  Before: {}'.format(dedup_test))
    print('  After:  {}'.format(dedup_result))
    if len(dedup_result) == 3:
        print('  [PASS] Dedup berhasil (3 unique from 4)')
        passed += 1
    else:
        print('  [FAIL] Expected 3, got {}'.format(len(dedup_result)))
        failed += 1

    # -- Summary --
    print()
    print('=' * 60)
    print('SUMMARY: {} passed, {} failed, {} total'.format(passed, failed, passed + failed))
    print('=' * 60)

    return failed == 0


def print_pattern_reference():
    """Print regex pattern yang digunakan google.py untuk referensi."""
    print()
    print('=' * 60)
    print('REGEX PATTERN REFERENCE (from google.py)')
    print('=' * 60)
    patterns = {
        'patern_href': r'href[\s=]+((?:")(.*?)(?:")|(?:\')(.*?)(?:\'))',
        'patern_google_cache': (
            r'(https?://)webcache\.googleusercontent\.[^\/]+/search\?q=cache:[^:]+:'
            r'(https?://)?(.+?)(\+?(&cd=[^&]+)(&hl=[^&]+)?(&ct=[^&]+)?(&gl=[^&]+)?.*)'
        ),
        'find_by_attr (data-ved)': r'<a\s[^>]*?\bdata-ved\s*=\s*["\'](?:.*)["\'][^>]*?>',
        'find_by_attr (id=pnnext)': r'<a\s[^>]*?\bid\s*=\s*["\']pnnext["\'][^>]*?>',
    }
    for name, pat in patterns.items():
        print()
        print('  {}:'.format(name))
        print('    {}'.format(pat))


if __name__ == '__main__':
    import sys

    mode = 'all'
    if len(sys.argv) > 1:
        mode = sys.argv[1]

    if mode in ('links', 'all'):
        debug_get_links(SAMPLE_HTML_FULL)

    if mode in ('next', 'all'):
        debug_get_next_page(SAMPLE_HTML_NEXT)
        debug_get_next_page(SAMPLE_HTML_NO_NEXT)

    if mode in ('test', 'all'):
        run_tests()

    if mode == 'all':
        print_pattern_reference()

    print()
