#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela
from .client.client import WilmaAPIClient
from .net.classes import ErrorResult


class WilmaSDK:

    def __init__(self) -> None:
        super().__init__()
        self.apiClient = WilmaAPIClient(None, None)
        self.role = None
        self.roleRequired = False

    def checkRequiredParams(self, sessionRequired=True):
        if sessionRequired and self.apiClient.wilmasesson is None:
            return ErrorResult('Not logged in!')
        elif self.role is None and self.roleRequired:
            return ErrorResult('Role is required!')
        if self.apiClient.wilmaserver is None:
            return ErrorResult('Set wilma server URL first!')

    def getWilmaServers(self):
        self.checkRequiredParams(False)
        return self.apiClient.getWilmaServers()

    def setWilmaServer(self, url):
        self.apiClient.changeWilmaAddress(url)

    def login(self, username, password, apikey):
        self.checkRequiredParams(False)
        sessionRequest = self.apiClient.getSession()
        if sessionRequest.is_error():
            return sessionRequest
        else:
            sessionID = sessionRequest.get_auth_session()
            loginResult = self.apiClient.login(username, password, sessionID, apikey)
            if not loginResult.is_error():
                self.roleRequired = loginResult.roleSelectionRequired

