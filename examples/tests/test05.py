from src.Simulator.OESimulator.SimulationData.Scenario import Scenario
from src.Simulator.OESimulator.DataProcessor import DataProcessor
from src.Simulator.UVAPadova.VirtualPatientT1DMS import VirtualPatientT1DMS
import matlab.engine

tstart = 0
tend = 60
b = []
bt = []
m = []
mt = []

# test05: bolus insulin increasing by 0.1 U in every 5 minutes starting from 0.1 U,
#         0.0 U basal insulin, no meal

for i in range(1,tend+1):
    if i%5 == 0:
        b.append(round(0.1*(i/5),1))
        bt.append(i)

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

patient = VirtualPatientT1DMS(patient_name="adult#001.mat", BGinit=matlab.double([])) # , eng=eng, path=path

patient.simulatePatient(simulation_data=T1DMSdata) # matlab engine

patient.plotHistoricalStates()
