import ipaddress
import time

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

import snakeboi.sync


def check(opt):
    if opt['proto'].lower() == 'ping':
        return snakeboi.ping.check(**opt)
    elif opt['proto'].lower() == 'ftp':
        return snakeboi.ftp.check(**opt)
    elif opt['proto'].lower() == 'ssh':
        return snakeboi.ssh.check(**opt)
    elif opt['proto'].lower() == 'smtp':
        return snakeboi.smtp.check(**opt)
    elif opt['proto'].lower() == 'dns':
        return snakeboi.dns.check(**opt)
    elif opt['proto'].lower() == 'http':
        return snakeboi.http.check(**opt)
    elif opt['proto'].lower() == 'ldap':
        return snakeboi.ldap.check(**opt)
    elif opt['proto'].lower() == 'pop3':
        return snakeboi.pop3.check(**opt)
    elif opt['proto'].lower() == 'imap':
        return snakeboi.imap.check(**opt)
    elif opt['proto'].lower() == 'mysql':
        return snakeboi.mysql.check(**opt)
    else:
        raise RuntimeError('config error: proto not found')


def watch(config):
    opts = []

    for name, base in config.teams.items():
        snakeboi.sync.scores[name] = snakeboi.sync.manager.list()

        for proto, service in config.services.items():
            addr = str(ipaddress.IPv4Address(base) + service['offset'])
            score = snakeboi.sync.manager.dict({'proto': proto, 'addr': addr, 'status': False, 'score': 0})
            opt = {'addr': addr, 'link': score}
            opt.update(service)

            snakeboi.sync.scores[name].append(score)
            opts.append(opt)

    while True:
        try:
            wait = time.time()

            for opt in opts:
                if check(opt):
                    opt['link']['status'] = True
                    opt['link']['score'] += opt['weight'] if 'weight' in opt else 1
                else:
                    opt['link']['status'] = False

            while time.time() - wait < config.interval:
                time.sleep(1)

        except KeyboardInterrupt:
            break
