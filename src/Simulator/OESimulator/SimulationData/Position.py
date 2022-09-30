class Position(object):
    """ Defines the position (column index) of the data of interest in an ndarray.
            Defined by __slots__ as the class only serves quick data access purposes.

            Args:
                basal: Position (column index) of the basal rate value in an ndarray.
                bolus: Position (column index) of the bolus value in an ndarray.
                meal: Position (column index) of the cho content in an ndarray.
                time_constant: Position (column index) of the time constant in an ndarray.
                glucose_level: Position (column index) of the glucose value in an ndarray.
    """
    __slots__ = ['basal','bolus','meal',
                'glucose_level','time_constant']
    def __init__(self):
        """ Constructor initalized with default position values.
        """
        self.basal: int = 1
        self.bolus: int = 1
        self.meal: int = 1
        self.time_constant: int = -1
        self.glucose_level: int = 1

    @property
    def __dict__(self):
        return {s: getattr(self, s, None) for s in self.__slots__}

    def copy(self):
        """ Create a deep copy of the instance.

        Returns:
            Position : Deep copy of the instance.

        """
        position = Position()
        for attribute in self.__slots__:
            if hasattr(self, attribute):
                setattr(position, attribute, getattr(self, attribute))
        return position
