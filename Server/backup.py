import os, zipfile
from datetime import datetime

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

ROOT_name = os.path.dirname(os.path.realpath(__file__)).split("/")[-2]
ROOT_directory = "/".join(os.path.dirname(os.path.realpath(__file__)).split("/")[:-1])

def zipdata(filename: str) -> None:
    """ Zip up the information of the server """

    # Create the output file
    zippedFile = zipfile.ZipFile(filename, "w", compression=zipfile.ZIP_DEFLATED)

    # Walk over the directory and save all files
    for abspath, dirnames, filenames in os.walk(ROOT_directory):
        local = abspath[abspath.index(ROOT_name):]
        [zippedFile.write(os.path.join(abspath, name), os.path.join(local, name)) for name in filenames]

    # Close the zip file
    zippedFile.close()

# Create representation of google drive
drive = GoogleDrive(GoogleAuth())

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

# Removed the zipped file created
os.remove(filename)