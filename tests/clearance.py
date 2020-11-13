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

    print("Fetching lesson notes")
    lessonNotes = sdk.getLessonNotes()
    if lessonNotes.is_error():
        if lessonNotes.get_wilma_error() is not None:
            print(lessonNotes.get_wilma_error()['message'])
            print("--> " + lessonNotes.get_wilma_error()['description'])
        else:
            print(lessonNotes.get_exception())
    else:
        if not lessonNotes.excuses_allowed:
            print("You're not allowed to mark clearances!")
            exit(-1)
        for item in lessonNotes.lesson_notes:
            if item['requiresClearance']:
                print(" " + str(item['id']) + " --> " + item['type']['name'] + ", " + item['course']['name'] + ", " +
                      item['teacher']['name'])

    num = input("Enter ID of lesson note you want to mark clearance on: \n (If list is empty, it means you don't have "
                "any lesson notes to mark clearance on)\n")
    lessonId = int(num)

    excuseReasons = sdk.getExcuseReasons()
    if excuseReasons.is_error():
        if excuseReasons.get_wilma_error() is not None:
            print(excuseReasons.get_wilma_error()['message'])
            print("--> " + excuseReasons.get_wilma_error()['description'])
        else:
            print(excuseReasons.get_exception())
    else:
        print("Got excuse reasons")
        idValues = []
        for reason in excuseReasons.reasons:
            idValues.append(reason['id'])
            print(" " + str(reason['id']) + " --> " + reason['caption'])
        num = input("Enter number: \n")
        numInt = int(num)
        itemExists = any(item['id'] == numInt for item in excuseReasons.reasons)
        if itemExists is False:
            print("Invalid number!")
            exit(-1)
        else:
            itemPos = (item['id'] == numInt for item in excuseReasons.reasons)
            item = None
            for i, res in enumerate(list(itemPos)):
                if res is True:
                    item = excuseReasons.reasons[i]
            if item is None:
                print("Item not found")
            else:
                print("Marking clearance")
                text = None
                if ('requireText' in item and item['requireText'] is True) or ('explanationAllowed' in item and item['explanationAllowed'] is True):
                    text = input("This type requires you to type reason: \n")
                    if len(text) < 1:
                        print("Text is too short!")
                        exit(-1)
                    print("Continuing marking clearance")
                result = sdk.markClearance(item, lessonId, text)
                if result.is_error():
                    if result.get_wilma_error() is not None:
                        print(result.get_wilma_error()['message'])
                        print("--> " + result.get_wilma_error()['description'])
                    else:
                        print(excuseReasons.get_exception())
                else:
                    print("Success!")
