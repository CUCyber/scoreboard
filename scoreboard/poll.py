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
        team = []

        for proto, service in config.services.items():
            addr = str(ipaddress.IPv4Address(base) + service['offset'])
            score = {'proto': proto, 'addr': addr, 'status': False, 'score': 0}
            opt = {'link': (name, len(team)), 'addr': addr}
            opt.update(service)

            team.append(score)
            opts.append(opt)

        scoreboard.sync.scores[name] = team

    while True:
        try:
            wait = time.time()

            for opt in opts:
                if check(opt):
                    tmp = scoreboard.sync.scores[opt['link'][0]]
                    tmp[opt['link'][1]]['status'] = True
                    tmp[opt['link'][1]]['score'] += opt['weight'] if 'weight' in opt else 1
                    scoreboard.sync.scores[opt['link'][0]] = tmp
                else:
                    tmp = scoreboard.sync.scores[opt['link'][0]]
                    tmp[opt['link'][1]]['status'] = False
                    scoreboard.sync.scores[opt['link'][0]] = tmp


            while time.time() - wait < config.interval:
                time.sleep(1)

        except KeyboardInterrupt:
            break
