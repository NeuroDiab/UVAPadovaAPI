NOMINAL_BW: float = 69.7
""" Nominal value of the body weight.

"""

NOMINAL_GEZI: float = 3.03e-08
""" Nominal value of the glucose consumption at zero insulin level.

"""

NOMINAL_EGP: float = 1.488
""" Nominal value of the endogenous glucose production.

"""

NOMINAL_CI: float = 1200.0
""" Nominal value of the insulin clearance.

"""

NOMINAL_SI: float = 7.0e-04
""" Nominal value of the insulin sensitivity.

"""

NOMINAL_TAU1: float = 70.0500000000000
""" Nominal value of the time constant of the insulin absorption in the 1st compartment.

"""

NOMINAL_TAU2: float = 43.4
""" Nominal value of the time constant of the insulin absorption in the 2nd compartment.

"""

NOMINAL_P2: float = 0.010288
""" Nominal value of the rate constant of the insulin effect.

"""

NOMINAL_TAUD: float = 40.0
""" Nominal value of the time constant of the CHO absorption.

"""

NOMINAL_VG: float = 180.0
""" Nominal value of the glucose distribution volume.

"""

NOMINAL_PARAMS = [NOMINAL_BW, NOMINAL_GEZI, NOMINAL_EGP, NOMINAL_CI, NOMINAL_SI, NOMINAL_TAU1, NOMINAL_TAU2, NOMINAL_P2, NOMINAL_TAUD, NOMINAL_VG]

SIGMA_BW: float = 1.0
SIGMA_GEZI: float = 3E-9
SIGMA_EGP: float = 0.1
SIGMA_CI: float = 100
SIGMA_SI: float = 1E-5
SIGMA_TAU1: float = 1.0
SIGMA_TAU2: float = 1.0
SIGMA_P2: float = 1E-3
SIGMA_TAUD: float = 1.0
SIGMA_VG: float = 1.0

SIGMA_PARAMS = [SIGMA_BW, SIGMA_GEZI, SIGMA_EGP, SIGMA_CI, SIGMA_SI, SIGMA_TAU1, SIGMA_TAU2, SIGMA_P2, SIGMA_TAUD, SIGMA_VG]


MIN_BW: float = 50.0
""" Minimum value of the body weight.

"""

MIN_GEZI: float = 5E-4
""" Minimum value of the glucose consumption at zero insulin level.

"""

MIN_EGP: float = 0.062
""" Minimum value of the endogenous glucose production.

"""

MIN_CI: float = 372.0
""" Minimum value of the insulin clearance.

"""

MIN_SI: float = 2.3E-6
""" Minimum value of the insulin sensitivity.

"""

MIN_TAU1: float = 10.0
""" Minimum value of the time constant of the insulin absorption in the 1st compartment.

"""

MIN_TAU2: float = 10.0
""" Minimum value of the time constant of the insulin absorption in the 2nd compartment.

"""

MIN_P2: float = 1.0/50.0
""" Minimum value of the rate constant of the insulin effect.

"""

MIN_TAUD: float = 10.0
""" Minimum value of the time constant of the CHO absorption.

"""

MIN_VG: float = 100.0
""" Minimum value of the glucose distribution volume.

"""

MAX_BW: float = 110.0
""" Maximum value of the body weight.

"""

MAX_GEZI: float = 7E-2
""" Maximum value of the glucose consumption at zero insulin level.

"""

MAX_EGP: float = 2.23
""" Maximum value of the endogenous glucose production.

"""

MAX_CI: float = 3350.0
""" Maximum value of the insulin clearance.

"""

MAX_SI: float = 0.0021
""" Maximum value of the insulin sensitivity.

"""

MAX_TAU1: float = 70.0#50.0
""" Maximum value of the time constant of the insulin absorption in the 1st compartment.

"""

MAX_TAU2: float = 50.0
""" Maximum value of the time constant of the insulin absorption in the 2nd compartment.

"""

MAX_P2: float = 1.0/10.0
""" Maximum value of the rate constant of the insulin effect.

"""

MAX_TAUD: float = 60.0
""" Maximum value of the time constant of the CHO absorption.

"""

MAX_VG: float = 1000.0
""" Maximum value of the glucose distribution volume.

"""

MIN_PARAMS = [MIN_BW, MIN_GEZI, MIN_EGP, MIN_CI, MIN_SI, MIN_TAU1, MIN_TAU2, MIN_P2, MIN_TAUD, MIN_VG]
MAX_PARAMS = [MAX_BW, MAX_GEZI, MAX_EGP, MAX_CI, MAX_SI, MAX_TAU1, MAX_TAU2, MAX_P2, MAX_TAUD, MAX_VG]

COLOR_WARNING: str = '\033[93m'
COLOR_OK: str = '\033[92m'
COLOR_FAIL: str = '\033[91m'
COLOR_END: str = '\033[0m'

DATETIME_FORMAT: str = '%d-%m-%Y %H:%M:%S'
""" Date format.

"""