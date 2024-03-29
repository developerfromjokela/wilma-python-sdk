#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

# Python rewrite of https://github.com/wilmaplus/web-backend/blob/master/utils/schedule_parser.js

from datetime import datetime, timedelta
from wilmasdk.models.schedule import *


def parse_wilma_date(date_string):
    date_format = "%Y-%m-%d"
    backup_format = "%Y-%m-%d %H:%M"
    try:
        date_time_obj = datetime.strptime(date_string, date_format)
    except Exception as e:
        # If timestamp contains time data, use backup format
        if "unconverted data" in str(e) and backup_format is not None:
            date_time_obj = datetime.strptime(date_string, backup_format)
        else:
            return None
    return date_time_obj


def split_week_ranges(start, end):
    diff = (end - start) / 7
    for i in range(7):
        yield start + diff * i
    yield end


def restructure_resource(resource, resource_type):
    return resource_type(resource.get("Id", None), resource, resource.get("Caption", None),
                         resource.get("LongCaption", None))


def restructure_course(group):
    course = Course(
        group.get("Id", None),
        group,
        group.get("CourseId", None),
        group.get("ShortCode", None),
        group.get("Caption", None),
        group.get("FullCaption", None),
        group.get("Class", None),
        [],
        []
    )

    for teacher in group.get("Teachers", []):
        course.teachers.append(restructure_resource(teacher, Teacher))

    for room in group.get("Rooms", []):
        course.rooms.append(restructure_resource(room, Room))

    return course


def parse_wilma_time(time_string, date: datetime = None):
    date_format = "%H:%M"
    backup_format = "%H:%M:%S"
    try:
        date_time_obj = datetime.strptime(time_string, date_format)
    except Exception as e:
        # If timestamp contains time data, use backup format
        if "unconverted data" in str(e) and backup_format is not None:
            date_time_obj = datetime.strptime(time_string, backup_format)
        else:
            return None
    if date is not None:
        return datetime.combine(date, date_time_obj.time())
    return date_time_obj


def restructure(date: datetime, reservation):
    new_reservation = Reservation(reservation.get("ReservationID", -1), reservation, reservation.get("ScheduleID", -1),
                                  date,
                                  parse_wilma_time(reservation.get("Start", None), date),
                                  parse_wilma_time(reservation.get("End", None), date),
                                  reservation.get("Class", None), [])
    for group in reservation.get("Groups", []):
        new_reservation.courses.append(restructure_course(group))

    return new_reservation


def parse_schedule(date: datetime, schedule):
    monday = date - timedelta(days=date.weekday())
    reservation_map = {}
    current_day = schedule[0].get("Day", 1)-1 if len(schedule) > 0 else 0
    last_day = 0
    for schedule_reservation in schedule:
        reservation_date = schedule_reservation.get("Day", -1)
        if reservation_date > last_day:
            if last_day != 0:
                current_day = reservation_date - 1
            last_day = reservation_date

        # Getting date
        corrected_date = datetime.combine((monday + timedelta(days=current_day)), datetime(1970, 1, 1, 0, 0, 0, 0).time())
        restructured_reservation = restructure(date, schedule_reservation)
        unix_time = float(corrected_date.strftime("%s"))
        if unix_time in reservation_map:
            array = reservation_map[unix_time]
            array.append(restructured_reservation)
            reservation_map[unix_time] = array
        else:
            reservation_map[unix_time] = [restructured_reservation]

    # Creating final object
    days = []
    for key in reservation_map.keys():
        timestamp = datetime.fromtimestamp(key)
        days.append(Day(date=timestamp, reservations=reservation_map[key], raw=schedule))

    # Sorting
    def date_sort(value: Day):
        return value.date

    days.sort(key=date_sort)
    return days


def parse_terms(terms):
    parsed_terms = []
    for term in terms:
        parsed_terms.append(
            Term(
                term,
                term.get("Name", None),
                parse_wilma_date(term.get("StartDate", None)),
                parse_wilma_date(term.get("EndDate", None))
            )
        )
    return parsed_terms
