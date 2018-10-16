#!/usr/bin/env python3
import json
import logging
import multiprocessing
import os
import signal
import sys
import time

import fooster.web

import scoreboard.poll
import scoreboard.scoreboard

import scoreboard.sync


def load(path):
    try:
        import importlib.util

        config_spec = importlib.util.spec_from_file_location('config', path)
        config = importlib.util.module_from_spec(config_spec)
        config_spec.loader.exec_module(config)
    except AttributeError:
        import imp

        config = imp.load_source('config', path)

    return config


def output():
    json.dump(scoreboard.sync.scores.copy(), sys.stdout, indent=2)
    sys.stdout.write('\n')


def main():
    import argparse

    parser = argparse.ArgumentParser(description='a scoreboard for verifying and scoring services in a red vs. blue competition')
    parser.add_argument('-a', '--address', dest='address', default='', help='address to bind')
    parser.add_argument('-p', '--port', type=int, dest='port', default=8000, help='port to bind')
    parser.add_argument('-t', '--template', dest='template', help='template directory to use')
    parser.add_argument('config', help='config file to use')

    args = parser.parse_args()

    web_log = logging.getLogger('web')

    web_log_handler = logging.StreamHandler(sys.stderr)
    web_log.addHandler(web_log_handler)
    web_log.setLevel(logging.INFO)

    http_log = logging.getLogger('http')

    http_log_handler = logging.StreamHandler(sys.stderr)
    http_log_handler.setFormatter(fooster.web.HTTPLogFormatter())
    http_log.addHandler(http_log_handler)
    http_log.addFilter(fooster.web.HTTPLogFilter())
    http_log.setLevel(logging.CRITICAL)

    log = logging.getLogger('scoreboard')
    log.addHandler(logging.StreamHandler(sys.stderr))
    log.setLevel(logging.INFO)

    config = load(args.config)
    scoreboard.poll.reload(config)

    sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)

    svcd = multiprocessing.Process(target=scoreboard.poll.watch, args=(config.interval,))
    httpd = fooster.web.HTTPServer((args.address, args.port), {'/': scoreboard.scoreboard.gen(config, args.template)}, sync=scoreboard.sync.manager, log=web_log, http_log=http_log)

    log.info('Scoreboard initialized')

    svcd.start()
    httpd.start()

    signal.signal(signal.SIGINT, sigint)

    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit())
    signal.signal(signal.SIGUSR1, lambda signum, frame: output())

    last = os.stat(args.config).st_mtime

    try:
        while True:
            wait = time.time()

            if os.stat(args.config).st_mtime > last:
                config = load(args.config)
                scoreboard.poll.reload(config)

                last = os.stat(args.config).st_mtime

            while time.time() - wait < config.interval:
                time.sleep(1)
    except KeyboardInterrupt:
        sys.stdout.write('\n')
    except SystemExit:
        pass

    svcd.terminate()
    svcd.join()

    httpd.close()

    output()


if __name__ == '__main__':
    main()
