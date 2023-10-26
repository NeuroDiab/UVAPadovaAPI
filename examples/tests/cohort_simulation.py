import numpy as np

from src.Simulator.OESimulator.SimulationData.Scenario import Scenario
from src.Simulator.OESimulator.DataProcessor import DataProcessor
from src.Simulator.UVAPadova.VirtualPatientT1DMS import VirtualPatientT1DMS
import matlab.engine
import pickle

tstart = 0
tend = 1700

patients = ["adult#001.mat","adult#002.mat","adult#003.mat","adult#004.mat","adult#005.mat",
            "adult#006.mat","adult#007.mat","adult#008.mat","adult#009.mat","adult#010.mat"]

insulin_scalers = [0.5,0.5,0.7,0.3,0.5,1,0.5,1,0.3,0.3]

patient = VirtualPatientT1DMS(patient_name="adult#001.mat", BGinit=matlab.double([]))  # , eng=eng, path=path

for patient_name,insulin_scaler in zip(patients,insulin_scalers):

    patient.patient = patient_name

    b = np.asarray([3,3,4,3,3,2])*insulin_scaler
    bt = [7.3*60, 10.3*60, 13*60, 15.25*60, 18.25*60, 21.1*60]
    m = np.asarray([35,10,65,20,45])
    mt = [7.5*60, 10.5*60, 12*60, 16.5*60, 18.5*60]

    b = tuple(b)
    bt = tuple(bt)
    m = tuple(m)
    mt = tuple(mt)
    Tsim = float(tend - tstart)
    scenario = Scenario(tstart,tend,"t1dms")
    scenario.Ts = 1
    scenario.setManualMealScheme(meal_times=mt, meal_values=m, unit='g')
    scenario.setManualBolusScheme(bolus_times=bt, bolus_values=b, unit='U')
    scenario.setManualBasalInsulin(patient.Quest.basal, unit=r"U/hr")
    scenario.setHardware(sensor='guardianRT.scs', pump='Generic_1.pmp')
    scenario.setParamsT1DMS()

    T1DMSprocessor = DataProcessor()
    T1DMSdata, patient_data = T1DMSprocessor.processData(scenario=scenario)


    patient.simulatePatient(simulation_data=T1DMSdata)

    # save_object = {}
    # save_object["scenario"] = Scenario
    # save_object["data"] = T1DMSdata
    # save_object["result"] = patient.result
    # filehandler = open(patient_name+".pkl", "wb")
    # pickle.dump(save_object, filehandler)

    scenario.plot(show=False)
    patient.plotHistoricalStates()