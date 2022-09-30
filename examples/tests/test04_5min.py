from src.UVAPadovaAPIWrapper import UvaPadovaAPI
import numpy as np
from scipy.io import savemat


tsim = 1440
tsim=int(tsim/5)
insulins = np.zeros(tsim)
chos = np.zeros(tsim)

virtual_patient = UvaPadovaAPI()
virtual_patient.initializePatient("adult#002")
for i in range(tsim):
    step_result = virtual_patient.doSimulation(chos[i],insulins[i])
    print(step_result)
#savemat('test5_4.mat',{'Glucose':virtual_patient.listOfBloodGlucoseValues})
print("")