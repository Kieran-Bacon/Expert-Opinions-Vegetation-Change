"""
This module provides a simple implementation of portable and transparent file locking using a simple double locking
system. Includes timeouts
"""
import os
import time
import logging

_LOCK_EXTN = ".LOCK"
_TIMEOUT = 0.8  # seconds

_LOG = logging.getLogger(__name__)


class LockingException(Exception):
    """ Exception for locking issues """
    pass


def _obtain_lock_and_do(func: callable):
    """
    A simple decorator that obtains a lock on the files and then performs the action in the fn before releasing the lock

    Args:
        func: a class method, where the class has attributes self.lock1 and self.lock2 relating to 2 file paths.

    Returns:
        The decorated method
    """

    def decorator(self, *args, **kwargs):
        """ Placeholder docstring """
        try:
            self.hold_on_lock(lock=self.lock1)
            self.set_lock(lock=self.lock1)
            self.hold_on_lock(lock=self.lock2)
            self.set_lock(lock=self.lock2)
            return func(self, *args, **kwargs)
        finally:
            self.unset_lock(self.lock1)
            self.unset_lock(self.lock2)

    decorator.__doc__ = func.__doc__
    return decorator


class LockedFile:
    """
    A class that performs simple locked file operations with binary reading and writing.
    """

    def __init__(self, filename, is_binary=False):
        self.filename = filename
        self.lock1 = filename + _LOCK_EXTN + "1"
        self.lock2 = filename + _LOCK_EXTN + "2"
        self.file_type = "b" if is_binary else "t"

    @staticmethod
    def hold_on_lock(lock: str) -> None:
        """
        Enters the delay loop, and waits for the locks to become available before returning.

        Args:
            lock (str): a lock filename
        Returns:
            None
        """
        while os.path.exists(lock):
            with open(lock, "r") as file:
                start_time = float(file.readline())
                if time.time() - start_time > _TIMEOUT:
                    _LOG.warning("Forcing unlock based on timeout")
                    LockedFile.unset_lock(lock)
                else:
                    time.sleep(_TIMEOUT / 10)

    @staticmethod
    def set_lock(lock: str) -> None:
        """
        Writes the lock file
        Args:
            lock: the lock filename

        Returns:
            None

        """
        with open(lock, "w") as file:
            file.write(str(time.time()))

    @staticmethod
    def unset_lock(lock: str) -> None:
        """
        Removes the lock file
        Args:
            lock (str): The lock filename

        Returns:
            None
        """
        try:
            os.remove(lock)
        except Exception:
            raise LockingException("Locking issue, please resolve.")

    @_obtain_lock_and_do
    def read(self) -> (bytes or str):
        """
        A locked read operation that returns the output of file.read()

        Returns:
            The output of file.read() for the type of file that is used. Eg, bytes or str
        """
        with open(self.filename, "r" + self.file_type) as file:
            return file.read()

    @_obtain_lock_and_do
    def write(self, data: (bytes or str), append: bool = False) -> int:
        """
        A locked write operation that returns the output of file.write(data)
        Args:
            data (bytes or str): The data to write, either bytes or str
            append (bool): A flag to control the write mode of the file, append or not.

        Returns:
            The output of file.write(data), typically rhe number of bytes or characters written.
        """
        open_type = "a" if append else "w"
        with open(self.filename, open_type + self.file_type) as file:
            return file.write(data)

    @_obtain_lock_and_do
    def read_and_write(self, callback: callable) -> int:
        """
        Obtains the lock and executes the callback on the file contents writing them back to the file.

        callback needs to have signature:
            func(str) -> str or func(bytes) -> bytes depending on whether the file is opened in is_binary mode.

        Args:
            callback: a function. Detailed above.

        Returns:
            The number of bytes written

        """
        with open(self.filename, "r" + self.file_type) as file:
            file_contents = file.read()
        with open(self.filename, "w" + self.file_type) as file:
            return file.write(callback(file_contents))
