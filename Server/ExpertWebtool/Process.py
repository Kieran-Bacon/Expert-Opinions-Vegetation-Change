import time, threading
from datetime import datetime, timedelta

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from .Helper import HiddenPages

class GarbageCollector(threading.Thread):
    """ Remove hidden pages when they time out """

    def run(self):
        while True:
            now = datetime.now()
            invalidAddress = []
            for address, genTime in HiddenPages.all():
                if genTime < now:
                    print("addredd removed", address)
                    invalidAddress.append(address)
            [HiddenPages.remove(addr) for addr in invalidAddress]
            time.sleep(60*60) # Sleep for an hour

class Backup(threading.Thread):
    """ Move site information into a long term versioning solution """

    def run(self):

        drive = GoogleDrive(GoogleAuth().LocalWebserverAuth())

        siteDB = drive.CreateFile({"title":""})
        siteDB.SetContentString("")
        siteDB.Upload()

        while True:
            # Create the file on the target and push
            time.sleep(60*60*24)