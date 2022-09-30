from src.Simulator.OESimulator.SimulationData.Scenario import Scenario
from src.Simulator.OESimulator.DataProcessor import DataProcessor
from src.Simulator.UVAPadova.VirtualPatientT1DMS import VirtualPatientT1DMS
import matlab.engine

tstart = 0
tend = 1440
b = []
bt = []
m = []
mt = []

# test03: 1 U bolus insulin in odd and 2 U in even hours, 1.0 U basal insulin,
#         10 g CH in odd and 20 g in even hours

for i in range(1,tend+1):
    if i%60 == 0:
        if (i/60)%2 == 0:
            b.append(2)
            m.append(20)
        else:
            b.append(1)
            m.append(10)
        mt.append(i)
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
scenario.setManualBasalInsulin(1.0, unit=r"U/hr")
scenario.setHardware(sensor='dexcom.scs', pump='Generic_1.pmp')
scenario.setParamsT1DMS()

T1DMSprocessor = DataProcessor()  # Tsimul, Tclosed, hardware, IVgluc,ins are in dataprocessor
T1DMSdata, patient_data = T1DMSprocessor.processData(scenario=scenario)

patient = VirtualPatientT1DMS(patient_name="adolescent#003.mat", BGinit=matlab.double([])) # , eng=eng, path=path

patient.simulatePatient(simulation_data=T1DMSdata) # matlab engine

patient.plotHistoricalStates()