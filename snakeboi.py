#!/usr/bin/env python3
import io
import ipaddress
import json
import multiprocessing
import os.path
import random
import signal
import ssl
import string
import sys
import time

import fooster.web
import fooster.web.page


import ftplib
import dns.exception
import dns.resolver
import http.client
import imaplib
import ldap
import MySQLdb
import paramiko.client
import paramiko.ssh_exception
import poplib
import smtplib
import socket
import subprocess


teams = {
    'Team1': '10.0.130.0',
    'Team2': '10.0.131.0',
    'Team3': '10.0.132.0',
    'Team4': '10.0.133.0',
}

services = {
    'FTP': {'offset': 5, 'port': 21, 'file': 'DONOTDELETE', 'contents': 'asdf', 'dne': 'DOESNOTEXIST'},
    'SSH': {'offset': 6, 'port': 22, 'username': 'asdf', 'password': 'asdf'},
    'HTTP': {'offset': 7, 'port': 80, 'regex': 'asdf'},
    'MySQL': {'offset': 8, 'port': 3306, 'username': 'asdf', 'password': 'asdf', 'db': 'asdf'},
}

interval = 60


signal.signal(signal.SIGINT, signal.SIG_IGN)


sync = multiprocessing.Manager()

run = sync.Value('b', False)
scores = sync.dict()


