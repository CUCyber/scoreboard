import logging
import socket

import paramiko.client
import paramiko.ssh_exception


log = logging.getLogger('scoreboard')


def check(addr, port, username, password, timeout=1, **kwargs):
    log.info(('SSH: trying {addr}:{port} with {username}').format(addr=addr, port=port, username=username))

    up = False

    try:
        sshc = paramiko.client.SSHClient()
        sshc.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)

        sshc.connect(addr, port, username, password, timeout=timeout)

        up = True

        stdin, stdout, stderr = sshc.exec_command('whoami', timeout=timeout)

        up = up and stdout.read().decode()[:-1] == username
    except (paramiko.ssh_exception.BadHostKeyException, paramiko.ssh_exception.SSHException, paramiko.ssh_exception.AuthenticationException, socket.error, EOFError):
        up = False
    finally:
        try:
            sshc.close()
        except:
            pass

    return up
