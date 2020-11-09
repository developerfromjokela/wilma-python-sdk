#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

def validateRole(role):
    requiredFields = ['Name', 'Type', 'PrimusId', 'FormKey', 'Photo']
    return all(name in role for name in requiredFields)
