#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

class TokenExpiredException(Exception):

    def __init__(self) -> None:
        super().__init__("Login session expired, please renew!")
