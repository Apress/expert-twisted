from twisted import plugin
from twisted.application import service, strports
from twisted.python.usage import Options
from twisted.web.server import Site
import treq
from feed_aggregation import FeedAggregation, FeedRetrieval
from zope.interface import implementer

class FeedAggregationOptions(Options):
    optParameters = [["listen", "l", "tcp:8080", "How to listen for requests"]]

@implementer(plugin.IPlugin, service.IServiceMaker)
class FeedAggregationServiceMaker(service.Service):
    tapname = "feed"
    description = "Aggregate RSS feeds."
    options = FeedAggregationOptions
    def makeService(self, config):
        urls = ["http://feeds.bbci.co.uk/news/technology/rss.xml",
                "http://planet.twistedmatrix.com/rss20.xml"]
        aggregator = FeedAggregation(FeedRetrieval(treq).retrieve, urls)
        factory = Site(aggregator.resource())
        return strports.service(config['listen'], factory)

makeFeedService = FeedAggregationServiceMaker()
