import requests
import json


class UvaPadovaAPI:
    """
    This class can be used by a client to make requests to the UVAPadovaAPI simply from Python code.
    In addition, the attributes of the class make input and output data more organized.

    Note:
        The methods don't check the correctness of the input parameters.
        To enter the input parameters correctly, please read the documentation of UVAPadova Simulator.

    Args:
        HOST_ADDRESS (str): The IP address of the server that runs the UVAPadovaAPI.py.
        PORT (int): The port number where the UVAPadovaAPI.py can be accessed on the server.
        listOfCarbohydrateIntakes (list(float)):
            A list which contains the carbohydrate intakes during the simulation line.
        listOfInsulinIntakes (list(float)): A list which contains the insulin intakes during the simulation line.
        listOfBloodGlucoseValues (list(float)):A list which contains the blood glucose values in 5 minute increments.

    """

    def __init__(self, HOST_ADDRESS: str = "127.0.0.1", PORT: int = 5000):
        """
        Args:
            HOST_ADDRESS (str, optional): The IP address of the server that runs the UVAPadovaAPI.py.
                Defaults to the loopback address.
            PORT (int, optional): The port number where the UVAPadovaAPI.py can be accessed on the server.
                Defaults to 5000.

        """


        self.HOST_ADDRESS = "http://" + HOST_ADDRESS
        self.PORT = PORT
        self.listOfCarbohydrateIntakes = list()
        self.listOfInsulinIntakes = list()
        self.listOfBloodGlucoseValues = list()

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
        self.listOfCarbohydrateIntakes.clear()
        self.listOfInsulinIntakes.clear()
        self.listOfBloodGlucoseValues.clear()
        return response.ok

    def setPump(self, pump: str) -> bool:
        """This method changes the insulin pump.

        Args:
            pump (str): The name of the pump.

        Returns:
            bool: If the request was successful returns true, otherwise returns false.
        """
        params = {'pump': pump}
        response = requests.post(url=self.HOST_ADDRESS + ":" + str(self.PORT) + "/simulate", params=params)
        return response.ok

    def setSensor(self, sensor: str) -> bool:
        """This method changes the CGM.

        Args:
            sensor (str): The name of the CGM.

        Returns:
            bool: If the request was successful returns true, otherwise returns false.
        """
        params = {'sensor': sensor}
        response = requests.post(url=self.HOST_ADDRESS + ":" + str(self.PORT) + "/simulate", params=params)
        return response.ok

    def doSimulation(self, carbohydrate: float = None, insulin: float = None):
        """This method extends the initialized simulation by 5 minutes.
        Insulin or/and carbohydrate intake can be added to the simulation.

        Note:
            Before calling this function, please initialize a patient by "initializePatient" function.

        Args:
            carbohydrate (float, optional): The amount of carbohydrate intake, in the last five minutes (in grams).
            insulin (float, optional): The amount of insulin intake, in the last five minutes (unit).

        Returns:
            If the simulation request was successful, the function returns a dictionary,
            which contains the "bloodGlucose" value at the end of the simulation
            and optionally other alerts related to the simulation.

            If the simulation request was unsuccessful, the function returns the reason of the error (string format).

        """
        params = {}
        if carbohydrate is not None:
            self.listOfCarbohydrateIntakes.append(float(carbohydrate))
            params["ch"] = carbohydrate
        if insulin is not None:
            self.listOfInsulinIntakes.append(float(insulin))
            params["insulin"] = insulin
        response = requests.get(url=self.HOST_ADDRESS + ":" + str(self.PORT) + "/simulate", params=params)
        if response.ok:
            result = response.json()
            result = json.loads(result)
            self.listOfBloodGlucoseValues.append(float(result["bloodGlucose"]))
            return result
        else:
            return response.reason
