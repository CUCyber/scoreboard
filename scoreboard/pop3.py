import logging
import poplib
import socket
import ssl


log = logging.getLogger('scoreboard:poll')


def check(addr, port, cert=None, username=None, password=None, list=None, timeout=1, **kwargs):
    log.info(('POP3: trying {addr}:{port}' + (' with {username}' if username else '')).format(addr=addr, port=port, username=username))

    up = False

    try:
        popc = poplib.POP3(addr, port, timeout=timeout)

        if cert:
            popc.stls(context=ssl.create_default_context(cafile=cert) if isinstance(cert, str) else ssl.create_default_context())

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
        except Exception:
            pass

    return up
