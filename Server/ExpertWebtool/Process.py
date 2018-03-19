import time, threading, os, zipfile
from datetime import datetime, timedelta

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

from . import ROOT
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

		while True:
			backup_process = "/".join(ROOT.split("/")[:-1]) + "/backup.py"
			os.system("python3 {}".format(backup_process))
			time.sleep(60*60*24)


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

			time.sleep(60*60*24)