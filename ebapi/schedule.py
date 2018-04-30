"""An Ecobee API Schedule."""

import datetime as dt


class Schedule:

    def __init__(self, week_schedule):
        self.days = [Day(i, sched) for i, sched in enumerate(week_schedule)]

    def __str__(self):
        str_rep = "Week Schedule:\n"
        for day in self.days:
            str_rep += str(day)
        return str_rep

    def replace_weekdays(self, dt_start, dt_end, climate_id):
        weekdays = self.get_weekday_indicies()
        self.update_schedule(weekdays, dt_start, dt_end, climate_id)

    def update_schedule(self, day_nums, dt_start, dt_end, climate_id):
        for day_num in day_nums:
            self.days[day_num].modify_schedule(dt_start,
                                               dt_end,
                                               climate_id)

    def to_json(self):
        return [day.schedule for day in self.days]

    def get_weekday_indicies(self):
        for i in range(5):
            yield i


class Day:

    def __init__(self, day_num, schedule):
        days_of_the_week = ["Monday",
                            "Tuesday",
                            "Wednesday",
                            "Thursday",
                            "Friday",
                            "Saturday",
                            "Sunday"]
        self.day_of_week = days_of_the_week[day_num]
        self.schedule = schedule

    def __str__(self):
        str_rep = self.day_of_week + "\n"
        vals = collapse(self.schedule)
        for start, end, climate in vals:
            start_time = get_time(start)
            end_time = get_time(end)
            str_rep += "\t{} from {} to {}\n".format(climate,
                                                     start_time, end_time)
        return str_rep

    def modify_schedule(self, start_time, end_time, climate):
        if start_time > end_time:
            raise ValueError("Start Time must be after End Time")

        start_index = get_index(start_time)
        end_index = get_index(end_time)
        for i in range(start_index, end_index + 1):
            self.schedule[i] = climate


def get_time(index):
    hour = index // 2
    minute = (index % 2) * 30
    return dt.time(hour, minute)


def get_index(time):
    return int(time.hour * 2 + time.minute / 30)


def collapse(alist):
    rt_list = []
    current = alist[0]
    start_index = 0
    for i, val in enumerate(alist[1:]):
        if val != current:
            rt_list.append((start_index, i, current))
            current = val
            start_index = i + 1
    rt_list.append((start_index, i + 1, val))
    return rt_list
