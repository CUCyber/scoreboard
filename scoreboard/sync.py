import logging
import sys

import fooster.web


class Sync:
    def __init__(self, manager):
        self.score = manager.Value('b', True)

        self.interval = manager.Value('I', 60)
        self.timeout = manager.Value('I', 1)
        self.poll = manager.Value('I', 1)
        self.show = manager.Value('b', True)
        self.watching = manager.Value('b', False)
        self.working = manager.Value('b', False)

        self.lock = manager.Lock()

        self.services = manager.list()
        self.teams = manager.list()
        self.scores = manager.dict()
        self.opts = manager.list()
        self.queue = manager.Queue()


log = logging.getLogger('scoreboard:poll')
log.addHandler(logging.StreamHandler(sys.stderr))
log.setLevel(logging.INFO)

web_log = logging.getLogger('scoreboard:web')
web_log_handler = logging.StreamHandler(sys.stderr)
web_log.addHandler(web_log_handler)
web_log.setLevel(logging.INFO)

http_log = logging.getLogger('scoreboard:http')
http_log_handler = logging.StreamHandler(sys.stderr)
http_log_handler.setFormatter(fooster.web.HTTPLogFormatter())
http_log.addHandler(http_log_handler)
http_log.addFilter(fooster.web.HTTPLogFilter())
http_log.setLevel(logging.CRITICAL)
