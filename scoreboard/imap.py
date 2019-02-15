import imaplib
import logging
import ssl


log = logging.getLogger('scoreboard')


def check(addr, port, cert=None, username=None, password=None, list=None, timeout=1, **kwargs):
    log.info(('IMAP: trying {addr}:{port}' + (' with {username}' if username else '')).format(addr=addr, port=port, username=username))

    up = False

    try:
        #imapc = imaplib.IMAP4(addr, port, timeout=timeout)
        imapc = imaplib.IMAP4(addr, port)

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
