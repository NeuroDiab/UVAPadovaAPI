from src.UVAPadovaAPIWrapper import UvaPadovaAPI
import numpy as np
from scipy.io import savemat


tsim = 1440
tsim=int(tsim/5)
insulins = np.zeros(tsim)
chos = np.zeros(tsim)

for i in range(1,tsim+1):
    if i%24 == 0:
        if (i/24)%2 == 0:
            insulins[i-1] = 2
            chos[i-1] = 45
        else:
            insulins[i-1] = 1
            chos[i-1] = 30

virtual_patient = UvaPadovaAPI()
virtual_patient.initializePatient("adolescent#003")
for i in range(tsim):
    step_result = virtual_patient.doSimulation(chos[i],insulins[i])
    print(step_result)
#savemat('test5_3.mat',{'Glucose':virtual_patient.listOfBloodGlucoseValues})
print("")