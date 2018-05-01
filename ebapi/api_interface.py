"""This class know how to format jsons to get and post to the ecobee API."""

from .api_connection import ApiConnection, ApiError
from .program import Program
from .climate import Climate
from .schedule import Schedule
from .vacation import from_json


class ApiInterface:
    """This class abstracts what we can ask the api and get from the api."""

    def __init__(self, verbose=False):
        self.conn = ApiConnection(verbose)

    def delete_vacations(self, names, identifier):
        funcs = [wrap_delete_vacation(n) for n in names]
        self.conn.send_functions(funcs, identifier)

    def send_vacations(self, vacations, identifier):
        funcs = [wrap_create_vacation(v.to_json()) for v in vacations]
        return self.conn.send_functions(funcs, identifier)

    def get_precool_settings(self, identifier):
        settings = self.get_settings(identifier)
        resp = {"disablePreCooling": settings["disablePreCooling"]}
        return resp

    def update_disable_precool_setting(self, identifier, cool_flag):
        body = {"disablePreCooling": cool_flag}
        return self.update_settings(body, identifier)

    def update_program(self, program, identifier):
        body = {"thermostat": {"program": program.to_json()}}
        return self.conn.send_post(body, identifier)

    def update_settings(self, settings, identifier):
        body = {"thermostat": {"settings": settings}}
        return self.conn.send_post(body, identifier)

    def get_times(self, identifier):
        body = {}
        resp = self.conn.send_get(body, identifier)
        resp_json = {"utc": resp["utcTime"],
                     "local": resp["thermostatTime"]}
        return resp_json

    def get_lat_lon(self, identifier):
        body = {"selection": {"includeLocation": True}}
        resp = self.conn.send_get(body, identifier)
        return {"lat_long": resp["location"]["mapCoordinates"]}

    def get_program(self, identifier):
        p_json = self.get_program_json(identifier)
        sched = Schedule(p_json["program"]["schedule"])
        climates = [Climate(c) for c in p_json["program"]["climates"]]
        prog = Program(sched, climates)
        return prog

    def get_program_json(self, identifier):
        body = {"selection": {"includeProgram": True}}
        return self.conn.send_get(body, identifier)

    def get_settings(self, identifier):
        body = {"selection": {"includeSettings": True}}
        resp = self.conn.send_get(body, identifier)
        return resp['settings']

    def get_sensors(self, identifier):
        body = {"selection": {"includeSensors": True}}
        resp = self.conn.send_get(body, identifier)
        sensors = resp["remoteSensors"]
        return sensors

    def get_vacations(self, identifier):
        events = self.get_events(identifier)
        rt_events = []
        for event in events:
            if event["type"] == "vacation":
                vac = from_json(event)
                rt_events.append(vac)
        return rt_events

    def get_events(self, identifier):
        body = {"selection": {"includeEvents": True}}
        resp = self.conn.send_get(body, identifier)
        return resp["events"]

    def get_extended_runtime(self, identifier):
        body = {"selection": {"includeExtendedRuntime": True}}
        resp = self.conn.send_get(body, identifier)
        return resp["extendedRuntime"]

    def get_runtime_and_sensors(self, identifier):
        body = {"selection": {"includeRuntime": True,
                              "includeSensors": True}}
        resp = self.conn.send_get(body, identifier)
        resp_json = {"runtime": resp["runtime"],
                     "sensors": resp["remoteSensors"]}
        return resp_json

    def get_temp(self, identifier):
        rt_and_snsrs = self.get_runtime_and_sensors(identifier)
        time = rt_and_snsrs["runtime"]["lastStatusModified"]
        sensors = rt_and_snsrs["sensors"]
        for sensor in sensors:
            if sensor["type"] == "thermostat":
                for cape in sensor["capability"]:
                    if cape["type"] == "temperature":
                        return {"time": time,
                                "temp": cape["value"]}
        raise ApiError("No thermostat temperature found")

    def add_user(self):
        self.conn.add_user()
    
    def rm_user(self, tstat_id):
        self.conn.tokens.delete(tstat_id)

def wrap_create_vacation(vacation):
    create_function = {"type": "createVacation",
                       "params": vacation}
    return create_function


def wrap_delete_vacation(name):
    delete_function = {"type": "deleteVacation",
                       "params": {"name": name}}
    return delete_function
