import os, uuid

from ExpertWebtool import CMOSTORAGE, TEMPSTORAGE
from ExpertRep import ClimateModelOutput

class CMOStore():

	_model_store = []

	def models():

		if not CMOStore._model_store:
			for modelName in os.listdir(CMOSTORAGE):
				if modelName == "Placeholder.ignore": continue
				model = ClimateModelOutput.load(os.path.join(CMOSTORAGE,modelName))
				CMOStore._model_store.append(model)

		return CMOStore._model_store

def tempStorage(fileContents, filename=None):

    if filename is None:
        filename = uuid.uuid4().hex.upper()

    while os.path.exists(os.path.join(TEMPSTORAGE, filename)):
	    # Ensure that the file is not overwritting another
        filename = uuid.uuid4().hex.upper()

    path = os.path.join(TEMPSTORAGE, filename)

    with open(path, "wb") as fileHandler:
        fileHandler.write(fileContents.read())

    return path

def emptyDirectory(directory: str) -> None:

	if os.path.isdir(directory):
		# Collect the contents of the directory
		contents = os.listdir(directory)
		for item in contents:
			path = os.path.join(directory,item)
			if os.path.isdir(path):
				# Recursively delete contents of sub-directory
				emptyDirectory(path)
				os.rmdir(path)
			else:
				# Remove file
				os.remove(path)