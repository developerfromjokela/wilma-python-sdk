#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

import wilmasdk.net.httpclient as httpclient
from ..net.classes import *
from ..net.conf import CONFIG


def checkForWilmaError(response):
    if response.status_code != 200:
        jsonResponse = json.loads(response.text)
        errorBody = jsonResponse.get('error', None)
        if errorBody is not None:
            return ErrorResult(Exception(errorBody['message']), errorBody)
        else:
            return ErrorResult(Exception("Unable to parse error code: " + str(response.status_code)))
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

    def getSession(self):
        try:
            result = self.httpclient.get_request('index_json')
            error_check = checkForWilmaError(requestResult.get_response())
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
