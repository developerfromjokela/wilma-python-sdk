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
import wilmasdk.parser.schedule
from wilmasdk.parser.lessonotes import optimizeAbsenceInfo
from datetime import datetime

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

    def __init__(self, wilmaserver, wilmasession, mfa_token=None) -> None:
        super().__init__()
        self.wilmaserver = wilmaserver
        self.wilmasesson = wilmasession
        self.mfa_token = mfa_token
        self.httpclient = httpclient.WilmaHttpClient(self.wilmasesson, self.wilmaserver, self.mfa_token)

    """
    If server URL needs an change, this is for that
    """

    def changeWilmaAddress(self, server: str):
        self.httpclient.set_wilma_url(server)
        self.wilmaserver = self.httpclient.baseUrl

    """
    Sets Session ID cookie
    """

    def setSession(self, session_id, mfa_token=None):
        self.httpclient.user_auth = session_id
        self.wilmasesson = session_id
        self.mfa_token = mfa_token

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
                        if response['LoginResult'] == "mfa-required":
                            return MfaRequired(response.get("FormKey", None))
                        return ErrorResult("Not logged in!")
                    else:
                        return HomepageResult(optimizeHomepage(response), (len(response.get('Roles', [])) > 0))

                else:
                    return ErrorResult("Homepage couldn't be parsed")
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def get_root_user(self):
        try:
            result = self.httpclient.authenticated_root_get_request('index_json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                if "LoginResult" in response:
                    if response['LoginResult'] != "Ok":
                        if response['LoginResult'] == "mfa-required":
                            return MfaRequired(response.get("FormKey", None))
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

    def getProfileImage(self, user_id, user_type="teacher"):
        try:
            result = self.httpclient.authenticated_get_request(f'profiles/photo/{user_type}/{user_id}?format=json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
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
    Get schedule
    """

    def get_schedule(self, date: datetime = None):
        try:
            result = self.httpclient.authenticated_get_request(
                f"schedule/index_json?date={date.strftime('%d.%m.%Y') if date is not None else ''}")
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                schedule_result = ScheduleResult([], [])
                if "Terms" in response:
                    schedule_result.terms = wilmasdk.parser.schedule.parse_terms(response["Terms"])
                if "Schedule" in response:
                    schedule_result.schedule = wilmasdk.parser.schedule.parse_schedule(
                        date if date is not None else datetime.now(), response['Schedule'])
                return schedule_result
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    """
    Get schedule within a date range
    """

    def get_schedule_range(self, start_date: datetime, end_date: datetime):
        reservations = []
        terms = []
        for date in list(wilmasdk.parser.schedule.split_week_ranges(start_date, end_date)):
            schedule = self.get_schedule(date)
            if schedule.is_error():
                return schedule
            for reservation in schedule.schedule:
                reservations.append(reservation)
            if len(schedule.terms) > 0 and len(terms) < 1:
                terms = schedule.terms
        return ScheduleResult(reservations, terms)

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

    def getMessages(self, folder="all"):
        try:
            if folder == "all":
                inbox = self.httpclient.authenticated_get_request(f'messages/list/inbox')
                archive = self.httpclient.authenticated_get_request(f'messages/list/archive')
                outbox = self.httpclient.authenticated_get_request(f'messages/list/outbox')
                appointments = self.httpclient.authenticated_get_request(f'messages/list/appointments')
                messages = []

                for folder in [inbox, archive, outbox, appointments]:
                    if not folder.is_error():
                        error_check = checkForWilmaError(folder.get_response())
                        if error_check is not None:
                            return error_check
                    response = folder.get_response().json()
                    if "Messages" in response:
                        messages = messages + wilmasdk.parser.optimizer.optimizeMessages(response['Messages'])
                return MessagesResult(messages)
            else:
                result = self.httpclient.authenticated_get_request(f'messages/list/{folder}')
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

    def getRecipients(self):
        try:
            result = self.httpclient.authenticated_get_request('messages/recipients?format=json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                return RecipientsResult(response)
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getTeacherRecipients(self, school_id):
        try:
            result = self.httpclient.authenticated_get_request(f'messages/recipients/teachers/{school_id}?format=json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                if "TeacherRecords" not in response:
                    return NoRecipientsAvailable()
                return RecipientsResult(response["TeacherRecords"])
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getOwnTeachers(self, teachers_id):
        try:
            result = self.httpclient.authenticated_get_request(
                f'messages/recipients/ownteachers/{teachers_id}?format=json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                if "TeacherRecords" not in response:
                    return NoRecipientsAvailable()
                return RecipientsResult(response["TeacherRecords"])
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getClassRecipients(self, school_id):
        try:
            result = self.httpclient.authenticated_get_request(f'messages/recipients/class/{school_id}?format=json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                if "StudentRecords" not in response:
                    return NoRecipientsAvailable()
                return RecipientsResult(response["StudentRecords"])
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getPersonnelRecipients(self, school_id):
        try:
            result = self.httpclient.authenticated_get_request(f'messages/recipients/personnel/{school_id}?format=json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                if "PersonnelRecords" not in response:
                    return NoRecipientsAvailable()
                return RecipientsResult(response["PersonnelRecords"])
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def searchRecipients(self, query):
        try:
            result = self.httpclient.authenticated_get_request(f'messages/recipients/search?name={query}&format=json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                return RecipientsResult(response)
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def get_group_recipients(self, region=None, include_students=True, region_errors_as_empty=False):
        def get_period(name, errors_as_empty=False):
            wilma_period = self.fetch_group_recipients(name)
            if wilma_period.is_error():
                return [] if errors_as_empty else wilma_period
            wilma_period = [] if "PeriodGroups" not in wilma_period else wilma_period["PeriodGroups"]

            if include_students:
                for index, value in enumerate(wilma_period):
                    if "ID" in value:
                        students = self.fetch_group_recipients(value["ID"])
                        if students.is_error():
                            return students
                        students = [] if "StudentRecords" not in students else students["StudentRecords"]
                        wilma_period[index]['students'] = students
            return wilma_period

        if region is None:
            past = get_period("past", errors_as_empty=region_errors_as_empty)
            current = get_period("current", errors_as_empty=region_errors_as_empty)
            future = get_period("future", errors_as_empty=region_errors_as_empty)

            if not region_errors_as_empty:
                if not isinstance(past, list):
                    return past
                if not isinstance(current, list):
                    return current
                if not isinstance(future, list):
                    return future

            return RecipientsResult({"past": past, "current": current, "future": future})
        else:
            api_region = get_period(region)
            return api_region if api_region.is_error() else RecipientsResult(api_region)

    def fetch_group_recipients(self, group_region, key_element=None):
        try:
            result = self.httpclient.authenticated_get_request(f'messages/recipients/groups/{group_region}&format=json')
            if not result.is_error():
                error_check = checkForWilmaError(result.get_response())
                if error_check is not None:
                    return error_check
                response = result.get_response().json()
                if key_element is None or key_element in response:
                    return RecipientsResult(response)
                else:
                    return ErrorResult(f"Key element requirements not met: {key_element}")
            else:
                return result
        except Exception as e:
            return ErrorResult(e)

    def getMessage(self, message_id: int):
        try:
            result = self.httpclient.authenticated_get_request(f'messages/{str(message_id)}?format=json')
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

    def replyToMessage(self, message_id: int, content: str):
        try:
            formKeyResult = self.getFormKey()
            if formKeyResult.is_error():
                return formKeyResult
            result = self.httpclient.authenticated_post_request('messages/collatedreply/' + str(message_id),
                                                                {'formkey': formKeyResult.form_key, 'format': 'json',
                                                                 'bodytext': content})
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

    def getGroupInTimeline(self, timeline="past"):
        try:
            result = self.httpclient.authenticated_get_request(f'groups/index_json/{timeline}')
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
                                                                 'mid': str(message_id), 'format': 'json'}, False)
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
                                                                 'mid': str(message_id), 'format': 'json'}, False)
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
                                                                 'mid': str(message_id), 'format': 'json'}, False)
            if not result.is_error():
                if result.get_response().status_code == 303:
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
                if "LoginResult" in response and (response['LoginResult'] == "Ok"
                                                  or response["LoginResult"] == "mfa-required"):
                    if 'Wilma2SID' not in cookies:
                        return ErrorResult("Session not found")

                    if response['LoginResult'] == "mfa-required":
                        return MfaRequired(response.get("FormKey", None), cookies['Wilma2SID'])
                    return LoginResult(cookies['Wilma2SID'], (len(response.get('Roles', [])) > 0),
                                       optimizeHomepage(response))
                else:
                    return ErrorResult("Login failed, check username and password")
            else:
                return result
        except Exception as e:
            return ErrorResult(e)
