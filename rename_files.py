import glob
import os
import shutil
from math import ceil, log10

path = os.path.abspath(os.getcwd())
files = glob.glob(os.path.join(path, '*.tif'))

if not files:
    raise OSError('no files found')

digits = int(ceil(log10(len(files))))

for f in files:
    base, ext = os.path.splitext(f)
    root, number = os.path.basename(base).split('_') 
    number = number.zfill(digits)
    new_name = os.path.join(path,
                            '{}_{}{}'.format(root, number, ext))
    shutil.move(f, new_name)
    