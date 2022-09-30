import numpy as np
from matplotlib import pyplot as plt
from ..OESimulator.SimulationData.Scenario import Scenario
from ..OESimulator.DataProcessor import DataProcessor
from .VirtualPatientT1DMS import VirtualPatientT1DMS
import matlab.engine
import time


class UvaPadovaSimulator:
    """
        This class can be store the current state of a simulation and can extend it by 5 minutes per step.

        Note:
            This class was created exclusively to serve the API.

        Args:
            patient (obj) :
                A VirtualPatientT1DMS object, which represents a virtual patient and controls the MATLAB engine.
            scenario (obj):
                A Scenario object, which provides a storage and interface for the simulation related information.
            chLostFlag (bool):
                A flag which indicates whether the meal could be considered according to
                the rules of the UvaPadovaSimulator or not.
            tEndReal (int): The duration of the simulation in minutes.
            i_times (list(int)): The list of minutes when was insulin intake.
            meals (list(float)): The list of the amounts of carbohydrate taken.
            m_times (list(int)): The list of minutes when was carbohydrate intake.
            insulins (list(float)): The list of the amounts of insulin taken.
            sensor (str): The type of the CGM sensor currently in use. Defaults to 'guardianRT.scs'
            pump (str): The type of the insulin pump currently in use. Defaults to 'Generic_1.pmp'

    """

    def __init__(self, patient_name: str):
        self.patient = VirtualPatientT1DMS(patient_name=patient_name, BGinit=matlab.double([]))
        self.scenario = None
        self.chLostFlag = False
        self.tEndReal = 0
        self.i_times = list()
        self.meals = list()
        self.m_times = list()
        self.insulins = list()
        self.sensor = 'guardianRT.scs'
        self.pump = 'Generic_1.pmp'

    def doSimulation(self, carbohydrate: float, insulin: float):
        """
        This method extends the initialized simulation by 5 minutes.
        The method invokes the MATHLAB engine with an extended Scenario.


        Args:
            carbohydrate (float):
                The amount of carbohydrate intake, in the last five minutes (in grams).
                Zero if there wasn't carbohydrate intake.
            insulin (float):
                The amount of insulin intake, in the last five minutes (in unites).
                Zero if there wasn't insulin intake.

        Returns:
            The blood glucose level value at the end of the simulation.
        """
        self.chLostFlag = False  # reset the flag
        self.__buildScenario(carbohydrate, insulin)
        T1DMSprocessor = DataProcessor()
        T1DMSdata, patient_data = T1DMSprocessor.processData(scenario=self.scenario)
        self.patient.simulatePatient(simulation_data=T1DMSdata)
        return self.patient.bg[self.tEndReal][0]

    def __buildScenario(self, carbohydrate: float, insulin: float):
        """This method builds and the extended Scenario, considering the simulation rules of UvaPadova Simulator.

        Args:
            carbohydrate (float):
                The amount of carbohydrate intake, in the last five minutes (in grams).
                Zero if there wasn't carbohydrate intake.
            insulin (float):
                The amount of insulin intake, in the last five minutes (in unites).
                Zero if there wasn't insulin intake.
        """
        # Update values
        self.tEndReal += 5
        if carbohydrate != 0 and self.__newChIsEnabled():
            self.m_times.append(self.tEndReal)
            self.meals.append(carbohydrate)
        if insulin != 0:
            self.i_times.append(self.tEndReal)
            self.insulins.append(insulin)
        if self.tEndReal < 30:
            tend = 30
        else:
            tend = self.tEndReal

        # Create Scenario
        self.scenario = Scenario(0, tend, "t1dms")
        self.scenario.Ts = 1
        self.scenario.setManualMealScheme(meal_times=tuple(self.m_times), meal_values=tuple(self.meals), unit='g')
        self.scenario.setManualBolusScheme(bolus_times=tuple(self.i_times), bolus_values=tuple(self.insulins), unit='U')
        self.scenario.setManualBasalInsulin(0.0, unit=r"U/hr")
        self.scenario.setHardware(sensor=self.sensor, pump=self.pump)
        self.scenario.setParamsT1DMS()

    def __newChIsEnabled(self) -> bool:
        """This method checks the meal could be considered according to the rules of the UvaPadova Simulator or not
        and sets the chLostFlag's value.

        Returns:
            bool: True if the carbohydrate intake can be considered. False otherwise.
        """
        if self.tEndReal >= 60 and (not self.m_times or (self.tEndReal - self.m_times[-1]) >= 60):
            return True
        else:
            self.chLostFlag = True
            return False
