from src.UVAPadovaAPIWrapper import UvaPadovaAPI
import numpy as np
from scipy.io import savemat


tsim = 1440
tsim=int(tsim/5)
insulins = np.zeros(tsim)
chos = np.zeros(tsim)

# # test 06
b = [4,7,2,8,2]
bt = [7*60,12*60,16*60,18*60,23*60]
m = [45,70,20,80,20]
mt = [7*60,12*60,16*60,18*60,23*60]

for i in range(len(mt)):
    for j in range(1,tsim+1):
        if j*5 == mt[i]:
            insulins[j-1] = b[i]
            chos[j-1] = m[i]

virtual_patient = UvaPadovaAPI()
virtual_patient.initializePatient("adolescent#001")
for i in range(tsim):
    step_result = virtual_patient.doSimulation(chos[i],insulins[i])
    print(step_result)
#savemat('test5_6.mat',{'Glucose':virtual_patient.listOfBloodGlucoseValues})
print("")