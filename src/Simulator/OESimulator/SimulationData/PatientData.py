import numpy as np
from .PatientParams import PatientParams

class PatientData(object):
    """ Patient data.
            Defined by __slots__ as the class only serves quick data access purposes.
    """
    __slots__ = ['x_hist_timestamped','patient_params_timestamped','patient_id','patient_params']

    def __init__(self):
        """ Constructor.

        """
        # Stores the historically estimated states with timestamps.
        self.x_hist_timestamped: np.ndarray = np.array([], dtype=np.float32)
        # Stores the historically estimated patient parameters.
        self.patient_params_timestamped: np.ndarray = np.array([], dtype=np.float32)
        # Patient ID as in the database.
        self.patient_id: str = ""
        # Current patient parameters.
        self.patient_params = PatientParams()

    @property
    def __dict__(self):
        return {s: getattr(self, s, None) for s in self.__slots__}
