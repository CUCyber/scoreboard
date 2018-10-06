import ipaddress
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

import scoreboard.sync


def check(opt):
    if opt['proto'].lower() == 'ping':
        return scoreboard.ping.check(**opt)
    elif opt['proto'].lower() == 'ftp':
        return scoreboard.ftp.check(**opt)
    elif opt['proto'].lower() == 'ssh':
        return scoreboard.ssh.check(**opt)
    elif opt['proto'].lower() == 'smtp':
        return scoreboard.smtp.check(**opt)
    elif opt['proto'].lower() == 'dns':
        return scoreboard.dns.check(**opt)
    elif opt['proto'].lower() == 'http':
        return scoreboard.http.check(**opt)
    elif opt['proto'].lower() == 'ldap':
        return scoreboard.ldap.check(**opt)
    elif opt['proto'].lower() == 'pop3':
        return scoreboard.pop3.check(**opt)
    elif opt['proto'].lower() == 'imap':
        return scoreboard.imap.check(**opt)
    elif opt['proto'].lower() == 'mysql':
        return scoreboard.mysql.check(**opt)
    else:
        raise RuntimeError('config error: proto not found')


def watch(config):
    opts = []

    for name, base in config.teams.items():
        scoreboard.sync.scores[name] = scoreboard.sync.manager.list()

        for proto, service in config.services.items():
            addr = str(ipaddress.IPv4Address(base) + service['offset'])
            score = scoreboard.sync.manager.dict({'proto': proto, 'addr': addr, 'status': False, 'score': 0})
            opt = {'addr': addr, 'link': score}
            opt.update(service)

            scoreboard.sync.scores[name].append(score)
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
