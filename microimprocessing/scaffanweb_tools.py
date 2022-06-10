# /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import zipfile

# zipdir
#
# def zipdir(path, zip_fn):
#
#     ziph = zipfile.ZipFile(zip_fn, 'w', zipfile.ZIP_DEFLATED)
#     # ziph is zipfile handle
#     for root, dirs, files in os.walk(path):
#         for file in files:
#             ziph.write(os.path.join(root, file))
# zipdir('./my_folder', zipf)
# zipf.close()

import random
import string
import numpy as np
import skimage.transform

import random
try:
    from hashlib import sha1 as sha_constructor
except ImportError:
    from django.utils.hashcompat import sha_constructor


def generate_sha1(string, salt=None):
    """
    Generates a sha1 hash for supplied string.

    :param string:
        The string that needs to be encrypted.

    :param salt:
        Optionally define your own salt. If none is supplied, will use a random
        string of 5 characters.

    :return: Tuple containing the salt and hash.

    """
    string = str(string)
    if not salt:
        salt = str(sha_constructor(str(random.random())).hexdigest()[:5])
    import hashlib
    # >> > sha = hashlib.sha256()
    # >> > sha.update('somestring'.encode())
    # >> > sha.hexdigest()
    hash = sha_constructor((salt+string).encode()).hexdigest()

    return hash

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def crop_square(frame:np.ndarray) -> np.ndarray:

    mn = np.min(frame.shape[:2])
    sh0 = frame.shape[0]
    sh1 = frame.shape[1]
    if sh0 > sh1:
        st0 = int((sh0/2) - (sh1/2))
        st1 = 0
    else:
        st0 = 0
        st1 = int((sh1/2) - (sh0/2))

    frame = frame[st0:st0+mn, st1:st1+mn]

    return frame

def resize_image(img:np.ndarray, scale=None, height=None, width=None):

    if scale is None and width is not None:
        scale = width / img.shape[1]
    if scale is None and height is not None:
        scale = height / img.shape[0]

    img = skimage.transform.rescale(img, scale, multichannel=True, preserve_range=True)
    return img