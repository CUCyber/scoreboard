import logging

import dns.exception
import dns.resolver


log = logging.getLogger('scoreboard')


def check(addr, port, hostname, type, answer=None, timeout=1, **kwargs):
    log.info(('DNS: trying {addr}:{port} for {type} {hostname}').format(addr=addr, port=port, type=type, hostname=hostname))

    up = False

    try:
        dnsc = dns.resolver.Resolver()
        dnsc.timeout = timeout

        dnsc.nameservers = [addr]
        dnsc.port = port

        response = dnsc.query(hostname, type)

        up = True

        if answer is not None:
            for rdata in response:
                if type == 'A' or type == 'AAAA':
                    up = rdata.address == answer
                elif type == 'PTR':
                    up = rdata.target == answer
                elif type == 'CNAME':
                    up = rdata.target == answer
                elif type == 'TXT':
                    if isinstance(answer, list):
                        up = rdata.strings == answer
                    else:
                        up = answer in rdata.strings
                elif type == 'SRV':
                    up = (rdata.priority, rdata.weight, rdata.port, str(rdata.target)) == answer
                elif type == 'SOA':
                    up = (str(rdata.mname), str(rdata.rname), rdata.serial, rdata.refresh, rdata.retry, rdata.expire, rdata.minimum) == answer

                if up:
                    break
    except dns.exception.DNSException:
        up = False

    return up
