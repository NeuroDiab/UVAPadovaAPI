from src.UVAPadovaAPIWrapper import UvaPadovaAPI
import numpy as np
from scipy.io import savemat


tsim = 60
tsim=int(tsim/5)
insulins = np.zeros(tsim)
chos = np.zeros(tsim)

virtual_patient = UvaPadovaAPI()
virtual_patient.initializePatient("adult#005")

for i in range(tsim):
    step_result = virtual_patient.doSimulation(chos[i],insulins[i])
    print(step_result)
#savemat('test5_2.mat',{'Glucose':virtual_patient.listOfBloodGlucoseValues})
print("")