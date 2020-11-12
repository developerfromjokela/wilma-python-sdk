#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

from authdetails import WILMA_SETTINGS
from wilmasdk.sdk import WilmaSDK
import json

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

    num = input("Enter Group ID: \n")
    numInt = int(num)
    group = sdk.getGroup(numInt)
    if group.is_error():
        if group.get_wilma_error() is not None:
            print(group.get_wilma_error()['message'])
            print("--> " + group.get_wilma_error()['description'])
        else:
            print(group.get_exception())
    else:
        print(json.dumps(group.group, indent=4, sort_keys=True, default=str))


