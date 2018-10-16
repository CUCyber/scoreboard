import subprocess


def check(addr, **kwargs):
    log.info('ICMP: trying {addr}', addr=addr)

    up = False

    try:
        up = subprocess.call(['ping', '-i0.1', '-c4', addr], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) == 0
    except subprocess.SubprocessError:
        up = False

    return up
