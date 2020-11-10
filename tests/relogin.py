#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

from wilmasdk.sdk import WilmaSDK

sdk = WilmaSDK()

from authdetails import WILMA_SETTINGS
import wilmasdk.exception
import traceback

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
    sid = result.session
    print("SID: "+result.session)
    print("Complete! Now logging out")
    logoutResult = sdk.logout()
    if logoutResult.is_error():
        if logoutResult.get_wilma_error() is not None:
            print(logoutResult.get_wilma_error()['message'])
            print("--> " + logoutResult.get_wilma_error()['description'])
        else:
            print(logoutResult.get_exception())
    else:
        print("Now trying to set old session ID and get homepage")
        result = sdk.loginUsingSessionId(session_id=sid)
        if result.is_error():
            print("Error, it seems to work. Checking if it's correct")
            if type(result.get_exception()) == wilmasdk.exception.exceptions.TokenExpiredException:
                print("It worked!")
            else:
                print("Got other exception:")
                print(type(result.get_exception()))
                print(result.get_exception())
            traceback.print_tb(result.get_exception().__traceback__)
        else:
            print("Session is still active, something went wrong")
