import time, threading
from datetime import datetime, timedelta

from ExpertWebtool.Helper import HiddenPages

class GarbageCollector(threading.Thread):
	""" Remove hidden pages when they time out """

	def run(self):
		while True:
			now = datetime.now()
			invalidAddress = []
			for address, genTime in HiddenPages.all():
				if genTime < now:
					invalidAddress.append(address)
				[HiddenPages.remove(addr) for addr in invalidAddress]
				time.sleep(60*60) # Sleep for an hour