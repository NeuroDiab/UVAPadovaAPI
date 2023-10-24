from threading import Thread
import json
import requests
import time


class AAPSHandler:
    __SIMULATION_PERIOD = 5

    """
    This class can be used by a client to make requests to the uva_padova_API simply from Python code.
    In addition, the attributes of the class make input and output data more organized.

    Args:
        HOST_ADDRESS (str, optional): The IP address of the server that runs the uva_padova_API.py.
            Defaults to the loopback address.
        PORT (int, optional): The port number where the uva_padova_API.py can be accessed on the server.
            Defaults to 5000.

    Note:
        The methods don't check the correctness of the input parameters.
        To enter the input parameters correctly, please read the documentation of UVAPadova Simulator.

    Attributes:
        HOST_ADDRESS (str): The IP address of the server that runs the uva_padova_API.py.
        PORT (int): The port number where the uva_padova_API.py can be accessed on the server.
        listOfCarbohydrateIntakes (list(float)):
            A list which contains the carbohydrate intakes during the simulation line.
        listOfInsulinIntakes (list(float)): A list which contains the insulin intakes during the simulation line.
        listOfBloodGlucoseValues (list(float)):A list which contains the blood glucose values in 5 minute increments.

    """

    def __init__(self, HOST_ADDRESS: str = "127.0.0.1", PORT: int = 5000):
        self.HOST_ADDRESS = "http://" + HOST_ADDRESS
        self.PORT = PORT
        self.__received_bloodglucose = list()
        self.__carbohydrate_to_dose = list()
        self.__insulin_to_dose = list()
        self.__scheduler_Thread: Thread = None
        self.__cancellation_token: bool = None

    def __del__(self):
        self.__cancellation_token: bool = False
        self.__scheduler_Thread.join()

    def initializePatient(self, patient_name: str, pump: str = None, sensor: str = None) -> bool:
        """
        This method initialize a new simulation (resets the simulation line).

        Args:
            patient_name (str): The identifier of the patient.
            pump (str, optional): The type of the insulin pump.
            sensor (str, optional): The type of the CGM sensor.

        Returns:
            bool: If the initialization was successful returns true, otherwise returns false.
        """

        params = {'id': patient_name}
        if pump is not None:
            params["pump"] = pump
        if sensor is not None:
            params["sensor"] = sensor
        response = requests.get(url=self.HOST_ADDRESS+":"+str(self.PORT)+"/createSimulation", params=params)
        self.__cancellation_token: bool = True
        self.__scheduler_Thread = Thread(target=self.__SimulationScheduler())
        return response.ok

    def addInsulin(self, amount: float):
        """This method doses insulin to the patient.

        Args:
            amount (float): The amount of insulin in units.
        """
        self.__insulin_to_dose.append(amount)

    def addCarbohydrate(self, amount: float):
        """This method intakes carbohydrate to the patient.

        Args:
            amount (float): The amount of carbohydrate in grams.
        """
        self.__carbohydrate_to_dose.append(amount)

    def getBloodGlucose(self, aggregated: bool = False) -> (str, bool):
        """This method... .

        Args:
            aggregated (bool): .

        Returns:
            str: If the request was successful returns true, otherwise returns false.
            bool: If the request was successful returns true, otherwise returns false.
        """
        if self.__received_bloodglucose:
            if aggregated:
                result = sum(self.__received_bloodglucose)/len(self.__received_bloodglucose)
            else:
                result = self.__received_bloodglucose.pop()
            status = True
        else:
            result, status = "Blood glucose value isn't available.", False
        return result, status

    def __SimulationScheduler(self):
        """This method extends the initialized simulation by 5 minutes.
        Insulin or/and carbohydrate intake can be added to the simulation.

        Note:
            Before calling this function, please initialize a patient by "initializePatient" function.
        """
        while self.__cancellation_token:
            time_at_start = time.time_ns()
            params = {}
            if self.__carbohydrate_to_dose:
                params["ch"] = sum(self.__carbohydrate_to_dose)
                self.__carbohydrate_to_dose.clear()
            if self.__insulin_to_dose:
                params["insulin"] = sum(self.__insulin_to_dose)
                self.__insulin_to_dose.clear()
            response = requests.get(url=self.HOST_ADDRESS + ":" + str(self.PORT) + "/simulate", params=params)
            if response.ok:
                result = response.json()
                result = json.loads(result)
                self.__received_bloodglucose.append(float(result["bloodGlucose"]))
            elapsed_time = time.time_ns() - time_at_start
            time.sleep(self.__SIMULATION_PERIOD - elapsed_time)
