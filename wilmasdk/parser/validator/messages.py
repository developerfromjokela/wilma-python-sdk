#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

def validateMessageForReplying(message):
    requiredFields = ['id', 'replyAllowed']
    return all(name in message for name in requiredFields)
