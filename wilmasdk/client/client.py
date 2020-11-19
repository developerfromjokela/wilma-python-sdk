#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela


import wilmasdk.net.httpclient as httpclient
from wilmasdk.net.classes import *
from wilmasdk.net.conf import CONFIG
import json
from wilmasdk.gen import apikey as keygen
from wilmasdk.parser.optimizer import optimizeHomepage, optimize_dict_array, optimize_dict
from wilmasdk.exception.exceptions import *
import wilmasdk.parser.lessonotes
import wilmasdk.parser.exams
import wilmasdk.parser.groups
import wilmasdk.parser.news
from wilmasdk.parser.lessonotes import optimizeAbsenceInfo

reLoginErrors = ['common-20', 'common-18', 'common-15', 'common-34']


def checkForWilmaError(response):
    if response.status_code != 200:
        try:
            jsonResponse = json.loads(response.text)
            errorBody = jsonResponse.get('error', None)
            if errorBody is not None:
                if errorBody['id'] in reLoginErrors:
                    return ErrorResult(TokenExpiredException(), errorBody)
                return ErrorResult(Exception(errorBody['message']), errorBody)
            else:
                return ErrorResult(Exception("Unable to parse error code: " + str(response.status_code)))
        except:
            return ErrorResult('Unable to parse response, are you sure this is Wilma server?')
    else:
        return None


