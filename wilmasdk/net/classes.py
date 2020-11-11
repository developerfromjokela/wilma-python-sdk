#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela
import six


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
        if isinstance(exception, six.string_types):
            exception = Exception(exception)
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


class LogoutResult(RequestResult):

    def __init__(self):
        super().__init__(False, None, None)


class HomepageResult(RequestResult):

    def __init__(self, homepage, roleSelectionRequired):
        super().__init__(False, None, None)
        self.homepage = homepage
        self.roleSelectionRequired = roleSelectionRequired


class LessonNotesResult(RequestResult):

    def __init__(self, lesson_notes, exuses_allowed):
        super().__init__(False, None, None)
        self.lesson_notes = lesson_notes
        self.excuses_allowed = exuses_allowed


class AuthSessionResult(RequestResult):

    def __init__(self, auth_session_d):
        super().__init__(False, None, None)
        self.authSessionId = auth_session_d

    def get_auth_session(self):
        return self.authSessionId


class SessionValidateResult(RequestResult):

    def __init__(self, validation, user_id, user_type):
        super().__init__(False, None, None)
        self.validation = validation
        self.user_id = user_id
        self.user_type = user_type

    def is_valid_session(self):
        return self.validation
