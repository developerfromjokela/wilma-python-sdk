#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

import hashlib


def generate_apikey(username, session_id, apikey):
    return "sha1:" + hashlib.sha1((username + "|" + session_id + "|" + apikey).encode('UTF-8')).hexdigest()
