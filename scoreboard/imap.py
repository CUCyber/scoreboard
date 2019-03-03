import imaplib
import logging
import socket # not needed once imaplib supports timeout
import ssl


log = logging.getLogger('scoreboard')


# not needed once imaplib supports timeout
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
        #imapc = imaplib.IMAP4(addr, port, timeout=timeout)
        imapc = IMAP4(addr, port) # not needed once imaplib supports timeout

        up = True

        if cert is not None:
            context = ssl.create_default_context()
            context.load_cert_chain(cert)

            imapc.starttls(ssl_context=context)

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
        except:
            pass

    return up
