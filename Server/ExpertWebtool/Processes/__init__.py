from multiprocessing import Process

from .Backup import Backup
from .GarbageCollector import GarbageCollector

@classmethod
def run(cls):
    """ Run the processes housed in processes """
    GarbageCollector().start()

    p = Process(target=Backup.run)
    p.daemon = True
    p.start()