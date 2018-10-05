#!/usr/bin/env python
import ipaddress
import json
import multiprocessing
import os.path
import signal
import subprocess
import sys
import time

import fooster.web
import fooster.web.page


teams = {
    'team1': '10.0.130.0',
    'team2': '10.0.131.0',
    'team3': '10.0.132.0',
    'team4': '10.0.133.0',
}

services = {
    'smtp': {'offset': 5, 'port': 25},
}

interval = 60


signal.signal(signal.SIGINT, signal.SIG_IGN)


sync = multiprocessing.Manager()

run = sync.Value('b', False)
scores = sync.dict()


def poll():
    addrs = []

    for name, base in teams.items():
        scores[name] = sync.list()

        for proto, service in services.items():
            addr = str(ipaddress.IPv4Address(base) + service['offset'])
            score = {'proto': proto, 'addr': addr, 'status': False, 'score': 0}
            scores[name].append(score)
            addrs.append({'proto': proto, 'addr': addr, 'port': service['port'], 'score': scores[name][-1]})

    run.value = True

    while run.value:
        for addr in addrs:
            up = False

            if proto == 'ping':
                pass
            elif proto == 'ftp':
                pass
            elif proto == 'ssh':
                pass
            elif proto == 'smtp':
                pass
            elif proto == 'http':
                pass
            elif proto == 'https':
                pass
            elif proto == 'pop3':
                pass
            elif proto == 'imap':
                pass

            if up:
                addr['score']['score'] += 1

        wait = time.time()
        while run.value and time.time() - wait < interval:
            time.sleep(1)


def stop():
    run.value = False


class Scoreboard(fooster.web.page.PageHandler):
    directory = os.path.dirname(os.path.abspath(__file__)) + '/html'
    page = 'index.html'

    def format(self, page):
        scoreboard = '<table>\n\t<thead>\n\t\t<tr>\n\t\t\t<th>Name</th>' + ''.join('<th>{}</th>'.format(service) for service in services) + '<th>Score</th>\n\t\t</tr>\n\t</thead>\n\n\t<tbody>'
        for name, items in scores.items():
            scoreboard += '\n\t\t<tr>\n\t\t\t<td>{}</td>'.format(name) + ''.join('<td>{}</td>'.format('Up' if score['status'] else 'Down') for score in items) + '<td>{}</td>\n\t\t</tr>'.format(sum(score['score'] for score in items))

        scoreboard += '\n\t</tbody>\n</table>'

        return page.format(scoreboard=scoreboard)

def main():
    routes = { '/': Scoreboard }

    svcd = multiprocessing.Process(target=poll)
    httpd = fooster.web.HTTPServer(('localhost', 8080), routes, sync=sync)

    svcd.start()
    httpd.start()

    signal.signal(signal.SIGINT, lambda signum, frame: stop())

    svcd.join()

    httpd.close()

    json.dump({name: items[:] for name, items in scores.items()}, sys.stdout, indent=2)

if __name__ == '__main__':
    main()