def poll():
    opts = []

    for name, base in teams.items():
        scores[name] = sync.list()

        for proto, service in services.items():
            addr = str(ipaddress.IPv4Address(base) + service['offset'])
            score = {'proto': proto, 'addr': addr, 'status': False, 'score': 0}
            opt = {'proto': proto, 'addr': addr, 'link': score}
            opt.update(service)

            scores[name].append(score)
            opts.append(opt)

    run.value = True

    while run.value:
        wait = time.time()

        for opt in opts:
            up = False

            if opt['proto'].lower() == 'ping':
                up = subprocess.call(['ping', '-c4', opt['addr']]) == 0
            elif opt['proto'].lower() == 'ftp':
                if 'dne' in opt:
                    nonce = ''.join(random.choice(string.ascii_letters) for _ in range(16)) + opt['dne']

                try:
                    if 'cert' in opt:
                        context = ssl.create_default_context()
                        context.load_cert_chain(opt['cert'])

                        ftp = ftplib.FTP_TLS(context=context)
                    else:
                        ftp = ftplib.FTP()

                    ftp.connect(opt['addr'], opt['port'])

                    up = True

                    if 'username' in opt:
                        ftp.login(opt['username'], opt['password'])
                    else:
                        ftp.login()

                    if 'file' in opt:
                        up = opt['file'] in ftp.nlst()

                        buf = io.StringIO()
                        ftp.retrlines('RETR {}'.format(opt['file']), buf.write)

                        if 'contents' in opt:
                            up = up and buf.getvalues() == opt['contents']

                    if 'dne' in opt:
                        up = up and nonce not in ftp.nlst()
                except ftplib.all_errors:
                    up = False
            elif opt['proto'].lower() == 'ssh':
                ssh = paramiko.client.SSHClient()
                try:
                    ssh.connect(opt['addr'], opt['port'], opt['username'], opt['password'])

                    up = True

                    stdin, stdout, stderr = client.exec_command('whoami')

                    up = up and stdout.read() == opt['username']
                except (paramiko.ssh_exception.BadHostKeyException, paramiko.ssh_exception.SSHException, paramiko.ssh_exception.AuthenticationException, socket.error):
                    up = False
            elif opt['proto'].lower() == 'smtp':
                nonce = ''.join(random.choice(string.ascii_letters) for _ in range(16))

                try:
                    smtpc = smtplib.SMTP()
                    smtpc.connect(opt['addr'], opt['port'])
                    smtpc.ehlo('{}.com'.format(nonce))

                    if 'cert' in opt:
                        context = ssl.create_default_context()
                        context.load_cert_chain(opt['cert'])

                        smtpc.starttls(context=context)

                    if 'username' in opt:
                        smtpc.login(opt['username'], opt['password'])

                    if 'from' in opt:
                        smtpc.mail(opt['from'])
                        smtpc.rcpt(opt['to'])

                    smtpc.quit()

                    up = True
                except smtplib.SMTPException:
                    up = False
            elif opt['proto'].lower() == 'dns':
                try:
                    dnsc = dns.resolver.Resolver()

                    dnsc.nameservers = opt['addr']
                    dnsc.port = opt['port']

                    answer = dnsc.query(opt['hostname'], opt['type'])

                    up = answer[0].items[0] == opt['answer']
                except dns.exception.DNSException:
                    up = False
            elif opt['proto'].lower() == 'http':
                try:
                    if 'cert' in opt:
                        context = ssl.create_default_context()
                        context.load_cert_chain(opt['cert'])

                        httpc = http.client.HTTPSConnection(opt['host'] if 'host' in opt else opt['addr'], opt['port'], context=context)
                    else:
                        httpc = http.client.HTTPConnection(opt['host'] if 'host' in opt else opt['addr'], opt['port'])

                    up = True

                    if 'method' in opt:
                        req = httpc.request(opt['method'], opt['url'], opt['body'] if 'body' in opt else None, opt['headers'] if 'headers' in opt else None)

                        if 'contents' in opt:
                            up = up and req.read() == opt['contents']
                except http.client.HTTPException:
                    up = False
            elif opt['proto'].lower() == 'ldap':
                try:
                    ldapc = ldap.initialize('ldap://cuid.clemson.edu')

                    up = True

                    if 'cert' in opt:
                        ldapc.set_option(ldap.OPT_X_TLS_CERTFILE, opt['cert'])
                        ldapc.start_tls_s()

                    if 'dn' in opt:
                        ldapc.simple_bind_s(opt['dn'], opt['password'])

                    if 'base' in opt:
                        ldapc.search_s(opt['base'], ldap.SCOPE_ONELEVEL, '(cn=' + opt['cn'] + ')', ['cn'])

                        up = up and results[0][1]['cn'][0].decode() == 'cn'
                except (ldap.LDAPError, IndexError, KeyError):
                    up = False
            elif opt['proto'].lower() == 'pop3':
                try:
                    popc = poplib.POP3(opt['addr'], opt['port'])

                    if 'cert' in opt:
                        context = ssl.create_default_context()
                        context.load_cert_chain(opt['cert'])

                        popc.stls(context=context)

                    if 'username' in opt:
                        popc.user(opt['username'])
                        popc.pass_(opt['password'])

                        if 'list' in opt:
                            up = popc.list()[0] == 'OK' and popc.list()[1] == opt['list']
                except (poplib.error_proto, socket.error):
                    up = False
            elif opt['proto'].lower() == 'imap':
                try:
                    imapc = imaplib.IMAP4(opt['addr'], opt['port'])

                    up = True

                    if 'cert' in opt:
                        context = ssl.create_default_context()
                        context.load_cert_chain(opt['cert'])

                        imapc.starttls(ssl_context=context)

                    if 'username' in opt:
                        imapc.login(opt['username'], opt['password'])

                        imapc.select()

                        if 'list' in opt:
                            up = up and imapc.list()[0] == 'OK' and imapc.list()[1] == opt['list']
                except imaplib.error:
                    up = False
            elif opt['proto'].lower() == 'mysql':
                try:
                    db = MySQLdb.connect(opt['addr'], opt['username'], opt['password'], opt['db'])

                    cursor = db.cursor()

                    up = True

                    if 'query' in opt:
                        cursor.execute(opt['query'])

                        if 'result' in opt:
                            up = up and cursor.fetchall() == opt['result']
                except MySQLdb.Error:
                    up = False

            if up:
                opt['link']['score'] += 1

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
            scoreboard += '\n\t\t<tr>\n\t\t\t<td>{}</td>'.format(name) + ''.join('<td class="{}">{}</td>'.format('up' if score['status'] else 'down', 'Up' if score['status'] else 'Down') for score in items) + '<td>{}</td>\n\t\t</tr>'.format(sum(score['score'] for score in items))

        scoreboard += '\n\t</tbody>\n</table>'

        return page.format(refresh=interval, scoreboard=scoreboard)

def main():
    routes = { '/': Scoreboard }

    svcd = multiprocessing.Process(target=poll)
    httpd = fooster.web.HTTPServer(('localhost', 8000), routes, sync=sync)

    svcd.start()
    httpd.start()

    signal.signal(signal.SIGINT, lambda signum, frame: stop())

    svcd.join()

    httpd.close()

    json.dump({name: items[:] for name, items in scores.items()}, sys.stdout, indent=2)

if __name__ == '__main__':
    main()
