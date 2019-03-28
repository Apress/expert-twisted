
import os

from twisted.internet.defer import inlineCallbacks

from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession
from autobahn.twisted.wamp import ApplicationRunner


class DirectoryLister(ApplicationSession):

    @inlineCallbacks
    def onJoin(self, details):
        while True:

            # List files and group them by extensions
            files = {}
            for f in os.listdir('.'):
                file, ext = os.path.splitext(f)
                if ext.strip():
                    files.setdefault(ext, []).append(f)

            # Send one event named "filewithext.xxx" for each file extension
            # with "xxx" being the extension. We attach the list of files
            # to the events to that every clients interested in the event
            # can get the file list.
            # This is the "publish" part of "PUB/SUB".
            for ext, names in files.items():
                # Note that there is no need to declare the event before
                # using it. You can publish events as you go.
                yield self.publish(u'filewithext' + ext , names)

            yield sleep(1)


# The ApplicationRunner will take care starting everything for us.
if __name__ == '__main__':
    runner = ApplicationRunner(url=u"ws://localhost:8080/ws", realm=u"realm1")
    print(u"Connecting to ws://localhost:8080/ws")
    runner.run(DirectoryLister)
