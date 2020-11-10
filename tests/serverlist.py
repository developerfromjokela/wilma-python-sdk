#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

from wilmasdk.sdk import WilmaSDK

sdk = WilmaSDK()
servers = sdk.getWilmaServers()

if servers.is_error():
    print(servers.get_exception())
    exit(-1)
else:
    print(servers.get_wilma_servers())
    exit(0)