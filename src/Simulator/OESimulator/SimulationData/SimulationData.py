from .Scenario import Scenario
from .Units import Units
import numpy as np
from typing import Union
from dataclasses import dataclass
from .Timestamp import Timestamp
from .DataContainer import DataContainer
from .CONSTANTS import NOMINAL_TAUD

@dataclass
class SimulationData(object):
    """ Stores all the necessary information to simulate a virtual patient. Created by DataProcessor instance.
            Defined by __slots__ as the class only serves quick data access purposes.

            Args:
                t_start (int): Start time of the simulation horizon in Unix timestamp format [minutes].
                t_end (int): Start time of the simulation horizon in Unix timestamp format [minutes].
                scenario (Scenario): Scenario of the simulation.
                units (Units): Units of the simulated mathematical model.
                glucose_level (ndarray): Measured glucose levels (if available).
                meal (DataContainer): Meal consumptions in the simulation horizon.
                basal (DataContainer): Basal infusion rates in the simulation horizon.
                bolus (DataContainer): Bolus injections in the simulation horizon.
                rate_of_appearance (DataContainer): Generated rate of appearance values of the mathematical model in Ts sample time resolution.
                EGP (DataContainer): Generated EGP values of the mathematical model in Ts sample time resolution.
                GEZI (DataContainer): Generated GEZI values of the mathematical model in Ts sample time resolution.
                SI (DataContainer): Generated SI values of the mathematical model in Ts sample time resolution.
                iterator_range (range): Iterator for the simulation horizon.
                time_axis (list): Timepoints of the simulation horizon in Unix timestamp format [minutes].
                t_section (tuple): Stores the timepoints where the daily intervals change based on the circadian rhythm. Always at meal consumptions.
    """
    __slots__ = ['t_start', 'glucose_level', 'scenario','t_end',
                 'basal', 'bolus', 'meal','units','iterator_range',
                 'time_axis','time_range','rate_of_appearance',
                 't_sections','EGP','GEZI','SI',
                 'is_meal_up_to_date', 'Vg']

    def __init__(self, scenario: Scenario):
        """ Constructor.
            Required arguments: start time, end time in %d-%m-%Y %H:%M:%S format.
        """
        self.scenario = scenario
        self.t_start: int = self.scenario.start_time.as_int
        self.t_end: int = self.scenario.start_time.as_int
        self.units: Units = Units()
        self.glucose_level: np.ndarray = np.array([], dtype=float)
        self.meal: DataContainer = DataContainer(impulsive=True)
        self.basal: DataContainer = DataContainer(impulsive=False)
        self.bolus: DataContainer = DataContainer(impulsive=True)
        self.rate_of_appearance: DataContainer = DataContainer(impulsive=False)
        self.EGP: DataContainer = DataContainer(impulsive=False)
        self.GEZI: DataContainer = DataContainer(impulsive=False)
        self.SI: DataContainer = DataContainer(impulsive=False)
        self.iterator_range: range = range(0)
        self.time_axis: list = []
        self.time_range: range
        self.t_sections: tuple
        self.is_meal_up_to_date: bool = False
        self.Vg: float = 0.0


    @property
    def __dict__(self):
        return {s: getattr(self, s, None) for s in self.__slots__}

    def createRanges(self):
        self.time_range = np.arange(self.t_start, self.t_end+self.scenario.Ts,self.scenario.Ts )#range(self.t_start, self.t_end, self.scenario.Ts)
        self.iterator_range = range(1, len(self.time_range))

    def copy(self):
        """ Create a deep copy of the instance.

        Returns:
            SimulationData : Deep copy of the instance.

        """
        simulation_data = SimulationData(self.scenario)
        for attribute in self.__slots__:
            if hasattr(self, attribute):
                if isinstance(getattr(self, attribute), (np.ndarray, Units, Scenario)):
                    setattr(simulation_data, attribute, getattr(self, attribute).copy())
                else:
                    setattr(simulation_data, attribute, getattr(self, attribute))
        return simulation_data

    def initArrays(self):
        self.time_range = np.arange(self.t_start, self.t_end+self.scenario.Ts, self.scenario.Ts)
        self.iterator_range = range(1, len(self.time_range))
        self.time_axis = [x - self.t_start for x in list(self.time_range)]
        self.bolus.as_array = np.zeros(len(self.time_range))
        self.meal.as_array = np.zeros(len(self.time_range))
        self.basal.as_array = np.zeros(len(self.time_range))
        self.basal.as_timestamped_array = np.array([], dtype=np.float64)
        self.meal.as_timestamped_array = np.array([], dtype=np.float64)
        self.bolus.as_timestamped_array = np.array([], dtype=np.float64)


    def trim(self, new_start_time: Union[str,int] = None, new_end_time: Union[str,int] = None):
        """ Trims all the arrays, which are sampled in Ts resolution inbetween the new start and end time.

        Note:
            Serves for quick resimulation, if the patient parameters and inputs remain the same and only the start or the end time of the horizon is changed.

        Args:
            new_start_time (Union[str,int]): New start time of the simulation horizon.
            new_end_time (Union[str,int]): New end time of the simulation horizon.

        Examples:
            >>> print(self.basal.as_array.shape)
            >>> self.trim(self.scenario.start_time.as_int+60,self.scenario.end_time.as_int)
            >>> print(self.basal.as_array.shape)
            (577,)
            (565,)

        """
        if new_start_time is not None:
            self.scenario.start_time = Timestamp(new_start_time)
            self.scenario.end_time = Timestamp(new_end_time)
        if self.scenario.start_time.as_int<self.t_start:
            raise ValueError("Cannot apply trim if the new start time is outside of the current data horizon.")
        if self.scenario.end_time.as_int>self.t_end:
            raise ValueError("Cannot apply trim if the new end time is outside of the current data horizon.")
        trim_start_idx = int((self.scenario.start_time.as_int - self.t_start)/self.scenario.Ts)
        trim_end_idx = len(self.time_range)+int((self.scenario.end_time.as_int - self.t_end)/self.scenario.Ts)


        t_start = self.scenario.start_time.as_int
        t_end = self.scenario.end_time.as_int

        self.t_start = t_start
        self.t_end = t_end

        range_array = np.logical_and(np.subtract(self.basal.as_timestamped_array[:, 0], self.t_start) > 0.0,
                               np.subtract(self.basal.as_timestamped_array[:, 0], self.t_end) <= 0.0)
        if (np.any(range_array)):
            range_array = range_array[1:]
            range_array = np.append(range_array, True)
        else:
            range_array[0] = True
            self.basal.as_timestamped_array[0,0] = self.t_start
        self.basal.as_timestamped_array = self.basal.as_timestamped_array[range_array, :]

        range_array = np.logical_and(np.subtract(self.bolus.as_timestamped_array[:, 0], self.t_start) >= 0.0,
                               np.subtract(self.bolus.as_timestamped_array[:, 0], self.t_end) < 0.0)
        self.bolus.as_timestamped_array = self.bolus.as_timestamped_array[range_array, :]

        range_array = np.logical_and(np.subtract(self.meal.as_timestamped_array[:, 0], self.t_start-600) >= 0.0,
                               np.subtract(self.meal.as_timestamped_array[:, 0], self.t_end) < 0.0)
        self.meal.as_timestamped_array = self.meal.as_timestamped_array[range_array, :]

        time_range_idxs = trim_end_idx-trim_start_idx
        self.time_range = np.linspace(self.t_start, self.t_end, time_range_idxs)
        if self.glucose_level.size:
            self.glucose_level = np.column_stack((self.time_range,np.interp(self.time_range,self.glucose_level[:, 0],self.glucose_level[:,1])))
            # range_array = np.logical_and(np.subtract(self.glucose_level[:, 0], self.t_start) >= 0.0,
            #                        np.subtract(self.glucose_level[:, 0], self.t_end + t_pred) <= 0.0)
            # self.glucose_level = self.glucose_level[range_array, :]
            # time_range_idxs = self.glucose_level.shape[0]

        range_array = np.logical_and(np.subtract(self.meal.as_timestamped_array[:, 0], self.t_start) >= 0.0,
                               np.subtract(self.meal.as_timestamped_array[:, 0], self.t_end) < 0.0)
        range_boluses = np.logical_and(np.subtract(self.bolus.as_timestamped_array[:, 0], self.t_start) >= 0.0,
                                       np.subtract(self.bolus.as_timestamped_array[:, 0], self.t_end) < 0.0)

        self.scenario.no_meals = sum(range_array)
        self.scenario.no_boluses = sum(range_boluses)
        #range(self.t_start, self.t_end, self.scenario.Ts)

        self.bolus.as_array = self.bolus.as_array[trim_start_idx:trim_end_idx]
        self.basal.as_array = self.basal.as_array[trim_start_idx:trim_end_idx]
        self.iterator_range = range(1, len(self.time_range))
        self.time_axis = [x - list(self.time_range)[0] for x in list(self.time_range)]
        self.is_meal_up_to_date = False
