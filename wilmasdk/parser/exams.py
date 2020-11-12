#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

import bs4
import datetime


def existenceCheck(dist_item, key):
    return key in dist_item and dist_item[key] is not None


"""
Converting Visma's format to more coding-friendly format, because their own is confusing and not logical
Visma! Write that down! Write that down!
"""


def optimizeExam(exam):
    newExam = {'id': -1, 'examId': -1, 'name': None, 'date': None, 'info': None, 'unseen': False,
               'course': {'id': -1, 'shortName': None, 'name': None, 'teachers': []},
               'grade': {'grade': None, 'verbal': None}}
    if existenceCheck(exam, 'Id'):
        newExam['id'] = exam['Id']
    if existenceCheck(exam, 'ExamId'):
        newExam['examId'] = exam['ExamId']
    if existenceCheck(exam, 'Course'):
        newExam['course']['shortName'] = exam['Course']
    if existenceCheck(exam, 'CourseId'):
        newExam['course']['id'] = exam['CourseId']
    if existenceCheck(exam, 'CourseTitle'):
        newExam['course']['name'] = exam['CourseTitle']
    if existenceCheck(exam, 'Teachers'):
        for teacher in exam['Teachers']:
            newExam['course']['teachers'].append(optimizeTeacher(teacher))
    if existenceCheck(exam, 'Name'):
        newExam['name'] = exam['Name']
    if existenceCheck(exam, 'Unseen'):
        newExam['unseen'] = exam['Unseen']
    if existenceCheck(exam, 'Info'):
        newExam['info'] = bs4.BeautifulSoup(exam['Info'], 'html.parser').text
    if existenceCheck(exam, 'Date'):
        newExam['date'] = datetime.datetime.strptime(exam['Date'], '%Y-%m-%d')
    if existenceCheck(exam, 'Grade'):
        newExam['grade']['grade'] = exam['Grade']
    if existenceCheck(exam, 'VerbalGrade'):
        newExam['grade']['verbal'] = exam['VerbalGrade']
    return newExam


"""
Optimizing many exams using the method above
"""


def optimizeExams(exams):
    newExams = []
    for exam in exams:
        newExams.append(optimizeExam(exam))
    return newExams


def optimizeTeacher(teacher):
    newTeacher = {'id': -1, 'code': None, 'name': None}
    if existenceCheck(teacher, 'TeacherId'):
        newTeacher['id'] = teacher['TeacherId']
    if existenceCheck(teacher, 'TeacherName'):
        newTeacher['name'] = teacher['TeacherName']
    if existenceCheck(teacher, 'TeacherCode'):
        newTeacher['code'] = teacher['TeacherCode']
    return newTeacher
