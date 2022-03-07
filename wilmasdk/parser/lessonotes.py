#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela
import datetime
from .schedule import parse_wilma_date

"""
Converting Visma's format to more coding-friendly format, because their own is confusing and not logical
Visma! Write that down! Write that down!
"""


def existenceCheck(dist_item, key):
    return key in dist_item and dist_item[key] is not None


def optimizeLessonNote(lesson_note):
    newLessonNote = {'id': -1, 'timestamp': None, 'duration': -1,
                     'teacher': {'id': -1, 'name': None, 'code': None},
                     'course': {'id': -1, 'name': None},
                     'type': {'id': -1, 'codeName': None, 'shortName': None, 'name': None},
                     'disc': {'id': -1, 'name': None},
                     'colors': {'foreground': None, 'background': None},
                     'info': None,
                     'requiresClearance': False,
                     "raw": lesson_note
                     }
    if existenceCheck(lesson_note, 'Id'):
        newLessonNote['id'] = lesson_note['Id']
    if existenceCheck(lesson_note, 'TimeStamp'):
        newLessonNote['timestamp'] = parse_wilma_date(lesson_note['TimeStamp']).date()
    if existenceCheck(lesson_note, 'Duration'):
        newLessonNote['duration'] = lesson_note['Duration']
    if existenceCheck(lesson_note, 'TeacherId'):
        newLessonNote['teacher']['id'] = lesson_note['TeacherId']
    if existenceCheck(lesson_note, 'TeacherName'):
        newLessonNote['teacher']['name'] = lesson_note['TeacherName']
    if existenceCheck(lesson_note, 'TeacherCode'):
        newLessonNote['teacher']['code'] = lesson_note['TeacherCode']
    if existenceCheck(lesson_note, 'CourseId'):
        newLessonNote['course']['id'] = lesson_note['CourseId']
    if existenceCheck(lesson_note, 'Course'):
        newLessonNote['course']['name'] = lesson_note['Course']
    if existenceCheck(lesson_note, 'TypeId'):
        newLessonNote['type']['id'] = lesson_note['TypeId']
    if existenceCheck(lesson_note, 'TypeCode'):
        newLessonNote['type']['codeName'] = lesson_note['TypeCode']
    if existenceCheck(lesson_note, 'TypeShort'):
        newLessonNote['type']['shortName'] = lesson_note['TypeShort']
    if existenceCheck(lesson_note, 'TypeName'):
        newLessonNote['type']['name'] = lesson_note['TypeName']
    if existenceCheck(lesson_note, 'ForegroundColor'):
        newLessonNote['colors']['foreground'] = lesson_note['ForegroundColor']
    if existenceCheck(lesson_note, 'BackgroundColor'):
        newLessonNote['colors']['background'] = lesson_note['BackgroundColor']
    if existenceCheck(lesson_note, 'DiscId'):
        newLessonNote['disc']['id'] = lesson_note['DiscId']
    if existenceCheck(lesson_note, 'DiscName'):
        newLessonNote['disc']['name'] = lesson_note['DiscName']
    if existenceCheck(lesson_note, 'ObservationInfo'):
        newLessonNote['info'] = lesson_note['ObservationInfo']
    if existenceCheck(lesson_note, 'RequiresClearance'):
        newLessonNote['requiresClearance'] = lesson_note['RequiresClearance']
    return newLessonNote


def optimizeLessonNotes(lesson_notes):
    newLessonNotes = []
    for lessonNote in lesson_notes:
        newLessonNotes.append(optimizeLessonNote(lessonNote))
    return newLessonNotes


def optimizeAbsenceInfo(absence_info):
    absence_info['available'] = (absence_info['ReportDate'] != 0)
    return absence_info
