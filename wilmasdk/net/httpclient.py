#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

import requests

from urllib.parse import urlparse

from .classes import *


class WilmaHttpClient:

    def __init__(self, user_auth, wilma_url, mfa_token):
        if wilma_url is not None and wilma_url[len(wilma_url) - 1] is not "/":
            wilma_url = wilma_url + "/"
        self.user_auth = user_auth
        self.baseUrl = wilma_url
        self.mfa_token = mfa_token
        self.sessionHttp = requests.Session()

    """
    Set Wilma BaseURL here
    """

    def set_wilma_url(self, url):
        if url is not None and url[len(url) - 1] is not "/":
            url = url + "/"
        self.baseUrl = url

    def getBaseURLDomainName(self):
        return '{uri.netloc}'.format(uri=urlparse(self.baseUrl))

    """
    Removing cookies, because they're injected anyway when needed
    Requests stores them across requests, we don't need that
    """

    def clearCookies(self):
        self.sessionHttp.cookies.clear()

    def get_request_external(self, url):
        self.clearCookies()
        try:
            r = self.sessionHttp.get(url)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def get_request(self, url):
        self.clearCookies()
        try:
            r = self.sessionHttp.get(self.baseUrl + url)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def authenticated_get_request(self, url):
        self.clearCookies()
        session_cookie = requests.cookies.create_cookie(domain=self.getBaseURLDomainName(), name='Wilma2SID',
                                                        value=self.user_auth)
        mfa_cookie = requests.cookies.create_cookie(domain=self.getBaseURLDomainName(), name='Wilma2MFASID',
                                                        value=self.mfa_token)
        self.sessionHttp.cookies.set_cookie(session_cookie)
        self.sessionHttp.cookies.set_cookie(mfa_cookie)
        try:
            r = self.sessionHttp.get(self.baseUrl + url)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def post_request(self, url, data, headers=None, followRedirects=True):
        self.clearCookies()
        try:
            r = self.sessionHttp.post(self.baseUrl + url, data=data, allow_redirects=followRedirects)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def authenticated_post_request(self, url, data, followRedirects=True):
        self.clearCookies()
        session_cookie = requests.cookies.create_cookie(domain=self.getBaseURLDomainName(), name='Wilma2SID',
                                                        value=self.user_auth)
        mfa_cookie = requests.cookies.create_cookie(domain=self.getBaseURLDomainName(), name='Wilma2MFASID',
                                                    value=self.mfa_token)
        self.sessionHttp.cookies.set_cookie(session_cookie)
        self.sessionHttp.cookies.set_cookie(mfa_cookie)

        try:
            r = self.sessionHttp.post(self.baseUrl + url, data=data,
                                      allow_redirects=followRedirects)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def loginId_post_request(self, url, data, session_id, followRedirects=True):
        self.clearCookies()
        session_cookie = requests.cookies.create_cookie(domain=self.getBaseURLDomainName(), name='Wilma2LoginID',
                                                        value=session_id)
        mfa_cookie = requests.cookies.create_cookie(domain=self.getBaseURLDomainName(), name='Wilma2MFASID',
                                                    value=self.mfa_token)
        self.sessionHttp.cookies.set_cookie(session_cookie)
        self.sessionHttp.cookies.set_cookie(mfa_cookie)
        try:
            r = self.sessionHttp.post(self.baseUrl + url, data=data,
                                      allow_redirects=followRedirects)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)
