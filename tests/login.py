#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

import sys
sys.path.append("..")

from wilmasdk.sdk import WilmaSDK

sdk = WilmaSDK()


# Login Test

sdk.setWilmaServer("https://test.inschool.fi")
print("Trying to Log in")

result = sdk.login("example", "example", "example")

if result.is_error():
    if result.get_wilma_error() is not None:
        print(result.get_wilma_error()['message'])
        print("--> "+result.get_wilma_error()['description'])
    else:
        print(result.get_exception())
else:
    print("Complete!")