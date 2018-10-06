import multiprocessing
import signal


sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)

manager = multiprocessing.Manager()
lock = manager.Lock()
scores = manager.dict()

signal.signal(signal.SIGINT, sigint)
