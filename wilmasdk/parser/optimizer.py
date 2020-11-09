#  Copyright (c) 2020 Developer From Jokela.
#  @author developerfromjokela
from PIL import Image
import base64
import io

"""
Does several things:
- Decodes profile image to Pillow object
"""


def optimizeHomepage(homepage):
    if "Roles" in homepage:
        for role in homepage['Roles']:
            if "Photo" in role and len(role['Photo']) > 0:
                role['Photo'] = base64ImageToPillow(role['Photo'])
    if "Photo" in homepage and len(homepage['Photo']) > 0:
        homepage['Photo'] = base64ImageToPillow(homepage['Photo'])
    return homepage


def base64ImageToPillow(image):
    msg = base64.b64decode(image)
    buf = io.BytesIO(msg)
    return Image.open(buf)
