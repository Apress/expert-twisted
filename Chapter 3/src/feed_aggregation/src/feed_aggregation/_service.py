import attr
from klein import Klein, Plating
import treq
import feedparser
from twisted.web.template import tags as t, slot
from twisted.logger import Logger

@attr.s(frozen=True)
class Feed(object):
    _source = attr.ib()
    _channel = attr.ib()

    def asJSON(self):
        return attr.asdict(self._channel)

    def asHTML(self):
        header = t.th(t.a(href=self._channel.link)
                      (self._channel.title))
        return t.table(t.tr(header))(
                [t.tr(t.td(t.a(href=item.link)(item.title)))
                 for item in self._channel.items])

@attr.s(frozen=True)
class Channel(object):
    title = attr.ib()
    link = attr.ib()
    items = attr.ib()

@attr.s(frozen=True)
class Item(object):
    title = attr.ib()
    link = attr.ib()

@attr.s(frozen=True)
class EmptyFeed(object):
    _source = attr.ib()
    _reason = attr.ib()

    def asJSON(self):
        return {"error": "Failed to load {}: {}".format(
            self._source, self._reason)}

    def asHTML(self):
        return t.a(href=self._source)("Failed to load feed: {}".format(
            self._reason))


class ResponseNotOK(Exception):
    """A response returned a non-200 status code."""


@attr.s
class FeedRetrieval(object):
    _treq = attr.ib()
    _logger = Logger()
    def retrieve(self, url):
        self._logger.info("Downloading feed {url}", url=url)
        feedDeferred = self._treq.get(url)

        def checkCode(response):
            if response.code != 200:
                raise ResponseNotOK(response.code)
            return response

        feedDeferred.addCallback(checkCode)
        feedDeferred.addCallback(treq.content)
        feedDeferred.addCallback(feedparser.parse)

        def toFeed(parsed):
            if parsed[u'bozo']:
                raise parsed[u'bozo_exception']
            feed = parsed[u'feed']
            entries = parsed[u'entries']
            channel = Channel(feed[u'title'], feed[u'link'],
                              tuple(Item(e[u'title'], e[u'link'])
                                    for e in entries))
            return Feed(url, channel)

        feedDeferred.addCallback(toFeed)

        def emptyFeedWhenNotOK(reason):
            reason.trap(ResponseNotOK)
            self._logger.error("Could not download feed {url}: {reason}",
                               url=url, reason=reason)
            return EmptyFeed(url, str(reason.value))


        def emptyFeedOnUnknwon(failure):
            self._logger.failure("Unexpected failure downloading {url}",
                                 failure=failure, url=url)
            return EmptyFeed(url, repr(failure.value))

        feedDeferred.addErrback(emptyFeedWhenNotOK)
        feedDeferred.addErrback(emptyFeedOnUnknwon)
        return feedDeferred

@attr.s
class FeedAggregation(object):
    _retrieve = attr.ib()
    _urls = attr.ib()
    _app = Klein()
    _plating = Plating(
        tags=t.html(
            t.head(t.title("Feed Aggregator 2.0")),
            t.body(slot(Plating.CONTENT))))
    def resource(self):
        return self._app.resource()
    @_plating.routed(
        _app.route("/"),
        t.div(render="feeds:list")(slot("item")),
    )
    def root(self, request):
        def convert(feed):
            return feed.asJSON() if request.args.get(b"json") else feed.asHTML()
        return {"feeds": [self._retrieve(url).addCallback(convert)
                          for url in self._urls]}
