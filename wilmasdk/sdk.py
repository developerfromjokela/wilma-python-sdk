#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela
from .client.client import WilmaAPIClient


class WilmaSDK:

    def __init__(self) -> None:
        super().__init__()
        self.apiClient = WilmaAPIClient(None, None)

    def getWilmaServers(self):
        return self.apiClient.getWilmaServers()

    def setWilmaServer(self, url):
        self.apiClient.changeWilmaAddress(url)

    def login(self, username, password, apikey):
        ...