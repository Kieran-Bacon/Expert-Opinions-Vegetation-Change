import time, threading, os, zipfile
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

	def zipdir(dirPath=None, zipFilePath=None, includeDirInZip=True):

		if not zipFilePath:
			zipFilePath = dirPath + ".zip"
		if not os.path.isdir(dirPath):
			raise OSError("dirPath argument must point to a directory. "
				"'%s' does not." % dirPath)
		parentDir, dirToZip = os.path.split(dirPath)
		#Little nested function to prepare the proper archive path
		def trimPath(path):
			archivePath = path.replace(parentDir, "", 1)
			if parentDir:
				archivePath = archivePath.replace(os.path.sep, "", 1)
			if not includeDirInZip:
				archivePath = archivePath.replace(dirToZip + os.path.sep, "", 1)
			return os.path.normcase(archivePath)

		outFile = zipfile.ZipFile(zipFilePath, "w",
			compression=zipfile.ZIP_DEFLATED)
			
		for (archiveDirPath, dirNames, fileNames) in os.walk(dirPath):
			for fileName in fileNames:
				filePath = os.path.join(archiveDirPath, fileName)
				outFile.write(filePath, trimPath(filePath))
			#Make sure we get empty directories as well
			if not fileNames and not dirNames:
				zipInfo = zipfile.ZipInfo(trimPath(archiveDirPath) + "/")
				#some web sites suggest doing
				#zipInfo.external_attr = 16
				#or
				#zipInfo.external_attr = 48
				#Here to allow for inserting an empty directory.  Still TBD/TODO.
				outFile.writestr(zipInfo, "")
		outFile.close()
	
	
	def run(self):

		drive = GoogleDrive(GoogleAuth().LocalWebserverAuth())



		while True:
			# Create the file on the target and push
			time.sleep(60*60*24)
			now = datetime.datetime.now()
			date = now.strftime("%Y-%m-%d")
			zipdir('/root',date+'.zip')

			file1 = drive.CreateFile()
			file1.SetContentFile(date+'.zip')
			file1['title'] = date+'.zip'



			file1.Upload()

			print('Created file %s with mimeType %s' % (file1['title'],
			file1['mimeType']))