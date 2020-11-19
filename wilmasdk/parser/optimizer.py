#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela
from PIL import Image
import base64
import io
import datetime

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


def existenceCheck(dist_item, key):
    return key in dist_item and dist_item[key] is not None


def convertType(type):
    return types[type]


def parseMessageTimestamp(string_time):
    try:
        return datetime.datetime.strptime(string_time, "%Y-%m-%d %H:%M")
    except:
        # Checking if the format is another one, because visma's api does so at midnight
        try:
            return datetime.datetime.strptime(string_time, "%Y-%m-%d")
        except:
            return None


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


def optimizeMessage(message):
    newMessage = {
        'id': -1, 'subject': None, 'timestamp': None, 'folder': None,
        'sender': {'id': -1, 'type': None, 'name': None, 'studentName': None, 'senderGuardianId': -1, 'senderGuardianName': None},
        'eventData': None,
        'recipients': [],
        'content': None,
        'replies': [],
        'replyAllowed': False,
        'isEvent': False
    }
    if existenceCheck(message, "Id"):
        newMessage['id'] = message['Id']
    if existenceCheck(message, "Subject"):
        newMessage['subject'] = message['Subject']
    if existenceCheck(message, "Folder"):
        newMessage['folder'] = message['Folder']
    if existenceCheck(message, "Recipients"):
        newMessage['recipients'] = message['Recipients']
    if existenceCheck(message, "TimeStamp"):
        newMessage['timestamp'] = parseMessageTimestamp(message['TimeStamp'])
    if existenceCheck(message, "SenderId"):
        newMessage['sender']['id'] = message['SenderId']
    if existenceCheck(message, "SenderType"):
        newMessage['sender']['type'] = convertType(message['SenderType'])
    if existenceCheck(message, "Sender"):
        newMessage['sender']['name'] = message['Sender']
    if existenceCheck(message, "SenderStudentName"):
        newMessage['sender']['studentName'] = message['SenderStudentName']
    if existenceCheck(message, "SenderPasswdID"):
        newMessage['sender']['senderGuardianId'] = message['SenderPasswdID']
    if existenceCheck(message, "SenderGuardianName"):
        newMessage['sender']['senderGuardianName'] = message['SenderGuardianName']
    if existenceCheck(message, "AllowCollatedReply"):
        newMessage['replyAllowed'] = message['AllowCollatedReply']
    if existenceCheck(message, "IsEvent"):
        newMessage['isEvent'] = message['IsEvent']
    # Events support is not fully supported yet
    if existenceCheck(message, "EventData"):
        newMessage['eventData'] = optimize_dict(message['EventData'])
    if existenceCheck(message, "ContentHtml"):
        newMessage['content'] = message['ContentHtml']
    if existenceCheck(message, "ReplyList"):
        for reply in message['ReplyList']:
            newMessage['replies'].append(optimizeReply(reply))
    return newMessage


def optimizeMessages(messages):
    newMessages = []
    for item in messages:
        newMessages.append(optimizeMessage(item))
    return newMessages


def optimizeReply(reply):
    newReply = {'id': None, 'content': None, 'timestamp': None,
                'sender': {'id': -1, 'type': None, 'name': None}}
    if existenceCheck(reply, "Id"):
        newReply['id'] = reply['Id']
    if existenceCheck(reply, "ContentHtml"):
        newReply['content'] = reply['ContentHtml']
    if existenceCheck(reply, "TimeStamp"):
        newReply['timestamp'] = parseMessageTimestamp(reply['TimeStamp'])
    if existenceCheck(reply, "SenderId"):
        newReply['sender']['id'] = reply['SenderId']
    if existenceCheck(reply, "SenderType"):
        newReply['sender']['type'] = convertType(reply['SenderType'])
    if existenceCheck(reply, "Sender"):
        newReply['sender']['name'] = reply['Sender']


def base64ImageToPillow(image):
    msg = base64.b64decode(image)
    buf = io.BytesIO(msg)
    return Image.open(buf)
