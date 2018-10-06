import subprocess


def check(addr, **kwargs):
    up = False

    try:
        up = subprocess.call(['ping', '-c4', addr]) == 0
    except subprocess.SubprocessError:
        up = False

    return up
