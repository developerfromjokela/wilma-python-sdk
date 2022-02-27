#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

from wilmasdk.parser.exams import optimizeTeacher, optimizeExam
import datetime
import bs4


def existenceCheck(dist_item, key):
    return key in dist_item and dist_item[key] is not None


"""
Converting Visma's format to more coding-friendly format, because their own is confusing and not logical
Visma! Write that down! Write that down!
"""


def optimizeGroup(group):
    newGroup = {'id': -1, 'courseId': -1, 'name': None, 'codeName': None, 'shortName': None, 'startDate': None,
                'endDate': None, 'teachers': [], 'students': [], 'homework': [], 'exams': [], "raw": group}
    if existenceCheck(group, 'Id'):
        newGroup['id'] = group['Id']
    if existenceCheck(group, 'Id'):
        newGroup['courseId'] = group['CourseId']
    if existenceCheck(group, 'CourseName'):
        newGroup['name'] = group['CourseName']
    if existenceCheck(group, 'CourseCode'):
        newGroup['codeName'] = group['CourseCode']
    if existenceCheck(group, 'Name'):
        newGroup['shortName'] = group['Name']
    if existenceCheck(group, 'StartDate'):
        newGroup['startDate'] = datetime.datetime.strptime(group['StartDate'], '%Y-%m-%d')
    if existenceCheck(group, 'EndDate'):
        newGroup['endDate'] = datetime.datetime.strptime(group['EndDate'], '%Y-%m-%d')
    if existenceCheck(group, 'Teachers'):
        for teacher in group['Teachers']:
            newGroup['teachers'].append(optimizeTeacher(teacher))
    if existenceCheck(group, 'Exams'):
        for exam in group['Exams']:
            newGroup['exams'].append(optimizeGroupExam(newGroup, exam))
    if existenceCheck(group, 'Homework'):
        for homework in group['Homework']:
            newGroup['homework'].append(optimizeHomework(homework))
    if existenceCheck(group, 'Students'):
        for student in group['Students']:
            newGroup['students'].append(optimizeGroupStudent(student))
    return newGroup


"""
Optimizing many groups using the method above
"""


def optimizeGroups(groups):
    newGroups = []
    for group in groups:
        newGroups.append(optimizeGroup(group))
    return newGroups


def optimizeGroupExam(group, exam):
    exam['Course'] = group['shortName'] + ' ' + group['codeName']
    exam['CourseTitle'] = group['name']
    exam['CourseId'] = group['courseId']
    newExam = optimizeExam(exam)
    newExam['teachers'] = group['teachers']
    return newExam


def optimizeGroupStudent(student):
    newStudent = {'id': -1, 'name': None, 'schoolId': -1, 'class': {'id': -1, 'name': None}, "raw": student}
    if existenceCheck(student, 'Id'):
        newStudent['id'] = student['Id']
    if existenceCheck(student, 'Name'):
        newStudent['name'] = student['Name']
    if existenceCheck(student, 'SchoolId'):
        newStudent['schoolId'] = student['SchoolId']
    if existenceCheck(student, 'Class'):
        newStudent['class']['id'] = student['Class']
    if existenceCheck(student, 'ClassName'):
        newStudent['class']['name'] = student['ClassName']
    return newStudent


def optimizeHomework(homework):
    newHomework = {'timestamp': None, 'content': None, "raw": homework}
    if existenceCheck(homework, 'Date'):
        newHomework['timestamp'] = datetime.datetime.strptime(homework['Date'], '%Y-%m-%d')
    if existenceCheck(homework, 'Homework'):
        newHomework['content'] = bs4.BeautifulSoup(homework['Homework'], 'html.parser').text
    return newHomework
