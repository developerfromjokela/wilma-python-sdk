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
        passwdFormKey = result.homepage['FormKey']
        for pos, role in enumerate(result.homepage['Roles']):
            if role['FormKey'] != passwdFormKey:
                print(" " + str(pos) + " --> " + role['Name'])
        num = input("Enter number: \n")
        numInt = int(num)
        if numInt not in range(1, len(result.homepage['Roles'])):
            print("Invalid number!")
            exit(-1)
        else:
            role = result.homepage['Roles'][numInt]
            print("Selected role: " + role['Name'])
            sdk.setRole(role)
            print("Trying to fetch role's homepage")
            homepageResult = sdk.getHomepage()
            if homepageResult.is_error():
                print(str(homepageResult.get_exception()))
                if homepageResult.get_wilma_error() is not None:
                    print(homepageResult.get_wilma_error())
            else:
                homepage = homepageResult.homepage
                if homepage['FormKey'] == role['FormKey']:
                    print("Successfully switched to " + homepage['Name'] + " role")
                    print("Primus ID: " + str(homepage['PrimusId']))
                    print("Type: " + str(homepage['Type']))
    else:
        print("Roles not required, not selecting")
