import multiprocessing
import signal


sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)

manager = multiprocessing.Manager()
lock = manager.Lock()
services = manager.list()
scores = manager.dict()
opts = manager.list()

signal.signal(signal.SIGINT, sigint)
