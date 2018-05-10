import os, time, threading, zipfile

from datetime import datetime

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from ExpertWebtool import ROOT

class Backup(threading.Thread):
    """ Move site information into a long term versioning solution """

    @staticmethod
    def run():

        """

        while True:
            backup_process = "/".join(ROOT.split("/")[:-1]) + "/backup.py"
            os.system("python3 {}".format(backup_process))
            time.sleep(60*60*24)
        """

        # Create representation of google drive
        GoogleAuth.DEFAULT_SETTINGS['client_config_file'] = os.path.join(ROOT,"Processes","client_secrets.json")
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

            time.sleep(60*60*24)