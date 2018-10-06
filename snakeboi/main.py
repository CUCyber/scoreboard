#!/usr/bin/env python3
import ipaddress
import json
import multiprocessing
import os.path
import signal
import sys
import time

import fooster.web
import fooster.web.page


import snakeboi.ping
import snakeboi.ftp
import snakeboi.ssh
import snakeboi.smtp
import snakeboi.dns
import snakeboi.http
import snakeboi.ldap
import snakeboi.pop3
import snakeboi.imap
import snakeboi.mysql


sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)


sync = multiprocessing.Manager()

scores = sync.dict()


def poll(config):
    signal.signal(signal.SIGINT, sigint)

    opts = []

    for name, base in config.teams.items():
        scores[name] = sync.list()

        for proto, service in config.services.items():
            addr = str(ipaddress.IPv4Address(base) + service['offset'])
            score = sync.dict({'proto': proto, 'addr': addr, 'status': False, 'score': 0})
            opt = {'addr': addr, 'link': score}
            opt.update(service)

            scores[name].append(score)
            opts.append(opt)

    while True:
        try:
            wait = time.time()

            for opt in opts:
                up = False

                if opt['proto'].lower() == 'ping':
                    up = snakeboi.ping.check(**opt)
                elif opt['proto'].lower() == 'ftp':
                    up = snakeboi.ftp.check(**opt)
                elif opt['proto'].lower() == 'ssh':
                    up = snakeboi.ssh.check(**opt)
                elif opt['proto'].lower() == 'smtp':
                    up = snakeboi.smtp.check(**opt)
                elif opt['proto'].lower() == 'dns':
                    up = snakeboi.dns.check(**opt)
                elif opt['proto'].lower() == 'http':
                    up = snakeboi.http.check(**opt)
                elif opt['proto'].lower() == 'ldap':
                    up = snakeboi.ldap.check(**opt)
                elif opt['proto'].lower() == 'pop3':
                    up = snakeboi.pop3.check(**opt)
                elif opt['proto'].lower() == 'imap':
                    up = snakeboi.imap.check(**opt)
                elif opt['proto'].lower() == 'mysql':
                    up = snakeboi.mysql.check(**opt)
                else:
                    raise RuntimeError('config error: proto not found')

                if up:
                    opt['link']['status'] = True
                    opt['link']['score'] += 1
                else:
                    opt['link']['status'] = False

            while time.time() - wait < config.interval:
                time.sleep(1)

        except KeyboardInterrupt:
            break


class Scoreboard(fooster.web.page.PageHandler):
    directory = os.path.dirname(os.path.abspath(__file__)) + '/html'
    page = 'index.html'
    config = {'services': [], 'interval': 60}

    def format(self, page):
        scoreboard = '<table>\n\t<thead>\n\t\t<tr>\n\t\t\t<th>Name</th>' + ''.join('<th>{}</th>'.format(service) for service in Scoreboard.config.services) + '<th>Score</th>\n\t\t</tr>\n\t</thead>\n\n\t<tbody>'
        for name, items in scores.items():
            scoreboard += '\n\t\t<tr>\n\t\t\t<td>{}</td>'.format(name) + ''.join('<td class="{}">{}</td>'.format('up' if score['status'] else 'down', 'Up' if score['status'] else 'Down') for score in items) + '<td>{}</td>\n\t\t</tr>'.format(sum(score['score'] for score in items))

        scoreboard += '\n\t</tbody>\n</table>'

        return page.format(refresh=Scoreboard.config.interval, scoreboard=scoreboard)


def main():
    import importlib.util

    if len(sys.argv) != 2:
        sys.stderr.write('Usage: {} <config.py>\n'.format(sys.argv[0]))
        sys.exit(1)

    config_spec = importlib.util.spec_from_file_location('config', sys.argv[1])
    config = importlib.util.module_from_spec(config_spec)
    config_spec.loader.exec_module(config)

    Scoreboard.config = config

    routes = {'/': Scoreboard}

    svcd = multiprocessing.Process(target=poll, args=(config,))
    httpd = fooster.web.HTTPServer(('', 8000), routes, sync=sync)

    svcd.start()
    httpd.start()

    svcd.join()

    httpd.close()

    json.dump({name: [score.copy() for score in items] for name, items in scores.items()}, sys.stdout, indent=2)


if __name__ == '__main__':
    main()
