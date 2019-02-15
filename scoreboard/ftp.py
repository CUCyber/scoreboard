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
        if cert is not None:
            context = ssl.create_default_context()
            context.load_cert_chain(cert)

            ftpc = ftplib.FTP_TLS(timeout=timeout, context=context)
        else:
            ftpc = ftplib.FTP(timeout=timeout)

        ftpc.connect(addr, port)

        up = True

        if username is not None:
            ftpc.login(username, password)

        if file is not None:
            up = file in ftpc.nlst()

            buf = io.StringIO()
            ftpc.retrlines('RETR {}'.format(file), buf.write)

            if contents is not None:
                up = up and buf.getvalues() == contents

        if dne is not None:
            up = up and nonce not in ftpc.nlst()
    except ftplib.all_errors:
        up = False
    finally:
        try:
            ftpc.quit()
        except:
            pass

    return up
