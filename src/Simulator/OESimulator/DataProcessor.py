from .SimulationData.SimulationData import SimulationData
from .SimulationData.Scenario import Scenario
from .SimulationData.Units import Units
from .SimulationData.Position import Position
from .SimulationData.PatientData import PatientData
from .SimulationData.PatientParams import PatientParams

from .SimulationData.CONSTANTS import *
from .DataProcessing.ErrorCodes import ERROR_CODES
from .DataProcessing.DBFile import DBFile


import numpy as np
import json
import datetime
from types import SimpleNamespace


class DataProcessor(json.JSONEncoder):
    """ Data processor class.
        Creates SimulationData and PatientData structures by defining a Scenario and patient id and data source.
    """

    def __init__(self, patient_id: str = ""):
        """ Constructor.
            Possible data sources: DT, azure.
        """
        self.data_source: str = ""
        self.patient_id = patient_id

    def checkData(self,scenario,input_data):
        return self.DTProcess(scenario,input_data)[2]

    def processData(self, scenario: Scenario, input_data = None):
        """
        """
        self.scenario = scenario
        switch = {'DT': self.DTProcess,
                  'manual': self.manualProcess,
                  'emulated': self.manualProcess,
                  't1dms': self.t1dmsProcess}  # UVa-Padova
        simulation_data, patient_data, error = switch[scenario.scenario_setting](scenario,input_data)
        print(error)
        return simulation_data, patient_data

    def handleTypes(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, range):
            return list(obj)
        if isinstance(obj, (PatientParams,Scenario,Units,Position,SimulationData,PatientData)):
            return obj.__dict__  # Or another method to serialize it
        return json.JSONEncoder.default(self, obj)

    def objectToDict(self, python_object):
        return json.loads(json.dumps(python_object.__dict__, default=self.handleTypes))#default=self.handleTypes

    def JSONToObject(self, json_data):
        return json.loads(json_data, object_hook=lambda d: SimpleNamespace(**d))

    def DTProcess(self, scenario: Scenario, input_data):
        print("in DTprocess")
        self.data_source = "DT"

        db_file = DBFile(input_data)
        if not db_file.loadCGM():
            return [], [], ERROR_CODES.CGM_INVALID
        if not db_file.loadMeals():
            return [], [], ERROR_CODES.CHO_INVALID
        if not db_file.loadInsulin():
            return [], [], ERROR_CODES.INSULIN_INVALID

        if not len(db_file.glucose_values):
            return [],[],ERROR_CODES.CGM_EMPTY
        if not len(db_file.bolus_values):
            return [],[],ERROR_CODES.INSULIN_EMPTY
        if not len(db_file.meal_values):
            return [],[],ERROR_CODES.CHO_EMPTY

        glucose_values = np.asarray(db_file.glucose_values)

        # if np.sum(np.logical_or(glucose_values>400.0, glucose_values<40.0)):
        #     return [],[],ERROR_CODES.CGM_OUTOFRANGE

        glucose_times, glucose_values = self.sort(db_file.glucose_times, db_file.glucose_values)
        basal_times, basal_values = self.sort(db_file.basal_times, db_file.basal_values)
        bolus_times, bolus_values = self.sort(db_file.bolus_times, db_file.bolus_values)
        meal_times, meal_values = self.sort(db_file.meal_times, db_file.meal_values)
        # print(max(glucose_times))
        # print(min(glucose_times))


        # diffs = np.diff(glucose_times)
        # print(np.diff(glucose_times))
        # print(min(diffs))
        # print(max(diffs))
        # plt.plot(glucose_times,glucose_values)
        # plt.show()

        # if np.sum(np.diff(glucose_times)>20.0):
        #     return [],[],ERROR_CODES.CGM_GAP

        if not basal_values:
            print("Basal value not found.")
            basal_values = 0.0
            basal_times = glucose_times[0]

        glucose_values = np.interp(np.linspace(glucose_times[0], glucose_times[-1], int((glucose_times[-1] - glucose_times[0]) / 5.0)), glucose_times, glucose_values)
        glucose_times = np.linspace(glucose_times[0], glucose_times[-1], int((glucose_times[-1] - glucose_times[0]) / 5.0))

        scenario.setManualMealScheme(meal_times, meal_values)
        scenario.setManualBolusScheme(bolus_times, bolus_values)
        scenario.setManualBasalInsulin(basal_values, basal_times)
        simulation_data, patient_data, error = self.manualProcess(scenario, input_data)
        simulation_data.glucose_level = np.zeros((len(glucose_values), 2))
        simulation_data.glucose_level[:, 0] = glucose_times
        simulation_data.glucose_level[:, 1] = glucose_values
        return simulation_data, patient_data, error

    def manualProcess(self, scenario: Scenario, input_data = None):
        """ Manual simulation data generation.

        """
        self.data_source = "manual"

        patient_data = PatientData()
        patient_data.patient_id = self.patient_id

        simulation_data = SimulationData(scenario)
        simulation_data.t_start = scenario.start_time.as_int
        simulation_data.t_end = scenario.end_time.as_int

        simulation_data.initArrays()
        simulation_data.basal.as_timestamped_array = scenario.manual_basal_insulin
        simulation_data.bolus.as_timestamped_array = scenario.manual_boluses
        simulation_data.meal.as_timestamped_array = scenario.manual_meals

        simulation_data.trim()

        #simulation_data.scenario.Ts = 5
        simulation_data.scenario.units.insulin = r"uU/min"
        simulation_data.scenario.position.basal = 1
        simulation_data.scenario.position.bolus = 1
        simulation_data.scenario.position.meal = 1
        simulation_data.scenario.position.time_constant = 2
        simulation_data.scenario.position.glucose_level = 1
        simulation_data.units.basal = r"uU/min"
        simulation_data.units.bolus = "uU/min"
        simulation_data.units.meal = r"g/min"
        simulation_data.t_sections = (scenario.end_time.as_int,)
        simulation_data.is_meal_up_to_date = False

        simulation_data.bolus.copyTimestampedArrayToArray(simulation_data.t_start,simulation_data.scenario.Ts,simulation_data.scenario.position.bolus)
        simulation_data.meal.copyTimestampedArrayToArray(simulation_data.t_start,simulation_data.scenario.Ts,simulation_data.scenario.position.meal)
        simulation_data.basal.copyTimestampedArrayToArray(simulation_data.t_start,simulation_data.scenario.Ts,simulation_data.scenario.position.basal)

        simulation_data.bolus.as_array = simulation_data.scenario.units.convertUnits(simulation_data.bolus.as_array, simulation_data.scenario.units.bolus,
                                                          simulation_data.units.insulin, simulation_data.scenario.Ts)
        simulation_data.basal.as_array = simulation_data.scenario.units.convertUnits(simulation_data.basal.as_array, simulation_data.scenario.units.basal,
                                                     simulation_data.units.insulin, simulation_data.scenario.Ts)

        return simulation_data, patient_data, False

    def t1dmsProcess(self, scenario: Scenario, input_data=None): # UVa-Padova
        import matlab.engine
        print("in t1dmsProcess")
        self.data_source = "t1dms"
        patient_data = None  #self.patient_id
        Ameals = list(scenario.manual_meals[:,1])
        dose = list(np.multiply(np.array(Ameals), 1000)) # meal amount in mg
        Tdose = list(scenario.manual_meals[:,0]) # meal times in min
        Tmeals = list(scenario.manual_meals[:,0] / 60.0) # meal times in hour
        Abolus = []
        Tbolus = []
        if scenario.params_t1dms.OB == 'off': # optimal bolus calculation ('on') or using the given value ('off')
            Abolus = list(scenario.manual_boluses[:,1])
            Tbolus = list(scenario.manual_boluses[:,0])
            for i in range(len(Tbolus)):
                Abolus[i] = float(Abolus[i])
                Tbolus[i] = float(Tbolus[i])

        for i in range(len(dose)):
            dose[i] = float(dose[i])
            Tdose[i] = float(Tdose[i])
            Ameals[i] = float(Ameals[i])
            Tmeals[i] = float(Tmeals[i])


        Tsimul = scenario.end_time.as_int - scenario.start_time.as_int
        Tsimul = float(Tsimul)
        Tclosed = Tsimul + 500.0 # start of closed loop, ignored above Tsimul
        IV_insulin = [[0.0,0.0],[Tsimul,0.0]] # start, end time and amount of continuous IV dextrose/insulin injections
        IV_glucose = [[0.0,0.0],[Tsimul,0.0]]

        if scenario.params_t1dms.Qbasal == 'quest': # subject specific basal ('quest') or using the given value
            basal_UpMin = 0.0 # it will be overwritten
        else:
            basal_UpMin = scenario.params_t1dms.basal/60.0 # U/h -> U/min

        if len(Tbolus) != 0:

            t_ins = [0.0] # vector of insulin times; for every t bolus time: t-0.01,t,t+1-0.01,t+1
            for i in range(len(Tbolus)):
                t_ins.append(Tbolus[i]-0.01)#(Tdose[i] - 0.01)
                t_ins.append(Tbolus[i])
                t_ins.append(Tbolus[i] + 1 - 0.01)
                t_ins.append(Tbolus[i] + 1)
            t_ins.append(Tbolus[i] + 2) # last value: 2 minutes after last t
            #t_ins = np.array([t_ins]).T

            val_ins = [[basal_UpMin, 0.0]] # basal and bolus insulin for every meal: 0,bolus,bolus,0
            if scenario.params_t1dms.OB == 'off':
                for i in range(len(Abolus)): # if bolus is fixed, bolus values are used
                    val_ins.append([basal_UpMin, 0.0])
                    val_ins.append([basal_UpMin, Abolus[i]])
                    val_ins.append([basal_UpMin, Abolus[i]])
                    val_ins.append([basal_UpMin, 0.0])
            else:
                for i in range(len(Ameals)): # if optimal bolus is calculated, meal values are used
                    val_ins.append([basal_UpMin, 0.0]) # 0,meal,meal,0
                    val_ins.append([basal_UpMin, Ameals[i]])
                    val_ins.append([basal_UpMin, Ameals[i]])
                    val_ins.append([basal_UpMin, 0.0])
            val_ins.append([basal_UpMin, 0.0]) # first and last value is 0
        else:
            t_ins = [0.0]
            val_ins = [basal_UpMin, 0.0]

        if len(Tdose) != 0:
            meals = [[0.0, 0.0]] # time and amount for every meal
            for i in range(len(Tdose)): # time: t-0.01,t,t+meal_duration-0.01,t+meal_duration; amount: 0,meal_amount/duration,meal_amount/duration,0
                meals.append([Tdose[i] - 0.01, 0.0])
                meals.append([Tdose[i], Ameals[i] / scenario.params_t1dms.meal_duration])
                meals.append([Tdose[i] + scenario.params_t1dms.meal_duration - 0.01, Ameals[i] / scenario.params_t1dms.meal_duration])
                meals.append([Tdose[i] + scenario.params_t1dms.meal_duration, 0.0])
            meals.append([Tdose[i] + scenario.params_t1dms.meal_duration + 1, 0.0]) # first and last value is 0

            t_meals = [0.0]
            for i in range(len(Tmeals)): # for every t [hour] meal time: (t-1)[min]-0.01,(t-1)[min],(t+1)[min],(t+1)[min]+0.01
                t_meals.append((Tmeals[i] - 1) * 60.0 - 0.01)
                t_meals.append((Tmeals[i] - 1) * 60.0)
                t_meals.append((Tmeals[i] + 1) * 60.0)
                t_meals.append((Tmeals[i] + 1) * 60.0 + 0.01)
            t_meals.append((Tmeals[i] + 1) * 60.0 + 1.01) # last value: 1 minute after last element of t_meal

            for i in range(len(t_meals) - 2): # to avoid the decrease of t_meals values (E.g. when only 1 hour passes between 2 meals,
                # t_meals vector would not be monotonically increasing: Tmeals=[2,3] -> t_meals=[59.99,60,180,180.01,119.99,120,240,240.01])
                if t_meals[i] >= t_meals[i + 2]:
                    t_meals[i] = t_meals[i + 2] - 0.03
                    t_meals[i + 1] = t_meals[i + 2] - 0.02

        #t_meals = np.array([t_meals]).T

            val_meals = [[0.0, 0.0]] # amount of every meal: 0,meal,meal,0
            for i in range(len(Ameals)): # times: 0,60,-60,0 (minimum 1 hour has to pass between meals)(?)
                val_meals.append([0.0, 0.0])
                val_meals.append([Ameals[i], 60.0]) # 60.0
                val_meals.append([Ameals[i], -60.0]) # -60.0
                val_meals.append([0.0, 0.0])
            val_meals.append([0.0, 0.0]) # first and last values are 0
        else:
            t_meals = [0.0, 1.0]
            meals = [[0.0, 0.0],[1.0, 0.0]]
            val_meals = [[0.0, 0.0],[0.0, 0.0]]
            dose = [0.0]
            Tdose = [0.0]

        T1DMSData= {'Lscenario':
                    {"SQ_Gluc": {"time": 0.0, "signals": {"dimensions": 1.0, "values": 0.0}},
                       "SQ_Pram": {"time": 0.0, "signals": {"dimensions": 1.0, "values": 0.0}, "dimension": 1.0},
                       "SQ_insulin": {"time": matlab.double(t_ins), "signals": {"values": matlab.double(val_ins), "dimensions": 2.0}},
                       "meals": matlab.double(meals),
                       "meal_announce": {"time": matlab.double(t_meals), "signals": {"values": matlab.double(val_meals), "dimensions": 2.0}},
                       "dose": matlab.double(dose),
                       "Tdose": matlab.double(Tdose),
                       #"Abolus": matlab.double(Abolus),
                       #"Tbolus": matlab.double(Tbolus),
                       "Qmeals": scenario.params_t1dms.Qmeals,
                       "Dmeals": scenario.params_t1dms.meal_duration,
                       "Tsimul": Tsimul,
                       "Tclosed": Tclosed,
                       "Treg": scenario.params_t1dms.Treg,
                       "CR": scenario.params_t1dms.CR,
                       "SQg": scenario.params_t1dms.SQg,
                       "IV_insulin": matlab.double(IV_insulin),
                       "IV_glucose": matlab.double(IV_glucose),
                       "QIVD": 'total',
                       "QIVins": 'total',
                       "SCNname": 'template',
                       "Qbolus": scenario.params_t1dms.Qbolus,
                       "simToD": scenario.params_t1dms.simToD,
                       "basal": scenario.params_t1dms.basal,
                       "Qbasal": scenario.params_t1dms.Qbasal
                     },

                    'hardwareN': {'sensor': scenario.params_t1dms.hardwareN_sensor,
                                  'pump': scenario.params_t1dms.hardwareN_pump},
                    'hardware': {'SensorType': scenario.params_t1dms.hardware_sensorType}
                    }

        return T1DMSData, patient_data, False

    @staticmethod
    def checkDate(date):
        try:
            datetime.datetime.strptime(date, DATETIME_FORMAT)
            return False
        except:
            return ERROR_CODES.DATE_INVALID
    @staticmethod
    def sort(time_array, values):
        values = [x for _, x in sorted(zip(time_array, values))]
        time_array = np.sort(time_array)
        return time_array,values
