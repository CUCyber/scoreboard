import http.client
import logging
import re
import socket
import ssl


log = logging.getLogger('scoreboard:poll')


def check(addr, port, cert=None, method=None, headers=None, host=None, url=None, body=None, regex=None, timeout=1, **kwargs):
    log.info(('HTTP: trying {addr}:{port}' + (' for {method} {url}' + (' at {host}' if host else '') if method else '')).format(addr=addr, port=port, method=method, url=url, host=host))

    up = False

    try:
        if cert:
            httpc = http.client.HTTPSConnection(addr, port, timeout=timeout, context=ssl.create_default_context(cafile=cert) if isinstance(cert, str) else ssl.create_default_context())
        else:
            httpc = http.client.HTTPConnection(addr, port, timeout=timeout)

        httpc.connect()

        up = True

        if method is not None:
            headers = headers if headers is not None else {}
            if host is not None:
                headers['host'] = host

            httpc.request(method, url, body, headers)

            if regex is not None:
                if isinstance(regex, bytes):
                    up = up and re.search(regex, httpc.getresponse().read())
                else:
                    up = up and re.search(regex, httpc.getresponse().read().decode())
    except (http.client.HTTPException, socket.error, AttributeError, UnicodeDecodeError):
        up = False
    finally:
        try:
            httpc.close()
        except Exception:
            pass

    return up
