import multiprocessing
import signal


sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)

manager = multiprocessing.Manager()
scores = manager.dict()

signal.signal(signal.SIGINT, sigint)
