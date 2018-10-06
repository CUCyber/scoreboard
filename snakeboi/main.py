#!/usr/bin/env python3
import json
import multiprocessing
import sys

import fooster.web

import snakeboi.poll
import snakeboi.scoreboard

import snakeboi.sync


def main():
    import importlib.util

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: {} <config.py>\n'.format(sys.argv[0]))
        sys.exit(1)

    config_spec = importlib.util.spec_from_file_location('config', sys.argv[1])
    config = importlib.util.module_from_spec(config_spec)
    config_spec.loader.exec_module(config)

    routes = {'/': snakeboi.scoreboard.gen(config)}

    svcd = multiprocessing.Process(target=snakeboi.poll.watch, args=(config,))
    httpd = fooster.web.HTTPServer(('', 8000), routes, sync=snakeboi.sync.manager)

    svcd.start()
    httpd.start()

    try:
        svcd.join()
    except KeyboardInterrupt:
        svcd.join()

    httpd.close()

    json.dump({name: [score.copy() for score in items] for name, items in snakeboi.sync.scores.items()}, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
