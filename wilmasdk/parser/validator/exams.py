#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

def validateExam(exam):
    requiredFields = ['id', 'examId']
    return all(name in excuse for name in requiredFields)