class WilmaAPIClient:

    def __init__(self, wilmaserver, wilmasession) -> None:
        super().__init__()
        self.wilmaserver = wilmaserver
        self.wilmasesson = wilmasession
        self.httpclient = httpclient.WilmaHttpClient(wilmasession, wilmaserver)

    """
    If server URL needs an change, this is for that
    """

    def changeWilmaAddress(self, server: str):
        self.httpclient.set_wilma_url(server)
        self.wilmaserver = self.httpclient.baseUrl

    """
    Sets Session ID cookie
    """

    def setSession(self, session_id):
        self.httpclient.user_auth = session_id
        self.wilmasesson = session_id

    """
    Saves role selection if required
    """

    def setRole(self, role: dict):
        slug = role['slug']
        if self.wilmaserver is not None and self.wilmaserver[len(self.wilmaserver) - 1] is "/":
            slug = slug[1:]
        self.changeWilmaAddress(self.wilmaserver + slug)

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
                        return ErrorResult('Wilma server is too old to work with this library. Api Version ' + str(
                            CONFIG['minimumapiversion']) + ' and '
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
            result = self.httpclient.authenticated_get_request('index_json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                if "LoginResult" in response:
                    if response['LoginResult'] != "Ok":
                        return ErrorResult("Not logged in!")
                    else:
                        return HomepageResult(optimizeHomepage(response), (len(response.get('Roles', [])) > 0))

                else:
                    return ErrorResult("Homepage couldn't be parsed")
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getExcuseReasons(self):
        try:
            result = self.httpclient.authenticated_get_request('attendance?format=json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                # When excuses are missing, it means that you don't have any lesson note to do clearance on
                if "Excuses" in response:
                    excuses = optimize_dict_array(response['Excuses'])
                    return ExcuseReasonsResult(excuses)
                else:
                    return ErrorResult(NoExcuseInformationException())
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getFormKey(self):
        result = self.getHomepage()
        if result.is_error():
            return result
        else:
            if 'formKey' in result.homepage:
                return FormKeyResult(result.homepage['formKey'])
            else:
                return ErrorResult("Unable to obtain formKey")

    """
    Marks clearance on lesson note, or as visma calls this operation: saving an excuse
    """

    def markClearance(self, excuse: dict, lesson_note_id: int, explanation: str = None):
        try:
            formKeyResult = self.getFormKey()
            if formKeyResult.is_error():
                return formKeyResult
            data = {
                'item' + str(lesson_note_id): 'true',
                'type': str(excuse['id']),
                'formkey': formKeyResult.form_key,
                'format': 'json'
            }
            if excuse['explanationAllowed'] is True or ('requireText' in excuse and excuse['requireText'] is True):
                if explanation is not None:
                    data['text'] = explanation
                else:
                    return ErrorResult("Explanation missing, even though it's required")
            result = self.httpclient.authenticated_post_request('attendance/saveexcuse', data, False)
            if not result.is_error():
                if result.get_response().status_code == 303:
                    return ClearanceMarkResult()
                else:
                    error_check = checkForWilmaError(result.get_response())
                    if error_check is not None:
                        return error_check
                    else:
                        return ErrorResult("Something went wrong, unable to find errors")
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    """
    Marks absence for student
    """

    def markAbsence(self, excuse: dict, report_date: int, explanation: str = None):
        try:
            formKeyResult = self.getFormKey()
            if formKeyResult.is_error():
                return formKeyResult
            data = {
                'ReportDate': str(report_date),
                'type': str(excuse['id']),
                'formkey': formKeyResult.form_key,
                'format': 'json'
            }
            if excuse['explanationAllowed'] is True or ('requireText' in excuse and excuse['requireText'] is True):
                if explanation is not None:
                    data['text'] = explanation
                else:
                    return ErrorResult("Explanation missing, even though it's required")
            result = self.httpclient.authenticated_post_request('attendance/savereport', data, False)
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                return AbsenceMarkResult()
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getAbsenceReasons(self):
        try:
            result = self.httpclient.authenticated_get_request('attendance/report?format=json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                return ExcuseReasonsResult(optimize_dict(optimizeAbsenceInfo(response)))
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getLessonNotes(self):
        try:
            result = self.httpclient.authenticated_get_request('attendance/index_json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                obs = []
                allowSaveExcuse = ("AllowSaveExcuse" in response)
                if allowSaveExcuse:
                    allowSaveExcuse = response['AllowSaveExcuse']
                if "Observations" in response:
                    obs = wilmasdk.parser.lessonotes.optimizeLessonNotes(response['Observations'])
                return LessonNotesResult(obs, allowSaveExcuse)
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    """
    Marks exam(s) as seen, multiple exams could be included in one request
    """

    def markExamAsSeen(self, exams):
        try:
            formKeyResult = self.getFormKey()
            if formKeyResult.is_error():
                return formKeyResult
            data = [('formkey', formKeyResult.form_key), ('format', 'json')]
            for exam in exams:
                data.append(('mid', str(exam['id']) + "-" + str(exam['examId'])))
            result = self.httpclient.authenticated_post_request('exams/seen', data)
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                # yes, this request has different Error format, Vismaaa!
                response = result.get_response().json()
                if 'Success' in response and 'Message' in response:
                    if response['Success'] is True:
                        return ExamSeenResult()
                    else:
                        return ErrorResult(response['Message'])
                else:
                    return ErrorResult("Unknown response, unable to handle: " + result.get_response().text)
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getExams(self):
        try:
            result = self.httpclient.authenticated_get_request('exams/index_json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                exams = []
                if "Exams" in response:
                    exams = wilmasdk.parser.exams.optimizeExams(response['Exams'])
                return ExamsResult(exams)
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getMessages(self):
        try:
            result = self.httpclient.authenticated_get_request('messages/index_json/all')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                messages = []
                if "Messages" in response:
                    messages = wilmasdk.parser.optimizer.optimizeMessages(response['Messages'])
                return MessagesResult(messages)
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getMessage(self, message_id: int):
        try:
            result = self.httpclient.authenticated_get_request('messages/index_json/' + str(message_id))
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                if "messages" in response and len(response['messages']) > 0:
                    message = wilmasdk.parser.optimizer.optimizeMessage(response['messages'][0])
                    return MessageResult(message)
                else:
                    return ErrorResult("Message not found")
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getGroups(self):
        try:
            result = self.httpclient.authenticated_get_request('groups/index_json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                groups = []
                if "Groups" in response:
                    groups = wilmasdk.parser.groups.optimizeGroups(response['Groups'])
                return GroupsResult(groups)
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getAnnouncements(self):
        try:
            result = self.httpclient.authenticated_get_request('news/index_json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                news = []
                if "News" in response:
                    news = wilmasdk.parser.news.optimizeNews(response['News'])
                return AnnouncementsResult(news)
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getAnnouncement(self, announcement_id: int):
        try:
            result = self.httpclient.authenticated_get_request('news/index_json/' + str(announcement_id))
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                if "News" in response and len(response['News']) > 0:
                    announcement = wilmasdk.parser.news.optimizeNew(response['News'][0])
                    return AnnouncementResult(announcement)
                else:
                    return ErrorResult("Announcement not found")
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getGroup(self, group_id: int):
        try:
            result = self.httpclient.authenticated_get_request('groups/index_json/' + str(group_id))
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                if "Groups" in response and len(response['Groups']) > 0:
                    group = wilmasdk.parser.groups.optimizeGroup(response['Groups'][0])
                    return GroupResult(group)
                else:
                    return ErrorResult("Group not found")
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def logout(self):
        try:
            result = self.httpclient.authenticated_post_request('logout', {'format': 'json'})
            if not result.is_error():
                response = result.get_response().json()
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                if "LoginResult" in response:
                    if response['LoginResult'] == "Failed":
                        self.setSession(None)
                        return LogoutResult()
                    else:
                        self.setSession(None)
                        return LogoutResult()
                else:
                    return ErrorResult("Logout failed, error object not found")
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def archiveMessage(self, message_id: int):
        try:
            formKeyResult = self.getFormKey()
            if formKeyResult.is_error():
                return formKeyResult
            result = self.httpclient.authenticated_post_request('messages/archivetool',
                                                                {'formkey': formKeyResult.form_key,
                                                                 'mid': str(message_id), 'format': 'json'})
            if not result.is_error():
                if result.get_response().status_code == 302:
                    return MessageArchiveResult()
                else:
                    error_check = checkForWilmaError(result.get_response())
                    if error_check is not None:
                        return error_check
                    else:
                        return ErrorResult("Archive result parsing failed")
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def unArchiveMessage(self, message_id: int):
        try:
            formKeyResult = self.getFormKey()
            if formKeyResult.is_error():
                return formKeyResult
            result = self.httpclient.authenticated_post_request('messages/restorearchived',
                                                                {'formkey': formKeyResult.form_key,
                                                                 'mid': str(message_id), 'format': 'json'})
            if not result.is_error():
                if result.get_response().status_code == 302:
                    return MessageUnArchiveResult()
                else:
                    error_check = checkForWilmaError(result.get_response())
                    if error_check is not None:
                        return error_check
                    else:
                        return ErrorResult("Archive result parsing failed")
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def deleteMessage(self, message_id: int):
        try:
            formKeyResult = self.getFormKey()
            if formKeyResult.is_error():
                return formKeyResult
            result = self.httpclient.authenticated_post_request('messages/delete',
                                                                {'formkey': formKeyResult.form_key,
                                                                 'mid': str(message_id), 'format': 'json'})
            if not result.is_error():
                if result.get_response().status_code == 302:
                    return MessageDeleteResult()
                else:
                    error_check = checkForWilmaError(result.get_response())
                    if error_check is not None:
                        return error_check
                    else:
                        return ErrorResult("Archive result parsing failed")
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

    def login(self, username: str, password: str, session_id: str, apikey: str):
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
                if "LoginResult" in response and response['LoginResult'] == "Ok":
                    if 'Wilma2SID' not in cookies:
                        return ErrorResult("Session not found")
                    return LoginResult(cookies['Wilma2SID'], (len(response.get('Roles', [])) > 0),
                                       optimizeHomepage(response))
                else:
                    return ErrorResult("Login failed, check username and password")
            else:
                return result
        except Exception as e:
            return ErrorResult(e)
