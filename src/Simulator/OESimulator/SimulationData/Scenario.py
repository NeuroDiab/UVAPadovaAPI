from .Units import Units
from .Position import Position
from .ParamsT1DMS import ParamsT1DMS
import calendar as cal
import datetime
import numpy as np
from matplotlib import pyplot as plt
from typing import Union
from typing import Tuple
from .Timestamp import Timestamp
from .CONSTANTS import *

class Scenario:
    """ Scenario class provides a storage and interface for the simulation related information (time points of the simulation horizon, meal, insulin inputs, units, sampling time, etc.).
            Defined by __slots__ as the class only serves quick data access purposes.

            Args:
                scenario_setting (str): Scenario setting: manual/DT/azure.
                Ts (int): sampling time (Default: 5 minutes)
                basal_insulin (float): Current basal insulin input.
                bolus_insulin (float): Current bolus insulin input.
                rate_of_appearance (float): Current rate of appearance input.
                no_boluses (int): Number of boluses in the window.
                no_meals (int): Number of meals in the window.
                units (Units): Units of the scenario.
                position (Position): Positions of the input values in a multidimensional array.
                start_time (Timestamp): Start time of the scenario.
                end_time (Timestamp): End time of the scenario str/int.
                t_start (float): Start time of the scenario (unix time, minute).
                t_end (float): End time of the scenario (unix time, minute).
                manual_meals (ndarray): User defined meal scheme. 2D array [timepoint, cho content, absorption time constant]
                manual_boluses (ndarray): User defined bolus scheme. 2D array [timepoint, insulin content]
                manual_basal_insulin (ndarray): User defined basal insulin scheme. 2D array [timepoint, insulin rate]
                verbose (bool): Prints information upon the creation of the Scenario and warning messages are activated.
                params_t1dms (ParamsT1DMS): Stores the Uva/Padova Matlab simulator related parameters.

            Examples:
                >>> scenario = Scenario(0,1000,"manual",verbose=True)
                ---------------------------
                Current scenario:
                Start time: 01-01-1970 00:00:00
                End time: 01-01-1970 16:40:00
                Sampling time: 5
                Scenario setting: manual
                ---------------------------

                >>> scenario = Scenario("22-09-2020 07:00:00", "22-09-2020 19:00:00", "emulated", verbose=True)
                ---------------------------
                Current scenario:
                Start time: 22-09-2020 07:00:00
                End time: 22-09-2020 19:00:00
                Sampling time: 5
                Scenario setting: emulated
                ---------------------------

    """
    __slots__ = ['Ts', 'basal_insulin','bolus_insulin','no_meals',
                 'no_boluses','units','position','start_time',
                 'end_time','manual_meals','manual_boluses',
                 'manual_basal_insulin','scenario_setting',
                 'rate_of_appearance','verbose','params_t1dms',
                 'cho','ident_horizon','t_pred']

    def __init__(self, start_time: Union[str,int] = "%d-%m-%Y %H:%M:%S or integer",
                 end_time: Union[str,int] = "%d-%m-%Y %H:%M:%S or integer", scenario_setting: str = "", verbose: bool = False):
        """ Constructor.

                Args:
                    start time : %d-%m-%Y %H:%M:%S format or (int) minutes
                    end time : %d-%m-%Y %H:%M:%S format or (int) minutes
                    scenario_setting : manual/Dt/azure

                Returns:
                    Scenario

                Raises:
                    KeyError : If the provided scenario settings is not a valid setting.
                    ValueError : If the start_time format is not valid.
                    ValueError : If the end_time format is not valid.

        """
        possible_settings = ["manual","azure","DT","emulated","t1dms"]
        setting_valid = False
        for possible_setting in possible_settings:
             if scenario_setting == possible_setting:
                 setting_valid = True
                 self.scenario_setting = scenario_setting
        if not setting_valid:
            raise KeyError("Unknown scenario setting: %s encountered. Consider: manual/DT/azure/emulated")
        if self.scenario_setting == "t1dms":
            self.params_t1dms: ParamsT1DMS = ParamsT1DMS()

        self.start_time = Timestamp(start_time)
        self.end_time = Timestamp(end_time)
        self.Ts: int = 5
        self.basal_insulin: float = 0.0
        self.bolus_insulin: float = 0.0
        self.rate_of_appearance: float = 0.0
        self.no_meals: int = 0
        self.no_boluses: int = 0
        self.units: Units = Units()
        self.position: Position = Position()
        self.manual_meals: np.ndarray = np.array([], dtype=float)
        self.manual_boluses: np.ndarray = np.array([], dtype=float)
        self.manual_basal_insulin: np.ndarray = np.array([], dtype=float)
        self.scenario_setting: str = scenario_setting
        self.verbose = verbose
        if self.verbose:
            print(self)

    def __repr__(self):
        """ Scenario representation.
        """
        lines = "---------------------------\n"
        representation = "Current scenario:\nStart time: %s \nEnd time: %s \nSampling time: %s\nScenario setting: %s \n" %\
                         (self.start_time.as_str, self.end_time.as_str, self.Ts, self.scenario_setting)
        return lines+representation+lines

    @property
    def __dict__(self):
        return {s: getattr(self, s, None) for s in self.__slots__}

    # def __copy__(self):
    #     scenario = Scenario(self.start_time, self.end_time, self.scenario_setting)
    #     for attribute in self.__slots__:
    #         if hasattr(self, attribute):
    #             setattr(scenario, attribute, getattr(self, attribute))
    #     return scenario

    def setManualMealScheme(self, meal_times: Union[Tuple[float, ...], Tuple[str, ...]], meal_values: Tuple[float, ...], time_constants: Tuple[float, ...] = None, unit: str = "g") -> np.ndarray:
        """ Creates the 2D numpy array for the meal scheme.

            Note:
                If the timepoints are strings, it converts to unix timestamps.
                Checks the validity of input arrays.
                Sets the no_meals attribute based on the number of meals in the input arrays.

            Args:
                meal_times : User defined time points of the meals.
                meal_values : User defined meal values.
                unit : Unit of the meal values.

            Returns:
                ndarray : 2D numpy array containing the combined time points and values.

            Examples:
                >>> self.setManualMealScheme(meal_times=("22-09-2020 06:00:00", "22-09-2020 12:00:00", "22-09-2020 18:00:00"),meal_values=(10, 40, 30),time_constants=(30,30,40))
                Warning: You have inputs defined before the start time of the scenario.
        """
        if self.scenario_setting == "emulated":
            meal_times = self.__strTimeToMinutes(meal_times)
        self.checkScheme(meal_times, meal_values)
        if time_constants is None:
           time_constants = np.multiply(NOMINAL_TAUD, np.ones(len(meal_times), ))
        self.units.meal = unit
        self.manual_meals = np.column_stack((meal_times, meal_values, time_constants)).astype(float)
        self.no_meals = np.sum(np.array(meal_values) > 0)
        return self.manual_meals

    def setManualBolusScheme(self, bolus_times: Union[Tuple[float, ...], Tuple[str, ...]], bolus_values: Tuple[float, ...], unit: str = "U") -> np.ndarray:
        """ Creates the 2D numpy array for the bolus scheme.

            Note:
                If the timepoints are strings, it converts to unix timestamps.
                Checks the validity of input arrays.
                Sets the no_boluses attribute based on the number of meals in the input arrays.

            Args:
                bolus_times : User defined time points of the boluses.
                bolus_values : User defined bolus values.
                unit : Unit of the bolus values.

            Returns:
                ndarray : 2D numpy array containing the combined time points and values.

            Examples:
                >>> self.setManualBolusScheme(bolus_times=("22-09-2020 07:00:00", "22-09-2020 12:00:00", "22-09-2020 18:00:00"),bolus_values=(2, 4, 3))
        """
        if self.scenario_setting == "emulated":
            bolus_times = self.__strTimeToMinutes(bolus_times)
        self.checkScheme(bolus_times, bolus_values)
        self.units.bolus = unit
        self.manual_boluses = np.column_stack((bolus_times, bolus_values)).astype(float)
        self.no_boluses = np.sum(np.array(bolus_values) > 0)
        return self.manual_boluses

    def setManualBasalInsulin(self, basal_insulin_values: Union[float, Tuple[float]] = 0.0, basal_insulin_times: Tuple[float] = None, unit: str = r"U/hr"):
        """ Creates 2D numpy array for the basal insulin.

            Note:
                If a scalar basal rate is provided without time point, it is assumed that the basal rate is active since 0 unix time.

            Args:
                basal_insulin_values : User defined basal rate.
                basal_insulin_times : User defined time point, when the basal rate is activated.
                unit : Unit of the basal rate.

            Examples:
                >>> self.setManualBasalInsulin(1.0,unit=r"U/hr")
        """
        self.units.basal = unit
        if basal_insulin_times is None:
            if basal_insulin_values < 0.0:
                raise ValueError("Basal insulin has to be >= 0.")
            self.manual_basal_insulin = np.array([[self.start_time.as_int, basal_insulin_values]]).astype(float)
        else:
            self.manual_basal_insulin = np.column_stack((basal_insulin_times, basal_insulin_values)).astype(float)

    def shift(self,time_shift: int = None, next_meal: float = None,next_taud: float = None, next_bolus: float = None, next_basal_insulin: float = None):
        """ Shifts the scenario by the user defined time.

        Note:
            Default of Ts shift is assumed without any modification on the CHO and insulin scheme.

        Args:
            time_shift : The time [minutes] by which the scenario is shifted. Default value of Ts.
            next_meal : CHO content of the meal in the shifted time step.
            next_taud : Absorption time constant of the meal in the shifted time step.
            next_bolus : Bolus insulin in the shifted time step.
            next_basal_insulin : Modified basal rate from the shifted time step.

        """
        if time_shift is not None:
            self.end_time.as_int = self.end_time.as_int + time_shift
            self.start_time.as_int = self.start_time.as_int + time_shift
        else:
            self.end_time.as_int = self.end_time.as_int + self.Ts
            self.start_time.as_int = self.start_time.as_int + self.Ts
        if next_basal_insulin is not None:
            self.basal_insulin = next_basal_insulin
        if next_meal is not None:
            if next_taud is not None:
                self.manual_meals = np.vstack([self.manual_meals, [self.end_time.as_int, next_meal, next_taud]])
            else:
                self.manual_meals = np.vstack([self.manual_meals, [self.end_time.as_int, next_meal, NOMINAL_TAUD]])
        if next_bolus is not None:
            self.manual_boluses = np.vstack([self.manual_boluses, [self.end_time.as_int, next_bolus]])


    def checkScheme(self, time_array: Tuple[float, ...], value_scheme: Tuple[float, ...]) -> bool:
        """ Checks the validity of the used defined arrays, the following criterias have to be met.

                Args:
                    time_array : Time points of the input array.
                    value_scheme : Values of the input array.

                Returns:
                    bool : True if the scheme is properly defined.

                Raises:
                    Value error : ERROR: The time and value array have to be of equal length.
                    Value error : ERROR: Values have to be >= 0.
                    Value error : WARNING: Time points defined before the start time of the scenario.
                    Value error : WARNING: Time points defined after the end time of the scenario.
                    Value error : WARNING: Time points have to be strictly monotonically increasing.
        """
        if len(time_array) != len(value_scheme):
            raise ValueError("Defined time array and value array have different lengths, they have to be of equal length.")
        if sum(value < 0 for value in value_scheme):
            raise ValueError("Defined values have to be >= 0.")
        if self.verbose:
            if np.sum((self.end_time.as_int-np.asarray(time_array)) < 0):
                print(COLOR_WARNING + "Warning: You have inputs defined after the end time of the scenario." + COLOR_END)
            if np.sum((np.asarray(time_array)-self.start_time.as_int) < 0):
                print(COLOR_WARNING + "Warning: You have inputs defined before the start time of the scenario." + COLOR_END)
        # if sum(time < 0 for time in time_array):
        #     raise ValueError("Time points have to be >= 0.")
        if self.scenario_setting != "emulated":
            time_differences = [j-i for i, j in zip(time_array[:-1], time_array[1:])]
            if sum(time_difference <= 0 for time_difference in time_differences):
                print("Time array not strictly monotonically increasing")
                # raise ValueError("Time array has to be strictly monotonically increasing.")
        return True

    def __strTimeToMinutes(self,t_raw):
        t_converted = []
        for time in t_raw:
            t_converted.append(int(cal.timegm(datetime.datetime.strptime(time, DATETIME_FORMAT).timetuple()) / 60.0))
        return np.asarray(t_converted)

    def copy(self):
        """ Create a deep copy of the instance.

        Returns:
            Scenario : Deep copy of the instance.

        """
        scenario = Scenario(self.start_time.as_str, self.end_time.as_str, self.scenario_setting)
        for attribute in self.__slots__:
            if hasattr(self, attribute):
                if isinstance(getattr(self, attribute), (np.ndarray, Units, Position, Timestamp)):
                    setattr(scenario, attribute, getattr(self, attribute).copy())
                else:
                    setattr(scenario, attribute, getattr(self, attribute))
        return scenario

    def appendBolusInsulin(self, next_bolus: float = 0.0, unit: str = r"U"):
        """ Appends bolus insulin to the already defined scenario.

        Args:
            next_bolus: Bolus value in the next time point (defined by Ts).
            unit: Unit of the bolus.
        """
        next_bolus = self.units.convertUnits(next_bolus, unit, self.units.bolus, self.Ts)
        self.manual_boluses = np.vstack([self.manual_boluses, [self.end_time.as_int, next_bolus]])

    def appendBasalInsulin(self, next_basal: float = 0.0, unit: str = r"U/hr"):
        """ Modifies the basal rate in the next time pont (defined by Ts).

        Args:
            next_basal: New basal rate.
            unit: Unit of the basal rate.
        """
        next_basal = self.units.convertUnits(next_basal, unit, self.units.basal, self.Ts)
        self.manual_basal_insulin = np.vstack([self.manual_basal_insulin, [self.end_time.as_int, next_basal]])

    def plot(self, show = True):
        """ Plots the CHO and insulin intakes of the scenario. Horizontal axis in UNIX timestamp [minutes].

            Examples:
                >>> self.plot()
        """
        for row in self.manual_meals:
            plt.arrow(row[0], 0, 0, row[1],width=1)
        for row in self.manual_boluses:
            plt.arrow(row[0], 0, 0, row[1],color=[0,1,0],width=1)
        plt.xlim((self.start_time.as_int,self.end_time.as_int))
        if show:
            plt.show()

    def setHardware(self, sensor: str, pump: str, type: float = 0.0):  # UVa-Padova
        self.params_t1dms.hardwareN_sensor = sensor
        self.params_t1dms.hardware_sensorType = type
        self.params_t1dms.hardwareN_pump = pump

    def setParamsT1DMS(self, simToD: float = 0.0, Qmeals: str = 'total', Treg: float = 0.0, meal_duration: float = 15.0,
                       Qbasal: str = 'fixed', OB = 'off', Qbolus: str = 'total',
                       SQg: float = 1.0):
        """ Sets the Uva/Padova simulator related parameters of the scenario.

            Args:
                simToD (float): Represents the "simToD" variable of the UVA/Padova simulator.
                Qmeals (str): Represents the "Qmeals" variable of the UVA/Padova simulator.
                Treg (str): Represents the "Treg" variable of the UVA/Padova simulator.
                meal_duration (float): Represents the "meal_duration" variable of the UVA/Padova simulator.
                Qbasal (str): Represents the "Qbasal" variable of the UVA/Padova simulator.
                OB (str): Represents the "OB" variable of the UVA/Padova simulator.
                Qbolus (str): Represents the "Qbolus" variable of the UVA/Padova simulator.
                SQg (float): Represents the "SQg" variable of the UVA/Padova simulator.
        """
        self.params_t1dms.simToD = simToD # time of day at start of simulation
        self.params_t1dms.Qmeals = Qmeals # unit of meals [g]
        self.params_t1dms.Treg = Treg # start time of regulation
        self.params_t1dms.meal_duration = meal_duration # default 15 min, max 30 min
        self.params_t1dms.basal = float(self.manual_basal_insulin[-1,1])
        self.params_t1dms.Qbasal = Qbasal # unit of basal [U]
        if Qbasal == 'quest':
            self.params_t1dms.basal = 0.0
        self.params_t1dms.OB = OB
        if OB == 'on':
            self.params_t1dms.CR = 'on' # subject-specific carbohydrate ratio, used to calculate optimal bolus
        else:
            self.params_t1dms.CR = 'off'
        self.params_t1dms.Qbolus = Qbolus # unit of bolus [U]
        self.params_t1dms.SQg = SQg
