FAILED = False
SUCCESS = True

class DBFile():
    def __init__(self, source):
        self.source = source
        self.glucose_values, self.glucose_times = [],[]
        self.meal_values, self.meal_times = [], []
        self.bolus_values, self.bolus_times = [],[]
        self.basal_values, self.basal_times = [],[]

    def loadCGM(self):
        for id, info in self.source.items():
            try:
                if "source" in info:
                    if (info["type"] == "glucose" and (
                            info["source"] == "LIBRE_FREESTYLE" or info["source"] == "CARELINK")):
                        self.glucose_times.append( info["timestamp"] / 60.0)
                        self.glucose_values.append( info["value"] * 18.018)
            except:
                return FAILED
        return SUCCESS

    def loadMeals(self):
        for id, info in self.source.items():
            try:
                if (info["type"] == "meal"):
                    tmp_meal = 0.0
                    for food in info["foods"]:
                        if "carbohydrates" in food["details"]:
                            tmp_meal = tmp_meal + float(food["details"]["carbohydrates"]) * float(food["amount"]) * float(food[
                                "weights"]) / 100.0
                        if "carbohydrate" in food["details"]:
                            tmp_meal = tmp_meal + float(food["details"]["carbohydrate"]) * float(food["amount"]) * float(food[
                                "weights"]) / 100.0
                    self.meal_values.append(tmp_meal)
                    self.meal_times.append(info["timestamp"] / 60.0)
            except BaseException as e:
                print(str(e))
                return FAILED
        return SUCCESS

    def loadInsulin(self):
        for id, info in self.source.items():
            try:
                if info["type"] == "insulin":
                    if (info["subtype"].isnumeric() and int(info["subtype"])<16) or info["subtype"]=="short":
                        self.bolus_values.append(float(info["value"]))
                        self.bolus_times.append(float(info["timestamp"]) / 60.0)
                    if (info["subtype"].isnumeric() and int(info["subtype"])>=16 or info["subtype"]=="long") :
                        self.basal_values.append(float(info["value"]) / 24.0)
                        self.basal_times.append(float(info["timestamp"]) / 60.0)
            except BaseException as e:
                print(str(e))
                return FAILED
        return SUCCESS

