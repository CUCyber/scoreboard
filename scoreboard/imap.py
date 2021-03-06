import imaplib
import logging
import socket  # not needed with Python 3.9
import ssl


log = logging.getLogger('scoreboard:poll')


# not needed with Python 3.9
class IMAP4(imaplib.IMAP4):
    def _create_socket(self, timeout):
        host = None if not self.host else self.host
        return socket.create_connection((host, self.port), timeout)

    def open(self, host='', port=imaplib.IMAP4_PORT, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        self.host = host
        self.port = port
        self.sock = self._create_socket(timeout)
        self.file = self.sock.makefile('rb')


def check(addr, port, cert=None, username=None, password=None, list=None, timeout=1, **kwargs):
    log.info(('IMAP: trying {addr}:{port}' + (' with {username}' if username else '')).format(addr=addr, port=port, username=username))

    up = False

    try:
        # imapc = imaplib.IMAP4(addr, port, timeout=timeout)
        imapc = IMAP4(addr, port, timeout=timeout)  # not needed with Python 3.9, replace with above

        up = True

        if cert:
            imapc.starttls(ssl_context=ssl.create_default_context(cafile=cert) if isinstance(cert, str) else ssl.create_default_context())

        if username is not None:
            imapc.login(username, password)

            imapc.select()

            if list is not None:
                up = up and imapc.list()[0] == 'OK' and imapc.list()[1] == list
    except imaplib.error:
        up = False
    finally:
        try:
            imapc.logout()
        except Exception:
            pass

    return up
