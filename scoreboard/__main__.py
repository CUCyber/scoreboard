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


if sys.version_info >= (3, 7):
    start_method = 'spawn'
else:
    start_method = 'fork'


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


def output(sync):
    json.dump(sync.scores.copy(), sys.stdout, indent=2)
    sys.stdout.write('\n')


def main():
    import argparse

    parser = argparse.ArgumentParser(prog=None if sys.argv[0] != __file__ or globals().get('__spec__') is None else 'python -m {}'.format(__spec__.name.rpartition('.')[0]), description='a scoreboard for verifying and scoring services in a red vs. blue competition')
    parser.add_argument('-a', '--address', dest='address', default='', help='address to bind')
    parser.add_argument('-p', '--port', type=int, dest='port', default=8000, help='port to bind')
    parser.add_argument('-t', '--template', dest='template', help='template directory to use')
    parser.add_argument('config', help='config file to use')

    args = parser.parse_args()

    log = logging.getLogger('scoreboard:poll')
    web_log = logging.getLogger('scoreboard:web')
    http_log = logging.getLogger('scoreboard:http')

    config = load(args.config)

    sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)

    manager = multiprocessing.get_context(start_method).Manager()
    sync = scoreboard.sync.Sync(manager)

    scoreboard.poll.reload(sync, config)

    svcd = multiprocessing.get_context(start_method).Process(target=scoreboard.poll.watch, args=(sync,))
    workers = [multiprocessing.get_context(start_method).Process(target=scoreboard.poll.worker, args=(sync,)) for i in range(config.workers)]
    httpd = fooster.web.HTTPServer((args.address, args.port), {'/': fooster.web.HTTPHandlerWrapper(scoreboard.scoreboard.Scoreboard, template=args.template, sync=sync), '/status': fooster.web.HTTPHandlerWrapper(scoreboard.scoreboard.ScoreboardJSON, sync=sync)}, log=web_log, http_log=http_log)

    log.info('Scoreboard initialized')

    sync.watching.value = True
    sync.working.value = True

    svcd.start()
    for worker in workers:
        worker.start()
    httpd.start()

    last = os.stat(args.config).st_mtime

    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit())
    signal.signal(signal.SIGUSR1, lambda signum, frame: output(sync))

    signal.signal(signal.SIGINT, sigint)

    try:
        while True:
            wait = time.time()

            if os.stat(args.config).st_mtime > last:
                previous = config

                config = load(args.config)
                scoreboard.poll.reload(sync, config)

                if previous.workers != config.workers:
                    log.info('Restarting workers')

                    sync.working.value = False

                    for worker in workers:
                        worker.join()

                    sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)

                    workers = [multiprocessing.get_context(start_method).Process(target=scoreboard.poll.worker, args=(sync,)) for i in range(config.workers)]

                    sync.working.value = True

                    for worker in workers:
                        worker.start()

                    signal.signal(signal.SIGINT, sigint)

                last = os.stat(args.config).st_mtime

            while time.time() - wait < sync.poll.value:
                time.sleep(1)
    except KeyboardInterrupt:
        sys.stderr.write('\n')
    except SystemExit:
        pass

    sync.watching.value = False
    sync.working.value = False

    svcd.join()
    for worker in workers:
        worker.join()

    httpd.close()

    output(sync)


if __name__ == '__main__':
    main()
