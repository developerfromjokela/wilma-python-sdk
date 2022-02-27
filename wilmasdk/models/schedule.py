#  Copyright (c) 2022 Developer From Jokela.
#  @author developerfromjokela

class Resource:

    def __init__(self, id, raw, type="resource"):
        self.id = id
        self.raw = raw
        self.type = type


class Teacher(Resource):

    def __init__(self, id, raw, code_name, name):
        super().__init__(id, raw, "teacher")
        self.code_name = code_name
        self.name = name


class Room(Resource):

    def __init__(self, id, raw, code_name, name):
        super().__init__(id, raw, "room")
        self.code_name = code_name
        self.name = name


class Course(Resource):

    def __init__(self, id, raw, course_id, short_code, code_name, name, class_name, teachers, rooms):
        super().__init__(id, raw, "course")
        self.course_id = course_id
        self.short_code = short_code
        self.class_name = class_name
        self.teachers = teachers
        self.rooms = rooms
        self.code_name = code_name
        self.name = name


class Reservation(Resource):

    def __init__(self, id, raw, schedule_id, date, start, end, class_name, courses):
        super().__init__(id, raw, "reservation")
        self.schedule_id = schedule_id
        self.date = date
        self.start = start
        self.end = end
        self.class_name = class_name
        self.courses = courses


class Term:

    def __init__(self, raw, name, start, end) -> None:
        self.name = name
        self.raw = raw
        self.start = start
        self.end = end


class Day:

    def __init__(self, raw, date, reservations: [Reservation]) -> None:
        super().__init__()
        self.date = date
        self.raw = raw
        self.reservations = reservations
