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