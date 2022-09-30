from src.Simulator.OESimulator.SimulationData.Scenario import Scenario
from src.Simulator.OESimulator.DataProcessor import DataProcessor
from src.Simulator.UVAPadova.VirtualPatientT1DMS import VirtualPatientT1DMS
import matlab.engine

tstart = 0
tend = 1440
b = [4,7,2,8,2]
bt = [7*60,12*60,16*60,18*60,23*60]
m = [45,70,20,80,20]
mt = [7*60,12*60,16*60,18*60,23*60]

b = tuple(b)
bt = tuple(bt)
m = tuple(m)
mt = tuple(mt)
Tsim = float(tend - tstart)
scenario = Scenario(tstart,tend,"t1dms")
scenario.Ts = 1
scenario.setManualMealScheme(meal_times=mt, meal_values=m, unit='g')
scenario.setManualBolusScheme(bolus_times=bt, bolus_values=b, unit='U')
scenario.setManualBasalInsulin(0.0, unit=r"U/hr")
scenario.setHardware(sensor='guardianRT.scs', pump='Generic_1.pmp')
scenario.setParamsT1DMS()

T1DMSprocessor = DataProcessor()  # Tsimul, Tclosed, hardware, IVgluc,ins are in dataprocessor
T1DMSdata, patient_data = T1DMSprocessor.processData(scenario=scenario)

patient = VirtualPatientT1DMS(patient_name="adolescent#001.mat", BGinit=matlab.double([])) # , eng=eng, path=path

patient.simulatePatient(simulation_data=T1DMSdata) # matlab engine
patient.simulatePatient(simulation_data=T1DMSdata)
patient.simulatePatient(simulation_data=T1DMSdata)
patient.plotHistoricalStates()