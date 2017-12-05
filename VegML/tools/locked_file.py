import os
import time
import logging

_LOCK_EXTN = ".LOCK"
_TIMEOUT = 0.8  # seconds

_LOG = logging.getLogger(__name__)


class LockingException(Exception):
    pass


def _obtain_lock_and_do(fn: callable):
    def decorator(self, *args, **kwargs):
        try:
            self._hold_on_lock(lock=self.lock1)
            self._set_lock(lock=self.lock1)
            self._hold_on_lock(lock=self.lock2)
            self._set_lock(lock=self.lock2)
            return fn(self, *args, **kwargs)
        finally:
            self._unset_lock(self.lock1)
            self._unset_lock(self.lock2)

    return decorator


class LockedFile:
    def __init__(self, filename, is_binary=False):
        self.filename = filename
        self.lock1 = filename + _LOCK_EXTN + "1"
        self.lock2 = filename + _LOCK_EXTN + "2"
        self.file_type = "b" if is_binary else "t"

    @staticmethod
    def _hold_on_lock(lock):
        while os.path.exists(lock):
            with open(lock, "r") as fp:
                t = float(fp.readline())
                if time.time() - t > _TIMEOUT:
                    _LOG.warning("Forcing unlock based on timeout")
                    LockedFile._unset_lock(lock)
                else:
                    time.sleep(_TIMEOUT / 10)

    @staticmethod
    def _set_lock(lock):
        with open(lock, "w") as fp:
            fp.write(str(time.time()))

    @staticmethod
    def _unset_lock(lock):
        try:
            os.remove(lock)
        except Exception:
            raise LockingException("Locking issue, please resolve.")

    @_obtain_lock_and_do
    def read(self):
        with open(self.filename, "r" + self.file_type) as fp:
            return fp.read()

    @_obtain_lock_and_do
    def write(self, data, append=False):
        open_type = "a" if append else "w"
        with open(self.filename, open_type + self.file_type) as fp:
            return fp.write(data)

    @_obtain_lock_and_do
    def read_and_write(self, callback: callable):
        with open(self.filename, "r" + self.file_type) as fp:
            file_contents = fp.read()
        with open(self.filename, "w" + self.file_type) as fp:
            return fp.write(callback(file_contents))
