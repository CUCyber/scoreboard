import contextlib
import logging
import socket


log = logging.getLogger('scoreboard')


def check(addr, port, **kwargs):
    log.info(('TCP: trying {addr}:{port}').format(addr=addr, port=port))

    up = False

    try:
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            up = sock.connect_ex((addr, port)) == 0
    except OSError:
        up = False

    return up
