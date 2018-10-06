import subprocess


def check(addr, **kwargs):
    up = False

    try:
        up = subprocess.call(['ping', '-c4', addr], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT) == 0
    except subprocess.SubprocessError:
        up = False

    return up
