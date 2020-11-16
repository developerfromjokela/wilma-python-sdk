#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

from authdetails import WILMA_SETTINGS
from wilmasdk.sdk import WilmaSDK

sdk = WilmaSDK()

# Login Test

sdk.setWilmaServer(WILMA_SETTINGS['server'])
print("Trying to Log in")

result = sdk.login(WILMA_SETTINGS['username'], WILMA_SETTINGS['password'], WILMA_SETTINGS['apikey'])

if result.is_error():
    if result.get_wilma_error() is not None:
        print(result.get_wilma_error()['message'])
        print("--> " + result.get_wilma_error()['description'])
    else:
        print(result.get_exception())
else:
    print("SID: " + result.session)
    print("Complete!")
    if result.roleSelectionRequired:
        print("Roles required, enter position number")
        passwdFormKey = result.homepage['formKey']
        for pos, role in enumerate(result.homepage['roles']):
            if role['formKey'] != passwdFormKey:
                print(" " + str(pos) + " --> " + role['name'])
        num = input("Enter number: \n")
        numInt = int(num)
        if numInt not in range(1, len(result.homepage['roles'])):
            print("Invalid number!")
            exit(-1)
        else:
            role = result.homepage['roles'][numInt]
            print("Selected role: " + role['name'])
            sdk.setRole(role)
            print("Trying to fetch role's homepage")
            homepageResult = sdk.getHomepage()
            if homepageResult.is_error():
                print(str(homepageResult.get_exception()))
                if homepageResult.get_wilma_error() is not None:
                    print(homepageResult.get_wilma_error())
            else:
                homepage = homepageResult.homepage
                if homepage['formKey'] == role['formKey']:
                    print("Successfully switched to " + homepage['name'] + " role")
                    print("Primus ID: " + str(homepage['primusId']))
                    print("Type: " + str(homepage['type']))
    else:
        print("Roles not required, not selecting")

    exams = sdk.getExams()
    if exams.is_error():
        if exams.get_wilma_error() is not None:
            print(exams.get_wilma_error()['message'])
            print("--> " + exams.get_wilma_error()['description'])
        else:
            print(exams.get_exception())
    else:
        print("Got exams")
        unseenExams = []
        for uExam in exams.exams:
            if uExam['unseen']:
                unseenExams.append(uExam)
        for i, exam in enumerate(unseenExams):
            name = "unknown"
            if exam['name'] is not None:
                name = exam['name']
            print(" " + str(i) + " --> " + name)

        num = input("Enter number: \n")
        numInt = int(num)
        if numInt not in range(0, len(unseenExams)):
            print("Invalid number!")
            exit(-1)
        else:
            exam = unseenExams[numInt]
            print("Proceeding to mark exam as seen")
            result = sdk.markExamSeen([exam])
            if result.is_error():
                print(str(result.get_exception()))
                if result.get_wilma_error() is not None:
                    print(result.get_wilma_error())
            else:
                print("Done, double-checking...")
                examsResult = sdk.getExams()
                if examsResult.is_error():
                    print(str(examsResult.get_exception()))
                    if examsResult.get_wilma_error() is not None:
                        print(examsResult.get_wilma_error())
                else:
                    for newExam in examsResult.exams:
                        if newExam['id'] == exam['id'] and newExam['examId'] == exam['examId']:
                            print("Found the exam in list")
                            if not newExam['unseen']:
                                print("Success!")
                                exit(0)
                    print("Failed! Exam was shown as unseen in the list")
