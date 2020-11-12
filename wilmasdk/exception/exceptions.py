#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

class TokenExpiredException(Exception):

    def __init__(self) -> None:
        super().__init__("Login session expired, please renew!")


class NoExcuseInformationException(Exception):

    def __init__(self) -> None:
        super().__init__("Unable to get excuse reasons, when you don't have any lesson notes to do clearance on")