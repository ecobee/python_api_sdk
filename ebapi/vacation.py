"""This file contains an Ecobee Vacation Event."""

import datetime as dt
dt_fmt = "%Y-%m-%d %H:%M:%S"

class Vacation:
    """An Ecobee API Vacation."""

    def __init__(self, dt_start, dt_end,
                 cool_stp, heat_stp, name):
        self.dt_start = dt_start
        self.dt_end = dt_end
        self.cool_stp = cool_stp
        self.heat_stp = heat_stp
        self.name = name
        self.validate()

    def validate(self):
        self.validate_stps()
        self.validate_times()

    def validate_stps(self):
        if self.heat_stp > self.cool_stp:
            raise ValueError("Heat Stp must be above Cool Stp.")

    def validate_times(self):
        if self.dt_end < self.dt_start:
            raise ValueError("End cannot be before Start")

    def to_json(self):
        st_date, st_time = self.dt_start.strftime(dt_fmt).split(" ")
        end_date, end_time = self.dt_end.strftime(dt_fmt).split(" ")
        vacation = {"Type": "dateTime",
                    "name": "irs_vac" + self.name,
                    "coolHoldTemp": convert_temp(self.cool_stp),
                    "heatHoldTemp": convert_temp(self.heat_stp),
                    "startDate": st_date,
                    "startTime": st_time,
                    "endDate": end_date,
                    "endTime": end_time}
        return vacation

    def to_sql(self):
        sql_str_fmt = "[{}, {}, {}, {}, {}]"
        start = self.dt_start.strftime(dt_fmt)
        end = self.dt_end.strftime(dt_fmt)
        sql_str = sql_str_fmt.format(start, end, self.cool_stp,
                                     self.heat_stp, self.name)
        return sql_str

    def __str__(self):
        str_rep = "Vacation: {}\n".format(self.name)
        st_str = self.dt_start.strftime(dt_fmt)
        end_str = self.dt_end.strftime(dt_fmt)
        str_rep += "\tStart: {}\n".format(st_str)
        str_rep += "\tEnd: {}\n".format(end_str)
        str_rep += "\tCool STP: {}°f\n".format(self.cool_stp)
        str_rep += "\tHeat STP: {}°f".format(self.heat_stp)
        return str_rep

    def __repr__(self):
        return self.__str__()


def convert_temp(temp):
    return int(temp * 10)


def from_json(json):
    dt_start = gen_dt("start", json)
    dt_end = gen_dt("end", json)
    cool_stp = unpack_temp("cool", json)
    heat_stp = unpack_temp("heat", json)
    name = json["name"]
    return Vacation(dt_start, dt_end, cool_stp, heat_stp, name)


def gen_dt(name, json):
    date = json[name + "Date"]
    time = json[name + "Time"]
    dt_str = "{} {}".format(date, time)
    return dt.datetime.strptime(dt_str, dt_fmt)


def unpack_temp(name, json):
    return int(json[name + "HoldTemp"]) / 10
