#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

class RequestResult:

    def __init__(self, error, exception=None, response=None):
        self.error = error
        self.exception = exception
        self.response = response
        if error and exception is None:
            raise Exception("Exception cannot be None when error is True")

    def get_exception(self):
        return self.exception

    def is_error(self):
        return self.error

    def get_response(self):
        return self.response


class ErrorResult(RequestResult):

    def __init__(self, exception, wilma_error=None):
        super().__init__(True, exception)
        self.wilma_error = wilma_error

    def get_wilma_error(self):
        return self.wilma_error


class WilmaServersResult(RequestResult):

    def __init__(self, servers):
        super().__init__(False, None, None)
        self.servers = servers

    def get_wilma_servers(self):
        return self.servers

class LoginResult(RequestResult):

    def __init__(self, session, roleSelectionRequired, homepage):
        super().__init__(False, None, None)
        self.session = session
        self.roleSelectionRequired = roleSelectionRequired
        self.homepage = homepage

    def get_wilma_servers(self):
        return self.servers


class AuthSessionResult(RequestResult):

    def __init__(self, auth_session_d):
        super().__init__(False, None, None)
        self.authSessionId = auth_session_d

    def get_auth_session(self):
        return self.authSessionId


class LoginResult(RequestResult):

    def __init__(self, session):
        super().__init__(False, None, None)
        self.session = session

    def get_session(self):
        return self.session


class SessionValidateResult(RequestResult):

    def __init__(self, validation, user_id, user_type):
        super().__init__(False, None, None)
        self.validation = validation
        self.user_id = user_id
        self.user_type = user_type

    def is_valid_session(self):
        return self.validation
