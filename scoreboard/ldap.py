import logging

import ldap


log = logging.getLogger('scoreboard')


def check(addr, port, cert=None, dn=None, password=None, base=None, cn=None, **kwargs):
    log.info(('LDAP: trying {addr}:{port}' + (' with {dn}' if dn else '') + (' for {base} cn={cn}' if base else '')).format(addr=addr, port=port, dn=dn, base=base, cn=cn))

    up = False

    try:
        ldapc = ldap.initialize('ldap://{}:{}'.format(addr, port))
        ldapc.set_option(ldap.OPT_NETWORK_TIMEOUT, 1)

        up = True

        if cert is not None:
            ldapc.set_option(ldap.OPT_X_TLS_CERTFILE, cert)
            ldapc.start_tls_s()

        if dn is not None:
            ldapc.simple_bind_s(dn, password)

        if base is not None:
            results = ldapc.search_s(base, ldap.SCOPE_ONELEVEL, '(cn=' + cn + ')', ['cn'])

            up = up and results[0][1]['cn'][0].decode() == cn
    except (ldap.LDAPError, IndexError, KeyError):
        up = False
    finally:
        try:
            ldapc.unbind_s()
        except:
            pass

    return up
