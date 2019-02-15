import logging
import poplib
import socket
import ssl


log = logging.getLogger('scoreboard')


def check(addr, port, cert=None, username=None, password=None, list=None, **kwargs):
    log.info(('POP3: trying {addr}:{port}' + (' with {username}' if username else '')).format(addr=addr, port=port, username=username))

    up = False

    try:
        popc = poplib.POP3(addr, port, timeout=1)

        if cert is not None:
            context = ssl.create_default_context()
            context.load_cert_chain(cert)

            popc.stls(context=context)

        if username is not None:
            popc.user(username)
            popc.pass_(password)

            if list is not None:
                up = popc.list()[0] == 'OK' and popc.list()[1] == list
    except (poplib.error_proto, socket.error):
        up = False
    finally:
        try:
            popc.quit()
        except:
            pass

    return up
