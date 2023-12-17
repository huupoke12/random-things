#!/usr/bin/env python3
import sys, hashlib
from PIL import Image

for path in sys.argv[1:]:
    try:
        with Image.open(path) as im:
            converted_img = im.convert('RGB')
            img_hash = hashlib.sha256(converted_img.tobytes()).hexdigest()
            print(f'{img_hash}  {path}')
    except Exception as err:
        print(err, file=sys.stderr)
