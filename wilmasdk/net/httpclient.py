#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela
import sys

import requests

if ((3, 0) <= sys.version_info <= (3, 9)):
    from urllib.parse import urlparse
elif ((2, 0) <= sys.version_info <= (2, 9)):
    from urlparse import urlparse

from .classes import *


class WilmaHttpClient:

    def __init__(self, user_auth, wilma_url):
        if wilma_url is not None and wilma_url[len(wilma_url)-1] is not "/":
            wilma_url = wilma_url + "/"
        self.user_auth = user_auth
        self.baseUrl = wilma_url
        self.sessionHttp = requests.Session()

    """
    Set Wilma BaseURL here
    """
    def set_wilma_url(self, url):
        if url is not None and url[len(url)-1] is not "/":
            url = url + "/"
        self.baseUrl = url

    def getBaseURLDomainName(self):
        return '{uri.netloc}'.format(uri=urlparse(self.baseUrl))

    def get_request_external(self, url):
        try:
            r = self.sessionHttp.get(  url)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def get_request(self, url):
        try:
            r = self.sessionHttp.get(self.baseUrl + url)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def authenticated_get_request(self, url):
        sessionCookie = requests.cookies.create_cookie(domain=self.getBaseURLDomainName(), name='Wilma2SID',
                                                       value=self.user_auth)
        self.sessionHttp.cookies.set_cookie(sessionCookie)
        try:
            r = self.sessionHttp.get(self.baseUrl + url)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def post_request(self, url, data, headers=None, followRedirects=True):
        try:
            r = self.sessionHttp.post(self.baseUrl + url, data=data, allow_redirects=followRedirects)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def authenticated_post_request(self, url, data, followRedirects=True):
        sessionCookie = requests.cookies.create_cookie(domain=self.getBaseURLDomainName(), name='Wilma2SID',
                                                       value=self.user_auth)
        self.sessionHttp.cookies.set_cookie(sessionCookie)

        try:
            r = self.sessionHttp.post(self.baseUrl + url, data=data,
                                      allow_redirects=followRedirects)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)

    def loginId_post_request(self, url, data, session_id, followRedirects=True):
        sessionCookie = requests.cookies.create_cookie(domain=self.getBaseURLDomainName(), name='Wilma2LoginID',
                                                       value=session_id)
        self.sessionHttp.cookies.set_cookie(sessionCookie)
        try:
            r = self.sessionHttp.post(self.baseUrl + url, data=data,
                                      allow_redirects=followRedirects)
            return RequestResult(False, None, r)
        except Exception as e:
            return ErrorResult(e)
