#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela
from PIL import Image
import base64
import io

"""
Does several things:
- Decodes profile image to Pillow object
- Changes type to user-firendly string
"""

types = {
    1: 'teacher',
    2: 'student',
    3: 'personnel',
    4: 'guardian',
    5: 'workplaceinstructor',
    6: 'johtokunta',
    7: 'passwd'
}


def convertType(type):
    return types[type]


def optimize_dict(d):
    new = {}
    for k, v in d.items():
        if isinstance(v, dict):
            v = optimize_dict(v)
        elif isinstance(v, list):
            n = []
            for i in v:
                if isinstance(i, dict):
                    n.append(optimize_dict(i))
                else:
                    n.append(i)
            v = n
        new[k[0].lower() + k[1:]] = v
    return new


def optimize_dict_array(array):
    newArr = []
    for item in array:
        if isinstance(item, dict):
            newArr.append(optimize_dict(item))
    return newArr


def optimizeHomepage(homepage):
    if "Roles" in homepage:
        for role in homepage['Roles']:
            if "Photo" in role and len(role['Photo']) > 0:
                role['Photo'] = base64ImageToPillow(role['Photo'])
            if "Type" in role:
                role['Type'] = convertType(role['Type'])

    if "Photo" in homepage and len(homepage['Photo']) > 0:
        homepage['Photo'] = base64ImageToPillow(homepage['Photo'])
    if "Type" in homepage:
        homepage['Type'] = convertType(homepage['Type'])
    return optimize_dict(homepage)


def optimizeMessages(messages):
    ...


def optimizeMessage(message):
    newMessage = {
        'id': -1, 'subject': None, 'timestamp': None, 'folder': None,
        'sender': {'id': -1, 'type': None, 'name': None},
        'recipients': [],
        'content': None,
        'replies': [],
        'replyAllowed': False
    }


def base64ImageToPillow(image):
    msg = base64.b64decode(image)
    buf = io.BytesIO(msg)
    return Image.open(buf)
