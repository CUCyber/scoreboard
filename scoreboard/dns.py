import dns.exception
import dns.resolver


def check(addr, port, hostname, type, answer=None, **kwargs):
    up = False

    try:
        dnsc = dns.resolver.Resolver()

        dnsc.nameservers = addr
        dnsc.port = port

        answer = dnsc.query(hostname, type)

        up = True

        if answer is not None:
            up = answer[0].items[0] == answer
    except dns.exception.DNSException:
        up = False

    return up
