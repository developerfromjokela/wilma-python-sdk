#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

import sys
from authdetails import WILMA_SETTINGS

from wilmasdk.sdk import WilmaSDK

sdk = WilmaSDK()

# Login Test

sdk.setWilmaServer(WILMA_SETTINGS['server'])
print("Trying to Log in using token: " + sys.argv[1])

result = sdk.loginUsingSessionId(sys.argv[1])

if result.is_error():
    if result.get_wilma_error() is not None:
        print(result.get_wilma_error()['message'])
        print("--> " + result.get_wilma_error()['description'])
    else:
        print(result.get_exception())
else:
    print("Complete!")
    if not result.is_error():
        print(result.homepage)
