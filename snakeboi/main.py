#!/usr/bin/env python3
import json
import multiprocessing
import sys

import fooster.web

import snakeboi.poll
import snakeboi.scoreboard

import snakeboi.sync


def main():
    import argparse
    import importlib.util

    parser = argparse.ArgumentParser(description='a scoreboard for verifying and scoring red vs. blue services')
    parser.add_argument('-a', '--address', dest='address', default='', help='address to bind')
    parser.add_argument('-p', '--port', type=int, dest='port', default=8000, help='port to bind')
    parser.add_argument('-t', '--template', dest='template', help='template directory to use')
    parser.add_argument('config', help='config file to use')

    args = parser.parse_args()

    config_spec = importlib.util.spec_from_file_location('config', args.config)
    config = importlib.util.module_from_spec(config_spec)
    config_spec.loader.exec_module(config)

    svcd = multiprocessing.Process(target=snakeboi.poll.watch, args=(config,))
    httpd = fooster.web.HTTPServer((args.address, args.port), {'/': snakeboi.scoreboard.gen(config, args.template)}, sync=snakeboi.sync.manager)

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
