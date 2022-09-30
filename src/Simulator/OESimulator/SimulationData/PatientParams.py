import numpy as np
from random import gauss

from . import CONSTANTS
from .DataContainer import DataContainer

class PatientParams(object):
    """ Stores the mathematical model parameters of the patient.
            Defined by __slots__ as the class only serves quick data access purposes.

            Args:
                BW (float): Body weight of the patient.
                GEZI (DataContainer): Glucose consumption at zero insulin level.
                EGP (DataContainer): Endogenous glucose production.
                CI (float): Insulin clearance.
                tau1 (float): Time constant of the absorption of the insulin in the 1st compartment.
                tau2 (float): Time constant of the absorption of the insulin in the 2nd compartment.
                p2 (float): Rate constant of the insulin effect.
                taud (DataContainer):  Time constant of the absoprtion of the CHO.
                meals (DataContainer): CHO contents of the meals.

            Examples:
                >>> print(PatientParams(sigma=0.0))
                ---------------------------
                Patient parameters: BW:70 GEZI:3e-08 EGP:1.5 CI:1.2e+03 SI:0.0007 tau1:70 tau2:43 p2:0.01 taud:40 Vg:1.8e+02
                 meal_tauds:
                ---------------------------
    """
    __slots__ = ['EGP','GEZI','p2','tau1','tau2','taud','Vg','BW','CI','SI','meals','is_up_to_date']

    def __init__(self, sigma: float = 0.0):
        """ Constructor.
            sigma : Standard deviation, when a random patient is being created from a normal distribution.
        """
        generated_params = [CONSTANTS.NOMINAL_BW + gauss(0, CONSTANTS.SIGMA_BW) * sigma, CONSTANTS.NOMINAL_GEZI + gauss(0, CONSTANTS.SIGMA_GEZI) * sigma,
                            CONSTANTS.NOMINAL_EGP + gauss(0, CONSTANTS.SIGMA_EGP) * sigma, CONSTANTS.NOMINAL_CI + gauss(0, CONSTANTS.SIGMA_CI) * sigma,
                            CONSTANTS.NOMINAL_SI + gauss(0, CONSTANTS.SIGMA_SI) * sigma, CONSTANTS.NOMINAL_TAU1 + gauss(0, CONSTANTS.SIGMA_TAU1) * sigma,
                            CONSTANTS.NOMINAL_TAU2 + gauss(0, CONSTANTS.SIGMA_TAU2) * sigma, CONSTANTS.NOMINAL_P2 + gauss(0, CONSTANTS.SIGMA_P2) * sigma,
                            CONSTANTS.NOMINAL_TAUD + gauss(0, CONSTANTS.SIGMA_TAUD) * sigma, CONSTANTS.NOMINAL_VG + gauss(0, CONSTANTS.SIGMA_VG) * sigma]
        # Constrains the parameters to be relevant ranges.
        if sigma > 0.0:
            generated_params = [min_param if param < min_param else param
                                for (param, min_param) in zip(generated_params, CONSTANTS.MIN_PARAMS)]
            generated_params = [max_param if param > max_param else param
                                for (param, max_param) in zip(generated_params, CONSTANTS.MAX_PARAMS)]
        self.BW: float = generated_params[0]
        self.GEZI: DataContainer = DataContainer(scalar=generated_params[1])
        self.EGP: DataContainer = DataContainer(scalar=generated_params[2])
        # self.EGP: float = generated_params[2]
        self.CI: float = generated_params[3]
        self.SI: DataContainer = DataContainer(scalar=generated_params[4])
        self.tau1: float = generated_params[5]
        self.tau2: float = generated_params[6]
        self.p2: float = generated_params[7]
        self.taud: DataContainer = DataContainer(scalar=generated_params[8])
        self.Vg: float = generated_params[9]
        self.taud.as_array = np.array([], dtype=np.float64)
        self.meals: np.ndarray = np.array([], dtype=np.float64)
        self.EGP.as_array = self.EGP.as_scalar*np.ones(1, dtype=np.float64)
        self.GEZI.as_array = self.GEZI.as_scalar*np.ones(1, dtype=np.float64)
        self.SI.as_array = self.SI.as_scalar*np.ones(1, dtype=np.float64)
        self.is_up_to_date: bool = False

    @property
    def __dict__(self):
        return {s: getattr(self, s, None) for s in self.__slots__}

    def __repr__(self):
        """ Parameter representations.
        """
        lines = "---------------------------\n"
        representation = "Patient parameters: BW:%0.2g GEZI:%0.2g EGP:%0.2g CI:%0.2g SI:%0.2g tau1:%0.2g tau2:%0.2g" \
               " p2:%0.2g taud:%0.2g Vg:%0.2g \n meal_tauds:" % (self.BW, self.GEZI.as_scalar, self.EGP.as_scalar, self.CI, self.SI.as_scalar
                                                  , self.tau1, self.tau2, self.p2, self.taud.as_scalar, self.Vg)
        meal_tauds = [str("%0.2g"%i)+" " for i in self.taud.as_array]
        return lines+representation + "".join(meal_tauds)+"\n"+lines

    def copy(self):
        """ Create a deep copy of the instance.

        Returns:
            PatientParams : Deep copy of the instance.

        """
        patient_params = PatientParams()
        for attribute in self.__slots__:
            for attribute in self.__slots__:
                if hasattr(self, attribute):
                    if isinstance(getattr(self, attribute), (np.ndarray, DataContainer)):
                        setattr(patient_params, attribute, getattr(self, attribute).copy())
                    else:
                        setattr(patient_params, attribute, getattr(self, attribute))
        return patient_params


    def vectorizeScalarParams(self):
        """ Organizes the scalar patient parameters into a list in the following order: [BW, CI, tau1, tau2, p2, Vg]

        """
        vectorized_params = []
        vectorized_params.append(self.BW)
        vectorized_params.append(self.CI)
        vectorized_params.append(self.tau1)
        vectorized_params.append(self.tau2)
        vectorized_params.append(self.p2)
        vectorized_params.append(self.Vg)
        return vectorized_params
