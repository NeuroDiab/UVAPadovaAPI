import numpy as np
import math
import matlab.engine
import matplotlib.pyplot as plt
import time
from dataclasses import dataclass
from collections import namedtuple

@dataclass
class Quest:
    """Class for keeping track of an item in inventory."""
    OB: float
    MD: float
    TDI: float
    age: float
    t1dm_duration: float
    names: str
    weight: float
    basal: float
    fastingBG: float


class VirtualPatientT1DMS:
    """ VirtualPatientT1DMS class implements a virtual patient on the basis of the OE simulator, and controls the MATLAB engine.

            Args:
                BGinit :
                patient (str): Patient ID.
                eng : Matlab engine for Python.
                simulation_data (SimulationData): Stores all the simulation related data.
                hardwareN (dict): Represents the "hardwareN" variable of the UVA/Padova simulator.
                hardware (dict): Represents the "hardware" variable of the UVA/Padova simulator.
                rep (int): Represents the "rep" variable of the UVA/Padova simulator.
                bck_meals (matlab.double): Represents the "bck_meals" variable of the UVA/Padova simulator.
                bck_meal_announce (matlab.double): Represents the "bck_meal_announce" variable of the UVA/Padova simulator.
                bck_SQinsulin (dict): Represents the "bck_SQinsulin" variable of the UVA/Padova simulator.
                ind (int): Represents the "ind" variable of the UVA/Padova simulator.
                sc (dict): Represents the "sc" variable of the UVA/Padova simulator.
                result (dict): Represents the "res_aux" variable of the UVA/Padova simulator.
                bg (np.array): Stores the simulated blood glucose trajectory.
    """

    def __init__(self, patient_name: str, BGinit: list):
        """ Constructor.

            Note:
                Starts the Matlab engine.

            Args:
                patient_name : Patient ID as given in the UVA/Padova simulator.
                BGinit : Initial blood glucose concentration of the patient. If empty, basal conditions is assumed.
        """
        self.BGinit = BGinit
        self.eng = matlab.engine.start_matlab()
        path = "C:/T1DMS_Install/UVa PadovaT1DM Simulator v3.2.1/"
        self.eng.cd(path, nargout=0)
        self.patient = patient_name

    @property
    def patient(self):
        return self._patient

    @patient.setter
    def patient(self, value):
        self._patient = value
        self.Quest = Quest(**self.eng.load_quest(value))
        print(
            "Patient info:" + self.patient + " basal:%.2f" % self.Quest.basal + " fasting BG:%.2f" % self.Quest.fastingBG)

    def simulatePatient(self, simulation_data: dict):
        """ Simulates the patient based on the data given in the simulation_data argument.

            Args:
                simulation_data (SimulationData): Stores the simulation related information.
        """
        self.simulation_data = simulation_data
        self.hardwareN = simulation_data['hardwareN']
        self.hardware = simulation_data['hardware']
        self.rep = 1
        self.bck_meals = simulation_data['Lscenario']['meals']
        self.bck_meal_announce = simulation_data['Lscenario']['meal_announce']
        self.bck_SQinsulin = simulation_data['Lscenario']['SQ_insulin']['signals']
        self.ind = 1
        self.sc = simulation_data['Lscenario']

        simulation_data['Lscenario']['BGinit'] = self.BGinit
        start_time = time.time()
        res_aux = self.eng.connect_function(self.sc,
                          self.patient,
                          self.hardwareN,
                          self.hardware,
                          self.rep,
                          self.bck_meals,
                          self.bck_meal_announce,
                          self.bck_SQinsulin,
                          self.ind)
        print("T1DMS simulation time: " + str(time.time()-start_time))
        self.result = res_aux
        self.bg = np.asarray(self.result[0]['G']['signals']['values'])

    def plotHistoricalStates(self):
        """ Plots the result of the simulatePatient() function.
        """
        bg = np.asarray(self.result[0]['G']['signals']['values'])
        sensor_noise = np.asarray(self.result[0]['sensor']['signals']['values'])

        plt.plot(bg, label="BG")
        plt.plot(sensor_noise, label="CGM")
        plt.legend()
        plt.title(self.patient)
        plt.show()

        rmse = math.sqrt(np.square(np.subtract(bg,sensor_noise)).mean())
        print(rmse)