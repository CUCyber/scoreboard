#!/usr/bin/env python3
import json
import logging
import multiprocessing
import sys

import fooster.web

import scoreboard.poll
import scoreboard.scoreboard

import scoreboard.sync


def main():
    import argparse
    import importlib.util

    parser = argparse.ArgumentParser(description='a scoreboard for verifying and scoring services in a red vs. blue competition')
    parser.add_argument('-a', '--address', dest='address', default='', help='address to bind')
    parser.add_argument('-p', '--port', type=int, dest='port', default=8000, help='port to bind')
    parser.add_argument('-t', '--template', dest='template', help='template directory to use')
    parser.add_argument('config', help='config file to use')

    args = parser.parse_args()

    config_spec = importlib.util.spec_from_file_location('config', args.config)
    config = importlib.util.module_from_spec(config_spec)
    config_spec.loader.exec_module(config)

    web_log = logging.getLogger('web')

    web_log_handler = logging.StreamHandler(sys.stderr)
    web_log.addHandler(web_log_handler)
    web_log.setLevel(logging.WARNING)

    http_log = logging.getLogger('http')

    http_log_handler = logging.StreamHandler(sys.stderr)
    http_log_handler.setFormatter(fooster.web.HTTPLogFormatter())
    http_log.addHandler(http_log_handler)
    http_log.addFilter(fooster.web.HTTPLogFilter())
    http_log.setLevel(logging.INFO)

    log = logging.getLogger('scoreboard')
    log.addHandler(logging.StreamHandler(sys.stderr))

    svcd = multiprocessing.Process(target=scoreboard.poll.watch, args=(config,))
    httpd = fooster.web.HTTPServer((args.address, args.port), {'/': scoreboard.scoreboard.gen(config, args.template)}, sync=scoreboard.sync.manager, log=web_log, http_log=http_log)

    svcd.start()
    httpd.start()

    try:
        svcd.join()
    except KeyboardInterrupt:
        svcd.join()

    httpd.close()

    sys.stdout.write('\n')
    json.dump({name: [score.copy() for score in items] for name, items in scoreboard.sync.scores.items()}, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
