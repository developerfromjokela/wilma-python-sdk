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

    def __init__(self, session, role_selection_required, homepage):
        super().__init__(False, None, None)
        self.session = session
        self.roleSelectionRequired = role_selection_required
        self.homepage = homepage


class LogoutResult(RequestResult):

    def __init__(self):
        super().__init__(False, None, None)


class FormKeyResult(RequestResult):

    def __init__(self, form_key):
        super().__init__(False, None, None)
        self.form_key = form_key


class HomepageResult(RequestResult):

    def __init__(self, homepage, role_selection_required):
        super().__init__(False, None, None)
        self.homepage = homepage
        self.roleSelectionRequired = role_selection_required


class LessonNotesResult(RequestResult):

    def __init__(self, lesson_notes, exuses_allowed):
        super().__init__(False, None, None)
        self.lesson_notes = lesson_notes
        self.excuses_allowed = exuses_allowed


class ExamsResult(RequestResult):

    def __init__(self, exams):
        super().__init__(False, None, None)
        self.exams = exams


class MessagesResult(RequestResult):

    def __init__(self, messages):
        super().__init__(False, None, None)
        self.messages = messages


class MessageResult(RequestResult):

    def __init__(self, message):
        super().__init__(False, None, None)
        self.message = message


class MessageArchiveResult(RequestResult):

    def __init__(self):
        super().__init__(False, None, None)


class MessageUnArchiveResult(RequestResult):

    def __init__(self):
        super().__init__(False, None, None)


class MessageDeleteResult(RequestResult):

    def __init__(self):
        super().__init__(False, None, None)


class ExamSeenResult(RequestResult):

    def __init__(self):
        super().__init__(False, None, None)


class GroupsResult(RequestResult):

    def __init__(self, groups):
        super().__init__(False, None, None)
        self.groups = groups


class AnnouncementsResult(RequestResult):

    def __init__(self, news):
        super().__init__(False, None, None)
        self.announcements = news


class ScheduleResult(RequestResult):

    def __init__(self, schedule):
        super().__init__(False, None, None)
        self.schedule = schedule


class GroupResult(RequestResult):

    def __init__(self, group):
        super().__init__(False, None, None)
        self.group = group


class AnnouncementResult(RequestResult):

    def __init__(self, announcement):
        super().__init__(False, None, None)
        self.announcement = announcement


class ExcuseReasonsResult(RequestResult):

    def __init__(self, reasons):
        super().__init__(False, None, None)
        self.reasons = reasons


class AbsenceReasonsResult(RequestResult):

    def __init__(self, reasons):
        super().__init__(False, None, None)
        self.reasons = reasons


class ClearanceMarkResult(RequestResult):

    def __init__(self):
        super().__init__(False, None, None)


class AbsenceMarkResult(RequestResult):

    def __init__(self):
        super().__init__(False, None, None)


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
