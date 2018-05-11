from multiprocessing import Process

from .Backup import Backup
from .GarbageCollector import GarbageCollector

def run():
    """ Run the processes housed in processes """
    GarbageCollector().start()

    p = Process(target=Backup.run)
    p.daemon = True
    p.start()