#  Copyright (c) 2020-2022 Developer From Jokela.
#  @author developerfromjokela
import datetime

from wilmasdk.client.client import WilmaAPIClient
from wilmasdk.net.classes import ErrorResult
from wilmasdk.parser.validator.exams import validateExam
from wilmasdk.parser.validator.excuses import validateExcuse
from wilmasdk.parser.validator.roles import validateRole


class WilmaSDK:

    def __init__(self) -> None:
        super().__init__()
        self.apiClient = WilmaAPIClient(None, None)
        self.role = None
        self.roleRequired = False

    def check_required_params(self, session_required=True):
        if session_required and self.apiClient.wilmasesson is None:
            return ErrorResult('Not logged in!')
        elif self.role is None and self.roleRequired:
            return ErrorResult('Role is required!')
        if self.apiClient.wilmaserver is None:
            return ErrorResult('Set wilma server URL first!')

    def get_wilma_servers(self):
        self.check_required_params(False)
        return self.apiClient.getWilmaServers()

    def set_wilma_server(self, url):
        self.apiClient.changeWilmaAddress(url)

    def set_role(self, role):
        if not validateRole(role):
            raise Exception("Role is not valid!")
        self.apiClient.setRole(role)

    def get_homepage(self):
        self.check_required_params(True)
        return self.apiClient.getHomepage()

    def get_lesson_notes(self):
        self.check_required_params(True)
        return self.apiClient.getLessonNotes()

    def get_exams(self):
        self.check_required_params(True)
        return self.apiClient.getExams()

    def get_courses(self):
        self.check_required_params(True)
        return self.apiClient.getGroups()

    def get_messages(self):
        self.check_required_params(True)
        return self.apiClient.getMessages()

    def get_message(self, message_id: int):
        self.check_required_params(True)
        return self.apiClient.getMessage(message_id)

    def delete_message(self, message_id: int):
        self.check_required_params(True)
        return self.apiClient.deleteMessage(message_id)

    def reply_to_message(self, message_id: int, content: str):
        self.check_required_params(True)
        return self.apiClient.replyToMessage(message_id, content)

    def archive_message(self, message_id: int):
        self.check_required_params(True)
        return self.apiClient.archiveMessage(message_id)

    def unarchive_message(self, message_id: int):
        self.check_required_params(True)
        return self.apiClient.unArchiveMessage(message_id)

    def get_course(self, group_id: int):
        self.check_required_params(True)
        return self.apiClient.getGroup(group_id)

    def get_announcements(self):
        self.check_required_params(True)
        return self.apiClient.getAnnouncements()

    def get_schedule(self, date: datetime.datetime = None):
        self.check_required_params(True)
        return self.apiClient.get_schedule(date)

    def get_announcement(self, announcement_id: int):
        self.check_required_params(True)
        return self.apiClient.getAnnouncement(announcement_id)

    def get_excuse_reasons(self):
        self.check_required_params(True)
        return self.apiClient.getExcuseReasons()

    def get_absence_reasons(self):
        self.check_required_params(True)
        return self.apiClient.getAbsenceReasons()

    def mark_clearance(self, excuse, lesson_note_id, reason=None):
        self.check_required_params(True)
        if not validateExcuse(excuse):
            return ErrorResult("Excuse is not valid!")
        return self.apiClient.markClearance(excuse, lesson_note_id, reason)

    def mark_exam_seen(self, exams):
        self.check_required_params(True)
        for exam in exams:
            if not validateExam(exam):
                return ErrorResult("One of exams is not valid!")
        return self.apiClient.markExamAsSeen(exams)

    def mark_absence(self, absence: dict, report_date: int, reason: str = None):
        self.check_required_params(True)
        # Validating excuse, because its type is identical to absence's one
        if not validateExcuse(absence):
            return ErrorResult("Absence is not valid!")
        return self.apiClient.markAbsence(absence, report_date, reason)

    def login(self, username, password, apikey):
        self.check_required_params(False)
        sessionRequest = self.apiClient.getSession()
        if sessionRequest.is_error():
            return sessionRequest
        else:
            sessionID = sessionRequest.get_auth_session()
            loginResult = self.apiClient.login(username, password, sessionID, apikey)
            if not loginResult.is_error():
                self.apiClient.setSession(loginResult.session)
                self.roleRequired = loginResult.roleSelectionRequired
            return loginResult

    def logout(self):
        self.check_required_params(True)
        return self.apiClient.logout()

    def login_using_session_id(self, session_id, mfa_token=None):
        self.apiClient.setSession(session_id, mfa_token)
        return self.apiClient.getHomepage()
