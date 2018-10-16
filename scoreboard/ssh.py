import socket

import paramiko.client
import paramiko.ssh_exception


def check(addr, port, username, password, **kwargs):
    log.info('SSH: trying {addr}:{port} with {username}', addr=addr, port=port, username=username)

    up = False

    try:
        sshc = paramiko.client.SSHClient()

        sshc.connect(addr, port, username, password)

        up = True

        stdin, stdout, stderr = sshc.exec_command('whoami')

        up = up and stdout.read().decode()[:-1] == username
    except (paramiko.ssh_exception.BadHostKeyException, paramiko.ssh_exception.SSHException, paramiko.ssh_exception.AuthenticationException, socket.error):
        up = False

    return up
