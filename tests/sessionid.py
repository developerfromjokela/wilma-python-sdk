#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

import sys
sys.path.append("..")

from wilmasdk.sdk import WilmaSDK
from authdetails import WILMA_SETTINGS

sdk = WilmaSDK()

# Testing random domain

sdk.setWilmaServer("https://example.com")
print("Checking fake")
from .authdetails import WILMA_SETTINGS

result = sdk.login("example", "example", "example")

if result.is_error():
    print(result.get_exception())
else:
    print("Pass RANDOM")

# Testing real Wilma server, expect different error

sdk.setWilmaServer(WILMA_SETTINGS['server'])
print("Checking real")
result = sdk.login(WILMA_SETTINGS['username'], WILMA_SETTINGS['password'], WILMA_SETTINGS['apikey'])

if result.is_error():
    if result.get_wilma_error() is not None:
        print(result.get_wilma_error())
    print(result.get_exception())
else:
    print("Pass REAL")