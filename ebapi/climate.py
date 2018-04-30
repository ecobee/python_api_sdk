"""A Ecobee Climate."""
import copy


class Climate:

    def __init__(self, json):
        self.json = json

    def to_json(self):
        return copy.deepcopy(self.json)

    def __str__(self):
        str_rep = "Climate\n"
        str_rep += "\tName: {}\n".format(self.json["name"])
        if self.has_climate_ref():
            str_rep += "\tClimate Ref: {}\n".format(self.json["climateRef"])
        str_rep += "\tCool Stp: {}\n".format(self.json["coolTemp"] / 10)
        str_rep += "\tHeat Stp: {}\n".format(self.json["heatTemp"] / 10)
        str_rep += "\tSensors: {}\n".format(self.json["sensors"])

        return str_rep

    def has_climate_ref(self):
        try:
            self.json["climateRef"]
            return True
        except KeyError:
            return False

    def get_name(self):
        return self.json["name"]

    def get_cool_heat_stps(self):
        return (self.json["coolTemp"], self.json["heatTemp"])

    def set_sensors(self, sensor_list):
        self.json["sensors"] = sensor_list
