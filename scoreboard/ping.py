import logging
import os
import subprocess


log = logging.getLogger('scoreboard')


def check(addr, **kwargs):
    log.info(('ICMP: trying {addr}').format(addr=addr))

    up = False

    try:
        if os.name == 'nt':
            up = subprocess.call(['ping', '-w', '100', '-n', '4', addr], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) == 0
        else:
            up = subprocess.call(['ping', '-i0.1', '-c4', addr], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) == 0
    except subprocess.SubprocessError:
        up = False

    return up
