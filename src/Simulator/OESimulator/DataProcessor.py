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


import xml.etree.ElementTree as et
import pandas as pd
import numpy as np
import os
from typing import Union, Tuple, List
import pickle
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
        if error:
            print("Error during data processing: "+error)
        else:
            print("Input data processing finished.")
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
        if not db_file.loadExercise():
            return [], [], ERROR_CODES.EXERCISE_INVALID

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
        exercise_times, exercise_values = self.sort(db_file.exercise_times, db_file.exercise_values)


        if not basal_values:
            print("Basal value not found.")
            basal_values = 0.0
            basal_times = glucose_times[0]

        glucose_values = np.interp(np.linspace(glucose_times[0], glucose_times[-1], int((glucose_times[-1] - glucose_times[0]) / 5.0)), glucose_times, glucose_values)
        glucose_times = np.linspace(glucose_times[0], glucose_times[-1], int((glucose_times[-1] - glucose_times[0]) / 5.0))

        scenario.setManualMealScheme(meal_times, meal_values)
        scenario.setManualBolusScheme(bolus_times, bolus_values)
        scenario.setManualBasalInsulin(basal_values, basal_times)
        scenario.setManualExerciseScheme(exercise_values,exercise_times)
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
        simulation_data.exercise.as_timestamped_array = scenario.manual_exercises

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
        simulation_data.exercise.copyTimestampedArrayToArray(simulation_data.t_start,simulation_data.scenario.Ts,simulation_data.scenario.position.exercise)


        simulation_data.bolus.as_array = simulation_data.scenario.units.convertUnits(simulation_data.bolus.as_array, simulation_data.scenario.units.bolus,
                                                          simulation_data.units.insulin, simulation_data.scenario.Ts)
        simulation_data.basal.as_array = simulation_data.scenario.units.convertUnits(simulation_data.basal.as_array, simulation_data.scenario.units.basal,
                                                     simulation_data.units.insulin, simulation_data.scenario.Ts)

        return simulation_data, patient_data, False

    def t1dmsProcess(self, scenario: Scenario, input_data=None): # UVa-Padova

        import matlab.engine
        print("Converting Scenario to T1DMS data...")
        self.data_source = "t1dms"
        patient_data = None  #self.patient_id
        Ameals_init = 30#np.sum(scenario.manual_meals[:,1])
        Ameals2 = []
        Ameals2.append(Ameals_init)
        for meal in scenario.manual_meals[:,1]:
            Ameals2.append(meal)
        Ameals = list(np.array(scenario.manual_meals[:,1]))
        dose = list(np.multiply(np.array(Ameals2), 1000)) # meal amount in mg
        Tdose2 = [0]
        for times in scenario.manual_meals[:,0]:
            Tdose2.append(times)
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
        for i in range(len(Tdose)):
            Tdose[i] = float(Tdose[i])
        for i in range(len(Ameals)):
            Ameals[i] = float(Ameals[i])
        for i in range(len(Tmeals)):
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

            t_meals = []
            for i in range(len(meals)):
                t_meals.append(meals[i][0])

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
                       "Tdose": matlab.double(Tdose2),
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

    def readfromxmltodict(self,path):
        xtree = et.parse(path)
        xroot = xtree.getroot()
        data = {}
        for node in xroot:
            data[node.tag] = []
            for f in node.getchildren():
                data[node.tag].append(f.attrib)
        return data

    def to_xml(self, df, filename=None, mode='w'):
        def row_to_xml(row):
            xml = ['<item>']
            for i, col_name in enumerate(row.index):
                xml.append('  <field name="{0}">{1}</field>'.format(col_name, row.iloc[i]))
            xml.append('</item>')
            return '\n'.join(xml)

        res = '\n'.join(df.apply(row_to_xml, axis=1))
        res = '<?xml version="1.0" encoding="UTF-8" ?>\n<root>\n' + res + '\n</root>'
        if filename is None:
            return res
        with open(filename, mode) as f:
            f.write(res)

    def readfromxmltodataframe(self, path, cols):
        xtree = et.parse(path)
        xroot = xtree.getroot()
        data = []
        for node in xroot:
            lis = []
            for c in node.getchildren():
                lis.append(c.text)
            data.append(lis)
        if cols == None:
            return pd.DataFrame(data)
        else:
            return pd.DataFrame(data, columns=cols)

    @staticmethod
    def saveObject(object, file_path_name: str):
        if os.path.exists(file_path_name+".obj"):
            print("File "+file_path_name+" already exists. Press ENTER to overwrite or specify NEW_PATH_NAME:")
            answer = input()
            if answer == "":
                filehandler = open(file_path_name + ".obj", "wb")
            else:
                filehandler = open(answer + ".obj", "wb")
        else:
            filehandler = open(file_path_name+".obj", "wb")
        pickle.dump(object, filehandler)

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
