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

def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))