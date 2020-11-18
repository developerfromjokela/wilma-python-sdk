#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

from wilmasdk.client.client import WilmaAPIClient
from wilmasdk.net.classes import ErrorResult
from wilmasdk.parser.validator.roles import validateRole
from wilmasdk.parser.validator.excuses import validateExcuse
from wilmasdk.parser.validator.exams import validateExam


class WilmaSDK:

    def __init__(self) -> None:
        super().__init__()
        self.apiClient = WilmaAPIClient(None, None)
        self.role = None
        self.roleRequired = False

    def checkRequiredParams(self, session_required=True):
        if session_required and self.apiClient.wilmasesson is None:
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

    def setRole(self, role):
        if not validateRole(role):
            raise Exception("Role is not valid!")
        self.apiClient.setRole(role)

    def getHomepage(self):
        self.checkRequiredParams(True)
        return self.apiClient.getHomepage()

    def getLessonNotes(self):
        self.checkRequiredParams(True)
        return self.apiClient.getLessonNotes()

    def getExams(self):
        self.checkRequiredParams(True)
        return self.apiClient.getExams()

    def getGroups(self):
        self.checkRequiredParams(True)
        return self.apiClient.getGroups()

    def getMessages(self):
        self.checkRequiredParams(True)
        return self.apiClient.getMessages()

    def getGroup(self, group_id: int):
        self.checkRequiredParams(True)
        return self.apiClient.getGroup(group_id)

    def getAnnouncements(self):
        self.checkRequiredParams(True)
        return self.apiClient.getAnnouncements()

    def getAnnouncement(self, announcement_id: int):
        self.checkRequiredParams(True)
        return self.apiClient.getAnnouncement(announcement_id)

    def getExcuseReasons(self):
        self.checkRequiredParams(True)
        return self.apiClient.getExcuseReasons()

    def getAbsenceReasons(self):
        self.checkRequiredParams(True)
        return self.apiClient.getAbsenceReasons()

    def markClearance(self, excuse, lesson_note_id, reason=None):
        self.checkRequiredParams(True)
        if not validateExcuse(excuse):
            return ErrorResult("Excuse is not valid!")
        return self.apiClient.markClearance(excuse, lesson_note_id, reason)

    def markExamSeen(self, exams):
        self.checkRequiredParams(True)
        for exam in exams:
            if not validateExam(exam):
                return ErrorResult("One of exams is not valid!")
        return self.apiClient.markExamAsSeen(exams)

    def markAbsence(self, absence: dict, report_date: int, reason: str = None):
        self.checkRequiredParams(True)
        # Validating excuse, because its type is identical to absence's one
        if not validateExcuse(absence):
            return ErrorResult("Absence is not valid!")
        return self.apiClient.markAbsence(absence, report_date, reason)

    def login(self, username, password, apikey):
        self.checkRequiredParams(False)
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
        self.checkRequiredParams(True)
        return self.apiClient.logout()

    def loginUsingSessionId(self, session_id):
        self.apiClient.setSession(session_id)
        return self.apiClient.getHomepage()
