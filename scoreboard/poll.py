import ipaddress
import logging
import time

import scoreboard.ping
import scoreboard.ftp
import scoreboard.ssh
import scoreboard.smtp
import scoreboard.dns
import scoreboard.http
import scoreboard.ldap
import scoreboard.pop3
import scoreboard.imap
import scoreboard.mysql
import scoreboard.tcp

import scoreboard.sync


log = logging.getLogger('scoreboard')


def check(opt, timeout):
    if opt['proto'].lower() == 'ping':
        return scoreboard.ping.check(timeout=timeout, **opt)
    elif opt['proto'].lower() == 'ftp':
        return scoreboard.ftp.check(timeout=timeout, **opt)
    elif opt['proto'].lower() == 'ssh':
        return scoreboard.ssh.check(timeout=timeout, **opt)
    elif opt['proto'].lower() == 'smtp':
        return scoreboard.smtp.check(timeout=timeout, **opt)
    elif opt['proto'].lower() == 'dns':
        return scoreboard.dns.check(timeout=timeout, **opt)
    elif opt['proto'].lower() == 'http':
        return scoreboard.http.check(timeout=timeout, **opt)
    elif opt['proto'].lower() == 'ldap':
        return scoreboard.ldap.check(timeout=timeout, **opt)
    elif opt['proto'].lower() == 'pop3':
        return scoreboard.pop3.check(timeout=timeout, **opt)
    elif opt['proto'].lower() == 'imap':
        return scoreboard.imap.check(timeout=timeout, **opt)
    elif opt['proto'].lower() == 'mysql':
        return scoreboard.mysql.check(timeout=timeout, **opt)
    elif opt['proto'].lower() == 'tcp':
        return scoreboard.tcp.check(timeout=timeout, **opt)
    else:
        raise RuntimeError('config error: proto \'{}\' not found'.format(opt['proto'].lower()))


def reload(config):
    log.info('Reloading')

    with scoreboard.sync.lock:
        for name, base in config.teams.items():
            team = []

            for service, opts in config.services.items():
                if service == 'dns':
                    if 'answer' in opts and isinstance(opts['answer'], int):
                        opts['answer'] = str(ipaddress.IPv4Address(base) + opts['answer'])

                addr = str(ipaddress.IPv4Address(base) + opts['offset'])
                if name in scoreboard.sync.scores:
                    for prev in scoreboard.sync.scores[name]:
                        if prev['service'] == service:
                            score = {'service': service, 'addr': addr, 'status': prev['status'], 'score': prev['score']}
                            break
                    else:
                        score = {'service': service, 'addr': addr, 'status': False, 'score': 0}
                else:
                    score = {'service': service, 'addr': addr, 'status': False, 'score': 0}
                opt = {'link': (name, len(team)), 'addr': addr}
                opt.update(opts)

                team.append(score)
                scoreboard.sync.opts.append(opt)

            if name not in scoreboard.sync.teams:
                scoreboard.sync.teams.append(name)
            scoreboard.sync.scores[name] = team

        del scoreboard.sync.services[:]

        for service in config.services.keys():
            scoreboard.sync.services.append(service)


def watch(interval, timeout):
    while True:
        log.info('Checking services')

        wait = time.time()

        for opt in scoreboard.sync.opts:
            if check(opt, timeout):
                with scoreboard.sync.lock:
                    tmp = scoreboard.sync.scores[opt['link'][0]]
                    tmp[opt['link'][1]]['status'] = True
                    tmp[opt['link'][1]]['score'] += opt['weight'] if 'weight' in opt else 1
                    scoreboard.sync.scores[opt['link'][0]] = tmp
            else:
                with scoreboard.sync.lock:
                    tmp = scoreboard.sync.scores[opt['link'][0]]
                    tmp[opt['link'][1]]['status'] = False
                    scoreboard.sync.scores[opt['link'][0]] = tmp

        while time.time() - wait < interval:
            time.sleep(1)
