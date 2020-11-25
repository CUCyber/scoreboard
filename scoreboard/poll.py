import ipaddress
import logging
import queue
import random
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
import scoreboard.sftp
import scoreboard.tcp

import scoreboard.sync


log = logging.getLogger('scoreboard:poll')


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
    elif opt['proto'].lower() == 'sftp':
        return scoreboard.sftp.check(timeout=timeout, **opt)
    elif opt['proto'].lower() == 'tcp':
        return scoreboard.tcp.check(timeout=timeout, **opt)
    else:
        raise RuntimeError('config error: proto \'{}\' not found'.format(opt['proto'].lower()))


def reload(sync, config):
    log.info('Reloading')

    with sync.lock:
        sync.score.value = config.score

        sync.interval.value = config.interval
        sync.timeout.value = config.timeout
        sync.poll.value = config.poll
        sync.show.value = config.show

        for name, base in config.teams.items():
            team = []

            for service, opts in config.services.items():
                if service == 'dns':
                    if 'answer' in opts and isinstance(opts['answer'], int):
                        opts['answer'] = str(ipaddress.IPv4Address(base) + opts['answer'])

                addr = str(ipaddress.IPv4Address(base) + opts['offset'])
                if name in sync.scores:
                    for prev in sync.scores[name]:
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

                for prev in sync.opts:
                    if prev['addr'] == opt['addr'] and prev['port'] == opt['port']:
                        sync.opts.remove(prev)
                        break
                sync.opts.append(opt)

            if name not in sync.teams:
                sync.teams.append(name)
            sync.scores[name] = team

        for name in sync.teams:
            if name not in config.teams:
                sync.teams.remove(name)

        del sync.services[:]

        for service in config.services.keys():
            sync.services.append(service)


def worker(sync):
    while sync.working.value:
        try:
            opt = sync.queue.get_nowait()
        except queue.Empty:
            time.sleep(sync.poll.value)
            continue

        if check(opt, sync.timeout.value):
            with sync.lock:
                tmp = sync.scores[opt['link'][0]]
                tmp[opt['link'][1]]['status'] = True
                if sync.score.value:
                    tmp[opt['link'][1]]['score'] += opt['weight'] if 'weight' in opt else 1
                sync.scores[opt['link'][0]] = tmp
        else:
            with sync.lock:
                tmp = sync.scores[opt['link'][0]]
                tmp[opt['link'][1]]['status'] = False
                sync.scores[opt['link'][0]] = tmp


def watch(sync):
    while sync.watching.value:
        log.info('Checking services')

        wait = time.time()

        with sync.lock:
            idx = {}
            for opt in sync.opts:
                probe = {}

                for key, val in opt.items():
                    if isinstance(val, list):
                        service = sync.scores[opt['link'][0]][opt['link'][1]]['service']
                        if service not in idx:
                            idx[service] = random.randint(0, len(val) - 1)
                        probe[key] = val[idx[service]]
                    else:
                        probe[key] = val

                sync.queue.put(probe)

        while sync.watching.value and time.time() - wait < sync.interval.value:
            time.sleep(sync.poll.value)
