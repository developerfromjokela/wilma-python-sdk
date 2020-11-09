#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

import wilmasdk.net.httpclient as httpclient
from ..net.classes import *
from ..net.conf import CONFIG
import json
from ..gen import apikey as keygen


def checkForWilmaError(response):
    if response.status_code != 200:
        try:
            jsonResponse = json.loads(response.text)
            errorBody = jsonResponse.get('error', None)
            if errorBody is not None:
                return ErrorResult(Exception(errorBody['message']), errorBody)
            else:
                return ErrorResult(Exception("Unable to parse error code: " + str(response.status_code)))
        except Exception as e:
            return ErrorResult('Unable to parse response, are you sure this is Wilma server?')
    else:
        return None


class WilmaAPIClient:

    def __init__(self, wilmaserver, wilmasession) -> None:
        super().__init__()
        self.wilmaserver = wilmaserver
        self.wilmasesson = wilmasession
        self.httpclient = httpclient.WilmaHttpClient(wilmasession, wilmaserver)

    def changeWilmaAddress(self, server):
        self.httpclient.set_wilma_url(server)
        self.wilmaserver = self.httpclient.baseUrl

    def setRole(self, role):
        slug = role['Slug']
        if self.wilmaserver is not None and self.wilmaserver[len(self.wilmaserver)-1] is "/":
            slug = slug[1:]
        self.changeWilmaAddress(self.wilmaserver+slug)

    def getSession(self):
        try:
            result = self.httpclient.get_request('index_json')
            error_check = checkForWilmaError(result.get_response())
            if error_check is not None:
                return error_check
            if not result.is_error():
                response = result.get_response().json()
                if 'SessionID' in response and "ApiVersion" in response:
                    if response['ApiVersion'] < CONFIG['minimumapiversion']:
                        return ErrorResult('Wilma server is too old to work with this library. Api Version 10 and '
                                           'newer is supported')
                    return AuthSessionResult(response['SessionID'])
                else:
                    return ErrorResult('Unable to get login information, are you sure this is Wilma server?')
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getHomepage(self):
        try:
            result = self.httpclient.get_request('index_json')
            error_check = checkForWilmaError(result.get_response())
            if error_check is not None:
                return error_check
            if not result.is_error():
                response = result.get_response().json()
                if "LoginResult" in response:
                    if response['LoginResult'] != "Ok":
                        return ErrorResult("Not logged in!")
                    else:
                        return HomepageResult(response, (len(response.get('Roles', [])) > 0))

                else:
                    return ErrorResult("Homepage couldn't be parsed")
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getWilmaServers(self):
        try:
            result = self.httpclient.get_request_external(CONFIG['wilmaservers_url'])
            if not result.is_error():
                response = result.get_response().json()
                return WilmaServersResult(response['wilmat'])
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def login(self, username, password, session_id, apikey):
        try:
            apikey = keygen.generate_apikey(username=username, session_id=session_id, apikey=apikey)
            data = {
                'Login': username,
                'Password': password,
                'CompleteJson': '',
                'SessionId': session_id,
                'ApiKey': apikey,
                'format': 'json'
            }
            result = self.httpclient.loginId_post_request('login', data, session_id)
            error_check = checkForWilmaError(result.get_response())
            if error_check is not None:
                return error_check
            if not result.is_error():
                response = result.get_response().json()
                cookies = result.get_response().cookies.get_dict()
                if 'Wilma2SID' not in cookies:
                    return ErrorResult("Session not found")
                if "LoginResult" in response and response['LoginResult'] == "Ok":
                    return LoginResult(cookies['Wilma2SID'], (len(response.get('Roles', [])) > 0), response)
                else:
                    return ErrorResult("Login failed, check username and password")
            else:
                return result
        except Exception as e:
            return ErrorResult(e)
