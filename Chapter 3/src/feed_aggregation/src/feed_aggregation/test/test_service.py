import attr
import json
from lxml import html
from twisted.internet import defer
from twisted.trial.unittest import SynchronousTestCase
from treq.testing import StubTreq
from .. import FeedAggregation
from .._service import Feed, Channel, Item, FeedRetrieval
from klein import Klein
from lxml.builder import E
from lxml.etree import tostring
from hyperlink import URL
from xml.sax import SAXParseException

FEEDS = (
    Feed(u"http://feed-1.invalid/rss.xml",
         Channel(title="First feed", link="http://feed-1/",
                 items=(Item(title="First item", link="#first"),))),
    Feed(u"http://feed-2.invald/rss.xml",
         Channel(title="Second feed", link="http://feed-2/",
                 items=(Item(title="Second item", link="#second"),))),
)

class FeedAggregationTests(SynchronousTestCase):
    def setUp(self):
        service = StubFeed(
            {URL.from_text(feed._source).host.encode('ascii'): makeXML(feed)
             for feed in FEEDS})
        treq = StubTreq(service.resource())
        urls = [feed._source for feed in FEEDS]
        retriever = FeedRetrieval(treq)
        self.client = StubTreq(
            FeedAggregation(retriever.retrieve, urls).resource())
    @defer.inlineCallbacks
    def get(self, url):
        response = yield self.client.get(url)
        self.assertEqual(response.code, 200)
        content = yield response.content()
        defer.returnValue(content)
    def test_renderHTML(self):
        content = self.successResultOf(self.get("http://test.invalid/"))
        parsed = html.fromstring(content)
        self.assertEqual(parsed.xpath('/html/body/div/table/tr/th/a/text()'),
                         ["First feed", "Second feed"])
        self.assertEqual(parsed.xpath('/html/body/div/table/tr/th/a/@href'),
                         ["http://feed-1/", "http://feed-2/"])
        self.assertEqual(parsed.xpath('/html/body/div/table/tr/td/a/text()'),
                         ["First item", "Second item"])
        self.assertEqual(parsed.xpath('/html/body/div/table/tr/td/a/@href'),
                         ["#first", "#second"])
    def test_renderJSON(self):
        content = self.successResultOf(self.get("http://test.invalid/?json=true"))
        parsed = json.loads(content)
        self.assertEqual(
            parsed,
            {"feeds": [{"title": "First feed", "link": "http://feed-1/",
                        "items": [{"title": "First item", "link": "#first"}]},
                       {"title": "Second feed", "link": "http://feed-2/",
                        "items": [{"title": "Second item", "link": "#second"}]}]})


@attr.s
class StubFeed(object):
    _feeds = attr.ib()
    _app = Klein()
    def resource(self):
        return self._app.resource()
    @_app.route("/rss.xml")
    def returnXML(self, request):
        host = request.getHeader(b'host')
        try:
            return self._feeds[host]
        except KeyError:
            request.setResponseCode(404)
            return b'Unknown host: ' + host


def makeXML(feed):
    channel = feed._channel
    return tostring(E.rss(E.channel(E.title(channel.title), E.link(channel.link),
                          *[E.item(E.title(item.title), E.link(item.link))
                            for item in channel.items],
                    version=u"2.0")))


class FeedRetrievalTests(SynchronousTestCase):
    def setUp(self):
        service = StubFeed(
            {URL.from_text(feed._source).host.encode('ascii'): makeXML(feed)
             for feed in FEEDS})
        treq = StubTreq(service.resource())
        self.retriever = FeedRetrieval(treq=treq)
    def testRetrieve(self):
        for feed in FEEDS:
            parsed = self.successResultOf(self.retriever.retrieve(feed._source))
            self.assertEqual(parsed, feed)
    def assertTag(self, tag, name, attributes, text):
        self.assertEqual(tag.tagName, name)
        self.assertEqual(tag.attributes, attributes)
        self.assertEqual(tag.children, [text])
    def test_responseNotOK(self):
        noFeed = StubFeed({})
        retriever = FeedRetrieval(StubTreq(noFeed.resource()))
        failedFeed = self.successResultOf(
            retriever.retrieve("http://missing.invalid/rss.xml"))
        self.assertEqual(
            failedFeed.asJSON(),
            {"error": "Failed to load http://missing.invalid/rss.xml: 404"}
        )
        self.assertTag(failedFeed.asHTML(),
            "a", {"href": "http://missing.invalid/rss.xml"},
            "Failed to load feed: 404")
    def test_unexpectedFailure(self):
        empty = StubFeed({b"empty.invalid": b""})
        retriever = FeedRetrieval(StubTreq(empty.resource()))
        failedFeed = self.successResultOf(
             retriever.retrieve("http://empty.invalid/rss.xml"))
        msg = "SAXParseException('no element found',)"
        self.assertEqual(
            failedFeed.asJSON(),
            {"error": "Failed to load http://empty.invalid/rss.xml: " + msg}
        )
        self.assertTag(failedFeed.asHTML(),
           "a", {"href": "http://empty.invalid/rss.xml"},
           "Failed to load feed: " + msg)
        self.assertTrue(self.flushLoggedErrors(SAXParseException))
