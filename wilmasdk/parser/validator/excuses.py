#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela

def validateExcuse(excuse):
    requiredFields = ['id', 'caption']
    excuseTextRequirement = ('requireText' in excuse) or ('explanationAllowed' in excuse)
    return all(name in excuse for name in requiredFields) and excuseTextRequirement
