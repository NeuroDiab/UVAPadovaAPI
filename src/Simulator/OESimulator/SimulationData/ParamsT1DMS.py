class ParamsT1DMS:
    """ ParamsT1DMS stores the Uva/Padova simulator related scenario parameters.

            Note:
                All the member variables all the equivalent of the Uva/Padova Matlab simulator variables.

    """
    __slots__ = ['Tsimul','simToD','Qmeals','Tclosed','BGinit','Treg','basal','Qbasal','CR','Qbolus',
                 'IV_glucose','IV_insulin','SQg','OB','CR','meal_duration','hardwareN_sensor','hardwareN_pump',
                 'hardware_sensorType']

    def __init__(self):
        self.simToD : float = 0.0
        self.Qmeals : str = 'total'
        self.Treg : float = 0.0
        self.meal_duration : float = 15.0
        self.Qbasal : str = 'fixed'
        self.OB : str = 'off'
        self.CR : str = 'off'
        self.Qbolus : str = 'total'
        self.SQg : float = 1.0
