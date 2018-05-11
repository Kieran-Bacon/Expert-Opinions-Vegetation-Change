import os, time, threading, zipfile, warnings
import logging
from datetime import datetime

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from ExpertWebtool import ROOT

class Backup(threading.Thread):
    """ Move site information into a long term versioning solution """

    @staticmethod
    def run():
        # Hide Google's incorrect requirement error
        logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)

        # Create representation of google drive
        drive = GoogleDrive(GoogleAuth())

        def zipdata(filename: str) -> None:
            """ Zip up the information of the server """

            # Generate the path to the project TODO: check if this is entire project or server
            directoryName = ROOT.split("/")[-3]
            codeDestination = "/".join(ROOT.split("/")[:-2])

            # Create the output file
            zippedFile = zipfile.ZipFile(filename, "w", compression=zipfile.ZIP_DEFLATED)

            # Walk over the directory and save all files
            for abspath, dirnames, filenames in os.walk(codeDestination):
                local = abspath[abspath.index(directoryName):]
                [zippedFile.write(os.path.join(abspath, name), os.path.join(local, name)) for name in filenames]

            # Close the zip file
            zippedFile.close()

        while True:
            # Construct the file name safely
            filename = "".join([datetime.now().strftime("%Y-%m-%d"), ".zip"])

            # Zip code
            zipdata(filename)

            # Create and link the file
            file1 = drive.CreateFile()
            file1.SetContentFile(filename)
            file1['title'] = filename

            # well you should know what this is...
            file1.Upload()

            # Remove local file after upload
            os.remove(filename)

            # Sleep process
            time.sleep(60*60*24)