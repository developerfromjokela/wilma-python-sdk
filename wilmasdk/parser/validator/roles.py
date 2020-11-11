#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

def validateRole(role):
    requiredFields = ['name', 'type', 'primusId', 'formKey', 'photo']
    return all(name in role for name in requiredFields)
