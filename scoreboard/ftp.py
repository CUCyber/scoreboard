import ftplib
import io
import logging
import random
import ssl
import string


log = logging.getLogger('scoreboard')


def check(addr, port, cert=None, username=None, password=None, file=None, contents=None, dne=None, timeout=1, **kwargs):
    log.info(('FTP: trying {addr}:{port}' + (' with {username}' if username else '') + (' for {file}' if file else '')).format(addr=addr, port=port, username=username, file=file))

    up = False

    if dne is not None:
        nonce = ''.join(random.choice(string.ascii_letters) for _ in range(16)) + dne

    try:
        if cert:
            ftpc = ftplib.FTP_TLS(timeout=timeout, context=ssl.create_default_context(cafile=cert) if isinstance(cert, str) else ssl.create_default_context())
        else:
            ftpc = ftplib.FTP(timeout=timeout)

        ftpc.connect(addr, port)

        up = True

        if username is not None:
            ftpc.login(username, password)

        if file is not None:
            up = up and file in ftpc.nlst()

            if isinstance(contents, str):
                buf = io.StringIO()
                ftpc.retrlines('RETR {}'.format(file), buf.write)
            else:
                buf = io.BytesIO()
                ftpc.retrbinary('RETR {}'.format(file), buf.write)

            if contents is not None:
                up = up and buf.getvalues() == contents

        if dne is not None:
            up = up and nonce not in ftpc.nlst()
    except ftplib.all_errors:
        up = False
    finally:
        try:
            ftpc.quit()
        except Exception:
            pass

    return up
