import os, sys, shutil
from glob import glob

startpath = '/home/andrea/Downloads/ubiquitins/ub'
os.chdir(startpath)
files = glob('*.cif')
keywords = ['diubiquitin','di-ubiquitin', 'di ubiquitin']

for file_ in files:
    with open(file_,'r') as f:
        print('Searching in file {}'.format(file_))
        for keyword in keywords:
            for line in f:
                if line.startswith('ATOM'):
                    break
                elif keyword.lower() in line.lower():
                    new_folder = os.path.join(startpath, keyword)
                    if not os.path.isdir(new_folder):
                        os.mkdir(new_folder)
                    new_name = os.path.join(keyword, file_)                
                    shutil.copy(file_, new_name)
                    break
                