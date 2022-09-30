import datetime
from .CONSTANTS import *
import calendar as cal
from typing import Union



class Timestamp(object):
    """ Stores time information in three alternative formats (Unix timestamp [minutes], string, datetime)
            Defined by __slots__ as the class only serves quick data access purposes.

            Note:
                Can be initialized in string or Unix timestamp [minutes] format. It automatically converts to the rest of the
                formats.

            Raises:
                ValueError: If the provided string format is not %d-%m-%Y %H:%M:%S.
    """
    __slots__ = ['_str','_int','_datetime']
    def __init__(self, timestamp: Union[str,int] = None):
        """ Constructor.

        """
        if isinstance(timestamp, str):
            try:
                self._str = timestamp
                self._datetime = datetime.datetime.strptime(timestamp, DATETIME_FORMAT)
                self._int: int = int(
                    cal.timegm(datetime.datetime.strptime(timestamp, DATETIME_FORMAT).timetuple()) / 60.0)
            except ValueError:
                raise ValueError("Incorrect date format, should be %d-%m-%Y %H:%M:%S or int [minutes]")
        if isinstance(timestamp, int):
            self._int = timestamp
            self._datetime = datetime.datetime.utcfromtimestamp(self._int*60)
            self._str = self._datetime.strftime(DATETIME_FORMAT)

    def copy(self):
        """ Create a deep copy of the instance.

        Returns:
            Timestamp : Deep copy of the instance.

        """
        timestamp = Timestamp()
        for attribute in self.__slots__:
            if hasattr(self, attribute):
                setattr(timestamp, attribute, getattr(self, attribute))
        return timestamp


    @property
    def as_int(self):
        """ Gets and sets timestamp based on Unix timestamp [minutes] format.

        Returns:
            int :  Timestamp in Unix timestamp [minutes] format.

        Examples:
            >>> print(Timestamp("22-09-2020 10:20:00").as_int)
            26679500

        """
        return self._int

    @as_int.setter
    def as_int(self, timestamp):
        self._int = timestamp
        self._datetime = datetime.datetime.utcfromtimestamp(self._int*60)
        self._str = self._datetime.strftime(DATETIME_FORMAT)

    @property
    def as_str(self):
        """ Gets and sets timestamp based on string format.

        Returns:
            str : Timestamp in string format.

        Examples:
            >>> print(Timestamp(26679500).as_str)
            22-09-2020 10:20:00

        """
        return self._str

    @as_str.setter
    def as_str(self, timestamp):
        self._str = timestamp
        try:
            self._datetime = datetime.datetime.strptime(timestamp, DATETIME_FORMAT)
            self._int: int = int(
                cal.timegm(datetime.datetime.strptime(timestamp, DATETIME_FORMAT).timetuple()) / 60.0)
        except ValueError:
            raise ValueError("Incorrect date format, should be %d-%m-%Y %H:%M:%S or int [minutes]")

    @property
    def as_datetime(self):
        """ Gets and sets timestamp based on datetime object.

        Returns:
            datetime : Timestamp in datetime format.

        Examples:
            >>> print(Timestamp(26679500).as_datetime)
            2020-09-22 10:20:00

        """
        return self._datetime

    @as_datetime.setter
    def as_datetime(self, timestamp):
        try:
            self._datetime = timestamp
            self._str = self._datetime.strftime(DATETIME_FORMAT)
            self._int: int = int(
                cal.timegm(datetime.datetime.strptime(self._str, DATETIME_FORMAT).timetuple()) / 60.0)
        except ValueError:
            raise ValueError("Incorrect date format, should be %d-%m-%Y %H:%M:%S or int [minutes]")


    @property
    def __dict__(self):
        return {s: getattr(self, s, None) for s in self.__slots__}