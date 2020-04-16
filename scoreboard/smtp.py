import logging
import random
import smtplib
import ssl
import string


log = logging.getLogger('scoreboard')


def check(addr, port, cert=None, username=None, password=None, from_=None, to=None, timeout=1, **kwargs):
    log.info(('SMTP: trying {addr}:{port}' + (' with {username}' if username else '') + (' for {from_} -> {to}' if from_ else '')).format(addr=addr, port=port, username=username, from_=from_, to=to))

    up = False

    nonce = ''.join(random.choice(string.ascii_letters) for _ in range(16))

    try:
        smtpc = smtplib.SMTP(timeout=timeout)
        smtpc.connect(addr, port)
        smtpc.ehlo('{}.com'.format(nonce))

        if cert:
            smtpc.starttls(context=ssl.create_default_context(cafile=cert) if isinstance(cert, str) else ssl.create_default_context())

        if username is not None:
            smtpc.login(username, password)

        if from_ is not None:
            smtpc.mail(from_)
            smtpc.rcpt(to)

        smtpc.quit()

        up = True
    except smtplib.SMTPException:
        up = False
    finally:
        try:
            smtpc.quit()
        except Exception:
            pass

    return up
