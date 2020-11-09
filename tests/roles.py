#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

import sys
from authdetails import WILMA_SETTINGS
sys.path.append("..")

from wilmasdk.sdk import WilmaSDK

sdk = WilmaSDK()


# Login Test

sdk.setWilmaServer(WILMA_SETTINGS['server'])
print("Trying to Log in")

result = sdk.login(WILMA_SETTINGS['username'], WILMA_SETTINGS['password'], WILMA_SETTINGS['apikey'])

if result.is_error():
    if result.get_wilma_error() is not None:
        print(result.get_wilma_error()['message'])
        print("--> "+result.get_wilma_error()['description'])
    else:
        print(result.get_exception())
else:
    print("Complete!")
    print("Roles required: "+str(result.roleSelectionRequired))