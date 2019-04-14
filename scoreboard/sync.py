import multiprocessing
import signal


sigint = signal.signal(signal.SIGINT, signal.SIG_IGN)

manager = multiprocessing.Manager()
interval = manager.Value('I', 60)
timeout = manager.Value('I', 1)
poll = manager.Value('I', 1)
show = manager.Value('b', True)
watching = manager.Value('b', False)
working = manager.Value('b', False)
lock = manager.Lock()
services = manager.list()
teams = manager.list()
scores = manager.dict()
opts = manager.list()
queue = manager.Queue()

signal.signal(signal.SIGINT, sigint)
