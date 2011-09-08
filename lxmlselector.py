"""
Lxml selector
Provides both XPath and CSS Selection.
Can use html5lib and BeautifulSoup.

Provided by Steeve Morin <steeve.morin@gmail.com>

See documentation in docs/topics/selectors.rst
"""


from lxml import etree
from lxml.cssselect import CSSSelector as lxml_CSSSelector
from scrapy.http import TextResponse
from scrapy.utils.python import flatten, unicode_to_str
from scrapy.utils.misc import extract_regex
from scrapy.utils.trackref import object_ref

__all__ = ['HtmlXPathSelector', 'XmlXPathSelector', 'LxmlSelector',
    'LxmlSelectorList']

class LxmlSelector(object_ref):

    __slots__ = [ 'doc', 'xmlNode', 'expr', '__weakref__', "namespaces" ]

    def __init__(self, response=None, text=None, node=None, parent=None, expr=None,
                 use_html5lib=False, use_BeautifulSoup=False, namespaces=None):
        if parent:
            self.doc = parent.doc
            self.xmlNode = node
        elif response:
            self.xmlNode = self._lxml_parse_document(response.body, use_html5lib,
                                                     use_BeautifulSoup)
            self.doc = self.xmlNode.getroottree()
        elif text:
            response = TextResponse(url='about:blank', body=unicode_to_str(text),
                                    encoding='utf-8')
            self.xmlNode = self._lxml_parse_document(response.body, use_html5lib,
                                                     use_BeautifulSoup)
            self.doc = self.xmlNode.getroottree()
        self.expr = expr
        self.namespaces = namespaces or {}
        
    def _lxml_parse_document(self, body, use_html5lib=False,
                             use_BeautifulSoup=False):
        if use_html5lib:
            from lxml.html import html5parser
            return html5parser.fromstring(body)
        elif use_BeautifulSoup:
            from lxml.html import soupparser
            return soupparser.fromstring(body)
        else:
            for parser in [ etree.XML, etree.HTML ]:
                try:
                    return (parser(body))
                except:
                    pass

    def xpath(self, xpath):
        """Perform the given XPath query on the current XPathSelector and
        return a XPathSelectorList of the result"""
        return self._make_select_results(self.xmlNode.xpath(xpath, namespaces=self.namespaces), expr=xpath, namespaces=self.namespaces)

    def css(self, css):
        return self._make_select_results(lxml_CSSSelector(css)(self.xmlNode), expr=css, namespaces=self.namespaces)

    def _make_select_results(self, result, expr, namespaces):
        if hasattr(result, '__iter__'):
            return LxmlSelectorList([ type(self)(node=node, parent=self,
                expr=expr, namespaces=self.namespaces) for node in result ])
        else:
            return LxmlSelectorList([ type(self)(node=result,
                parent=self, expr=expr, namespaces=self.namespaces) ])

    def re(self, regex):
        """Return a list of unicode strings by applying the regex over all
        current XPath selections, and flattening the results"""
        return extract_regex(regex, self.extract(), 'utf-8')

    def extract(self):
        """Return a unicode string of the content referenced by the XPathSelector"""
        if isinstance(self.xmlNode, etree._Element):
            return unicode(etree.tostring(self.xmlNode, encoding='utf-8'), 'utf-8', errors='ignore')
        try:
            text = unicode(self.xmlNode, 'utf-8', errors='ignore')
        except TypeError:  # catched when self.xmlNode is a float - see tests
            text = unicode(self.xmlNode)
        return text

    def extract_unquoted(self):
        """Get unescaped contents from the text node (no entities, no CDATA)"""
        if self.select('self::text()'):
            return unicode(self.xmlNode.getContent(), 'utf-8', errors='ignore')
        else:
            return u''

    def register_namespace(self, prefix, uri):
        """Register namespace so that it can be used in XPath queries"""
        self.doc.xpathContext.xpathRegisterNs(prefix, uri)

    def attrib(self, name):
        return self._make_select_results([self.xmlNode.attrib[name]], expr="%s/@%s()" % (self.expr, name), namespaces=self.namespaces)[0]

    def text(self):
        return self._make_select_results(self.xmlNode.xpath("text()"), expr="%s/text()" % self.expr, namespaces=self.namespaces)

    def __nonzero__(self):
        return bool(self.extract())

    def __str__(self):
        return "<%s (%s) xpath=%s>" % (type(self).__name__, getattr(self.xmlNode,
            'name', type(self.xmlNode).__name__), self.expr)

    __repr__ = __str__


class LxmlSelectorList(list):
    """List of XPathSelector objects"""

    def __getslice__(self, i, j):
        return LxmlSelectorList(list.__getslice__(self, i, j))

    def xpath(self, expr):
        """Perform the given XPath query on each XPathSelector of the list and
        return a new (flattened) XPathSelectorList of the results"""
        return LxmlSelectorList(flatten([ x.xpath(expr) for x in self ]))

    def css(self, expr):
        """Perform the given XPath query on each XPathSelector of the list and
        return a new (flattened) XPathSelectorList of the results"""
        return LxmlSelectorList(flatten([ x.css(expr) for x in self ]))

    def re(self, regex):
        """Perform the re() method on each XPathSelector of the list, and
        return the result as a flattened list of unicode strings"""
        return flatten([ x.re(regex) for x in self ])

    def attrib(self, name):
        """Return a list of unicode strings with the attributes referenced by each
        XPathSelector of the list"""
        return LxmlSelectorList([ x.attrib(name) if isinstance(x, LxmlSelector) else x for x in self])

    def text(self):
        """Return a list of unicode strings with the content text referenced by each
        XPathSelector of the list"""
        return LxmlSelectorList(flatten([ x.text() if isinstance(x, LxmlSelector) else x for x in self]))

    def extract(self):
        """Return a list of unicode strings with the content referenced by each
        XPathSelector of the list"""
        return [ x.extract() if isinstance(x, LxmlSelector) else x for x in self]

    def extract_unquoted(self):
        return [ x.extract_unquoted() if isinstance(x, LxmlSelector) else x for x in self]
