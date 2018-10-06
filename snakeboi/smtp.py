import random
import smtplib
import ssl
import string


def check(addr, port, cert=None, username=None, password=None, from_=None, to=None, **kwargs):
    up = False

    nonce = ''.join(random.choice(string.ascii_letters) for _ in range(16))

    try:
        smtpc = smtplib.SMTP()
        smtpc.connect(addr, port)
        smtpc.ehlo('{}.com'.format(nonce))

        if cert is not None:
            context = ssl.create_default_context()
            context.load_cert_chain(cert)

            smtpc.starttls(context=context)

        if username is not None:
            smtpc.login(username, password)

        if from_ is not None:
            smtpc.mail(from_)
            smtpc.rcpt(to)

        smtpc.quit()

        up = True
    except smtplib.SMTPException:
        up = False

    return up
