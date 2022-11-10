from flask import Flask, request
from flask_restful import Resource, Api
import json
from Simulator.UVAPadova.UVAPadovaSimulator import UvaPadovaSimulator
from dataclasses import dataclass, asdict
import subprocess
import pyperclip

uva_padova_simulator = None
"""
    This modul level variable will be contain (after initialization) an UvaPadovaSimulator instance, 
    which represents the current state of the simulation and modifies it.
"""


class SimulationCreator(Resource):
    """This class handles the requests to initialize a simulation.

    Note:
        The API doesn't check the correctness of the input parameters.
        To enter the input parameters correctly, please read the documentation of UVAPadova Simulator.

    """
    def get(self):
        """ A new simulation can be created by an HTTP GET request. For the initialization, the patient ID is required
        as a HTTP GET parameter. Optionally, the type of insulin pump or/and CGM sensor used for the simulation
        can also be specified as a HTTP GET parameter.

            Returns:
                str: A HTTP status code according to the success of the request.

            Examples:
                >>> http://<IP ADDRESS>:<PORT NUMBER>/createSimulation?patientid=<patient ID>&pump=<pump name>&sensor=<CGM name>
        """
        if "id" in request.args:
            patient_name = request.args.get("id")
        elif "name" in request.args:
            patient_name = request.args.get("name")
        elif "patientname" in request.args:
            patient_name = request.args.get("patientname")
        elif "patientid" in request.args:
            patient_name = request.args.get("patienid")
        else:
            return "", "400 The patient ID is required for initialization as HTTP GET parameter!"
        global uva_padova_simulator
        uva_padova_simulator = UvaPadovaSimulator(patient_name=patient_name)
        if "pump" in request.args:
            uva_padova_simulator.pump = request.args.get("pump")
        if "sensor" in request.args:
            uva_padova_simulator.sensor = request.args.get("sensor")
        return json.dumps(asdict(uva_padova_simulator.patient.Quest))
        #return "", '200 The ' + patient_name + " patient successfully loaded."


class Simulate(Resource):
    """This class handles the requests to modify the current state of the simulation.

    Note:
        The API doesn't check the correctness of the input parameters.
        To enter the input parameters correctly, please read the documentation of UVAPadova Simulator.

    """
    def get(self):
        """
        The simulation can be extended by 5 minutes by an HTTP GET request.
        If carbohydrate or insulin intake occurred in the last 5 minutes,
        their amount can be specified as an HTTP GET parameter.


        Examples:
            >>> http://<IP ADDRESS>:<PORT NUMBER>/simulate?carbohydrate=<value in grams>&insulin=<value in units>


        Returns:
            str:
                A HTTP status code according to the success of the request.
                Furthermore, if the simulation request was successful, the function returns a JSON string,
                which contains the "bloodGlucose" value at the end of the simulation
                and optionally other alerts related to the simulation.
        """
        if "ch" in request.args:
            carbohydrate = float(request.args.get("ch"))
        elif "c" in request.args:
            carbohydrate = float(request.args.get("c"))
        elif "carbohydrate" in request.args:
            carbohydrate = float(request.args.get("carbohydrate"))
        elif "meal" in request.args:
            carbohydrate = float(request.args.get("meal"))
        elif "mealvalue" in request.args:
            carbohydrate = float(request.args.get("mealvalue"))
        else:
            carbohydrate = 0
        if "insulin" in request.args:
            insulin = float(request.args.get("insulin"))
        elif "i" in request.args:
            insulin = float(request.args.get("i"))
        elif "bolus" in request.args:
            insulin = float(request.args.get("bolus"))
        elif "bolusinsulin" in request.args:
            insulin = float(request.args.get("bolusinsulin"))
        elif "bolusvalue" in request.args:
            insulin = float(request.args.get("bolusvalue"))
        else:
            insulin = 0
        global uva_padova_simulator
        if uva_padova_simulator is not None:
            result = {"bloodGlucose": uva_padova_simulator.doSimulation(carbohydrate, insulin)}
        else:
            return "", "409 Patient wasn't initialized."
        if uva_padova_simulator.chLostFlag:
            result["Alert"] = "Carbohydrate intake was ignored, because at least one hour should pass between meals."
        return json.dumps(result), 200

    def post(self):
        """
        During the simulation the type of the insulin pump or the CGM sensor can be changed by an HTTP POST request.
        The type of the new pump (or sensor) is required as HTTP POST parameter.


        Returns:
            int: A HTTP status code according to the success of the request.
        """
        if "pump" in request.args:
            uva_padova_simulator.pump = request.args.get("pump")
        if "sensor" in request.args:
            uva_padova_simulator.sensor = request.args.get("sensor")
        return "", 200


app = Flask(__name__)
api = Api(app)
api.add_resource(SimulationCreator, '/createSimulation')
api.add_resource(Simulate, '/simulate')


if __name__ == '__main__':
    app.run(host='0.0.0.0')


