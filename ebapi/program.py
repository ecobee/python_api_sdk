"""A Ecobee Program."""

from .schedule import Schedule
from .climate import Climate


class Program:

    def __init__(self, schedule, climates):
        self.schedule = schedule
        self.climates = climates

    def to_json(self):
        json = {"schedule": self.schedule.to_json(),
                "climates": [c.to_json() for c in self.climates]}
        return json

    def add_climate(self, climate):
        self.climates.append(climate)

    def remove_climate_if_exists(self, name):
        for c in self.climates:
            if c.get_name() == name:
                self.climates.remove(c)
                break

    def __str__(self):
        str_rep = "Program:\n"
        for c in self.climates:
            str_rep += str(c)
        str_rep += str(self.schedule)
        return str_rep

    def get_cool_heat_stps(self, name):
        for climate in self.climates:
            if climate.get_name() == name:
                return climate.get_cool_heat_stps()
        raise ValueError("No climate Named {}".format(name))
