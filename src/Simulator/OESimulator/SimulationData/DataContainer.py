import numpy as np
from matplotlib import pyplot as plt
from typing import Union, List, Tuple

class DataContainer(object):
    """ Stores data in different formats (scalar, array (with Ts sampling), timestamped array).
            Defined by __slots__ as the class only serves quick data access purposes.
    """
    __slots__ = ['_scalar','_array','_timestamped_array','impulsive']
    def __init__(self, scalar: float = None, array: np.ndarray = None, timestamped_array: np.ndarray = None, impulsive: bool = False):
        """ Constructor.

        """
        if scalar is not None:
            self._scalar = scalar
        else:
            self._scalar = np.nan
        if array is not None:
            self._array = array
        else:
            self._array = np.array([], dtype=float)
        if timestamped_array is not None:
            self._timestamped_array = timestamped_array
        else:
            self._timestamped_array: np.ndarray = np.array([], dtype=np.float64)
        self.impulsive = impulsive

    @property
    def as_scalar(self):
        """ Gets and sets the variable in scalar format.

        Note:
             When array format exists, it returns the value corresponding to the current time point. It is relevant only as an attribute of the SimulationData.

        Returns:
            float : Returns data in scalar format.
        """
        return self._scalar

    @as_scalar.setter
    def as_scalar(self, value):
        self._scalar = value

    @property
    def as_array(self) -> np.ndarray:
        """ Gets and sets the variable in array format.

        Note:
             Sampled based on the Ts variable of the Scenario.

        Returns:
            float : Returns data in array format.
        """
        return self._array

    @as_array.setter
    def as_array(self, array):
        self._array = array


    @property
    def as_timestamped_array(self) -> np.ndarray:
        """ Gets and sets the variable in timestamped array format.

        Note:
             Times points are given in Unix timestamp format [minutes].

        Returns:
            float : Returns data in timestamped array format.

        Examples:
            >>> print(self.as_timestamped_array)
            [[26679390       30       40]
             [26679540       15       10]]
        """
        return self._timestamped_array

    @as_timestamped_array.setter
    def as_timestamped_array(self, array):
        self._timestamped_array = array

    @property
    def __dict__(self):
        return {s: getattr(self, s, None) for s in self.__slots__}

    def copyTimestampedArrayToArray(self, start_time, Ts, position):
        inputs_in_horizon = (self._timestamped_array[:,0]-start_time)>=0
        indexes = np.ceil((self._timestamped_array[inputs_in_horizon, 0] - start_time) / Ts).astype(int)
        if np.any(inputs_in_horizon):
            if(self.impulsive):
                self._array[indexes] = self._timestamped_array[inputs_in_horizon, position]
            else:
                prev_i = 0
                b_i = 0
                if (len(indexes) < 2):
                    # If only 1 basal value is found in the raw data file for the current horizon, this value used until the end
                    self._array[0:] = self._timestamped_array[0, position]
                else:
                    # If more than 1 basal value found, each basal value is used up until the time point where the next basal is defined
                    for bolus_i in indexes[1:]:
                        self._array[prev_i:bolus_i] = self._timestamped_array[b_i, position]
                        b_i = b_i + 1
                        prev_i = bolus_i
                    # The last basal value is used until the end
                    self._array[prev_i:] = self._timestamped_array[b_i, position]


    def copy(self):
        """ Create a deep copy of the instance.

        Returns:
            DataContainer : Deep copy of the instance.

        """
        data_container = DataContainer()
        for attribute in self.__slots__:
            if isinstance(getattr(self, attribute), np.ndarray):
                setattr(data_container, attribute, getattr(self, attribute).copy())
            else:
                setattr(data_container, attribute, getattr(self, attribute))
        return data_container

    def plot(self):
        """ If array or timestamped_array exists it plots the stored data.

            Note:
                Array or timestamped_array format needed.

            Examples:
                >>> self.plot()
        """
        if self._timestamped_array.size:
            for row in self._timestamped_array:
                plt.arrow(row[0], 0, 0,row[1])
        elif self._array.size:
            plt.plot(self._array)
        plt.show()

