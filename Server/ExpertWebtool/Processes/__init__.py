from .Backup import Backup
from .GarbageCollector import GarbageCollector

def run():
    """ Run the processes housed in processes """
    #Backup.start()
    GarbageCollector().start()