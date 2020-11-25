import logging
import random
import socket
import string

import paramiko.client
import paramiko.sftp_client
import paramiko.ssh_exception


log = logging.getLogger('scoreboard:poll')


def check(addr, port, username, password, file=None, contents=None, dne=None, timeout=1, **kwargs):
    log.info(('SFTP: trying {addr}:{port} with {username}' + (' for {file}' if file else '')).format(addr=addr, port=port, username=username, file=file))

    up = False

    if dne is not None:
        nonce = ''.join(random.choice(string.ascii_letters) for _ in range(16)) + dne

    try:
        sshc = paramiko.client.SSHClient()
        sshc.set_missing_host_key_policy(paramiko.client.AutoAddPolicy)

        sshc.connect(addr, port, username, password, timeout=timeout)

        sftpc = paramiko.sftp_client.SFTPClient.from_transport(sshc.get_transport())

        up = True

        if file is not None:
            up = up and (file[0] == '/' or file in sftpc.listdir())

            if contents is not None:
                with sftpc.open(file) as fobj:
                    if isinstance(contents, str):
                        up = up and fobj.read().decode() == contents
                    else:
                        up = up and fobj.read() == contents

        if dne is not None:
            up = up and nonce not in sftpc.listdir()
    except (paramiko.ssh_exception.BadHostKeyException, paramiko.ssh_exception.SSHException, paramiko.ssh_exception.AuthenticationException, socket.error, IOError, EOFError):
        up = False
    finally:
        try:
            sshc.close()
        except Exception:
            pass

    return up
