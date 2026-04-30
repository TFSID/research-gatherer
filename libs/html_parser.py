import re
import html
from abc import ABC
from html.parser import HTMLParser
from xml.etree import ElementTree


class NativeHTMLParser(HTMLParser, ABC):
    """
    Python 3.x HTMLParser extension with ElementTree support.
    @see https://github.com/marmelo/python-htmlparser
    """

    def __init__(self):
        self.root = None
        self.tree = []
        HTMLParser.__init__(self)

    def feed(self, data):
        HTMLParser.feed(self, data)
        return self.root

    def handle_starttag(self, tag, attrs):
        if len(self.tree) == 0:
            element = ElementTree.Element(tag, dict(self.__filter_attrs(attrs)))
            self.tree.append(element)
            self.root = element
        else:
            element = ElementTree.SubElement(self.tree[-1], tag, dict(self.__filter_attrs(attrs)))
            self.tree.append(element)

    def handle_endtag(self, tag):
        self.tree.pop()

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)
        pass

    def handle_data(self, data):
        if self.tree:
            self.tree[-1].text = data

    def get_root_element(self):
        return self.root

    @staticmethod
    def __filter_attrs(attrs):
        return filter(lambda x: x[0] and x[1], attrs) if attrs else []

    @staticmethod
    def find_by_attr(html_content, tag, attr, value_regex):
        """
        Finds elements (opening tags) by attribute using regex on string HTML.
        Returns a list of matching opening tags strings.
        """
        results = []
        if not html_content:
            return results

        # 1. Find all opening tags
        # Naive regex assuming > is not in attribute values
        tag_pattern = re.compile(fr'<{tag}\b[^>]*>', re.IGNORECASE | re.DOTALL)

        # 2. Compile user regex
        val_matcher = re.compile(value_regex, re.IGNORECASE)

        # 3. Regex to extract attribute value
        attr_pattern = re.compile(fr'\b{attr}\s*=\s*(?:"([^"]*)"|\'([^\']*)\'|([^\s>]+))', re.IGNORECASE)

        for match in tag_pattern.finditer(str(html_content)):
            tag_str = match.group(0)
            attr_match = attr_pattern.search(tag_str)
            if attr_match:
                # Extract value from capturing groups
                val = attr_match.group(1) if attr_match.group(1) is not None else \
                      attr_match.group(2) if attr_match.group(2) is not None else \
                      attr_match.group(3)

                if val is not None and val_matcher.search(val):
                    results.append(tag_str)

        return results

    @staticmethod
    def get_text_content(html_content):
        """
        Extracts clean text from HTML content by stripping tags.
        """
        if not html_content:
            return ""
        s = str(html_content)
        # Remove script and style
        s = re.sub(r'<(script|style)[^>]*>.*?</\1>', '', s, flags=re.IGNORECASE | re.DOTALL)
        # Remove comments
        s = re.sub(r'<!--.*?-->', '', s, flags=re.DOTALL)
        # Remove tags
        s = re.sub(r'<[^>]+>', ' ', s)
        # Unescape
        s = html.unescape(s)
        # Normalize whitespace
        s = re.sub(r'\s+', ' ', s).strip()
        return s
