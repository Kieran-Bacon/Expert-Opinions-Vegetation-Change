import time, uuid, threading, hashlib
from datetime import datetime, timedelta

class HiddenPages:

	threadLock = threading.Lock()
	pages = {}

	def all():
		for content in HiddenPages.pages.items():
			yield content 

	def newAddress(leading: str, following="") -> str:
		""" Generate a random address at some point of the tree

		Params:
			lead - A string that will appear at the beginning of the path
			following - A string that will appear after the randomly generated segment

		Returns:
			str - The address of the new location
		"""

		location = leading + uuid.uuid4().hex.upper() + following
		while location in HiddenPages.pages:
			location = leading + uuid.uuid4().hex.upper() + following

		HiddenPages.threadLock.acquire()
		HiddenPages.pages[location] = datetime.now() + timedelta(days=1)
		HiddenPages.threadLock.release()

		return location

	def validate(address: str) -> bool:
		if address not in HiddenPages.pages.keys():
			time.sleep(5)
			return False
		return True

	def remove(address: str) -> None:
		HiddenPages.threadLock.acquire()
		del HiddenPages.pages[address]
		HiddenPages.threadLock.release()