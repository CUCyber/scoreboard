import http.client
import re
import socket
import ssl


def check(addr, port, cert=None, method=None, headers=None, host=None, url=None, body=None, regex=None, **kwargs):
    up = False

    try:
        if cert is not None:
            context = ssl.create_default_context()
            context.load_cert_chain(cert)

            httpc = http.client.HTTPSConnection(addr, port, context=context)
        else:
            httpc = http.client.HTTPConnection(addr, port)

        httpc.connect()

        up = True

        if method is not None:
            headers = headers if headers is not None else {}
            if host is not None:
                headers['host'] = host

            httpc.request(method, url, body, headers)

            if regex is not None:
                up = up and re.search(regex, httpc.getresponse().read().decode())
    except (http.client.HTTPException, socket.error, AttributeError):
        up = False

    return up
