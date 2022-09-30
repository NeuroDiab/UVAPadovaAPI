import numpy as np
from typing import Union, List, Tuple
# from .Scenario import Scenario


class Units(object):
    """ Defines the units of the variables in strings.
            Defined by __slots__ as the class only serves quick data access purposes.

            Args:
                basal (str): Unit of the basal rate.
                bolus (str): Unit of the bolus insulin.
                insulin (str): Unit of the insulin input.
                meal (str): Unit of the meal.
    """
    __slots__ = ['basal','bolus','insulin','meal']
    def __init__(self):
        """ Constructor initalized with default values.

        """
        self.basal: str = r"U/hr"
        self.bolus: str = "U"
        self.insulin: str = r"uU/min"
        self.meal: str = "g"

    @property
    def __dict__(self):
        return {s: getattr(self, s, None) for s in self.__slots__}

    def copy(self):
        """ Create a deep copy of the instance.

        Returns:
            Units : Deep copy of the instance.

        """
        units = Units()
        for attribute in self.__slots__:
            if hasattr(self, attribute):
                setattr(units, attribute, getattr(self, attribute))
        return units

    @staticmethod
    def convertUnits(original_value: Union[float, np.ndarray], unit_from: str, unit_to: str, Ts: float) -> Union[float, np.ndarray]:
        """ Convert values between different units.

                Note:
                    Possible conversions:
                        from U/hr to uU/min
                        from U to uU/min (based on Ts)
                        from g to g/min (based on Ts)
                        from uU/min to U/min

                Args:
                    original_value : The unconverted value(s).
                    unit_from : Unit of the unconverted value(s).
                    unit_to : Unit of the converted value(s).
                    Ts : Sampling time.

                Returns:
                    Union[float, ndarray] : The converted value(s).

                Examples:
                    >>> print(Units.convertUnits(original_value=10,unit_from="U/hr",unit_to=r"uU/min",Ts=5))
                    166666.666

        """
        if unit_to == unit_from:
            return original_value
        converted_value = 'nan'
        if (unit_from == r"U/hr" and unit_to == r"uU/min"):
            converted_value = original_value / 60.0 * 1E6
        if (unit_from == "U" and unit_to == r"uU/min"):
            converted_value = original_value * 1E6 / Ts
        if (unit_from == r"uU/min" and unit_to == "U"):
            converted_value = original_value / 1E6 * Ts
        if (unit_from == "g" and unit_to == r"g/min"):
            converted_value = original_value / Ts
        if (unit_from == r"uU/min" and unit_to == r"U/min"):
            converted_value = original_value/1E6
        return converted_value



