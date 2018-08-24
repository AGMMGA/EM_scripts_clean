# Relion coordinates to cisTEM
# Written by Dawid Zyla
#
# This easy script allows you to use Relion picked particles with cisTEM.
# Copy particles.star from export job from Relion directory to the same directory where are the images imported by
# cisTEM. You can choose if you want to create a list of files automaticaly or you will provide the files.txt file
#

import os
import glob
import sys
import re

path = '/local_data/shreya/20180529_Rad6_Rad18_PCNA_neg/A4_cisTEM/PCNA/Micrographs'
starfile = os.path.join(path, 'particles.star')
outfile = os.path.join(path, 'cistem_coordinates.txt')
pattern = os.path.join(path, '*.mrc')
mrc_cis_full = [os.path.basename(i) for i in glob.glob(pattern)]

if not mrc_cis_full:
    sys.exit(f'No micrographs found in {path}')
    
assert os.path.isfile(starfile)

#change here!
pixel_size = 2.33
counter = 0

# create a list from particle.star file
with open(starfile, 'r') as p:
    ptcls = p.readlines()
ptcls = list(set(ptcls)) #particles might be in more than one class average (ML)
cleaned = [p for p in ptcls if re.sub(r'\s+', '', p) #remove whitespace
                                   if '_' not in p] #remove headers
out_ptcls = []
for particle in ptcls:
    line = particle.split()
    if len(line)>3: #header and empty lines
        micrograph = os.path.basename(line[3])
        if micrograph not in mrc_cis_full:
            continue
        x_ang = float(line[0].strip()) * pixel_size
        y_ang = float(line[1].strip()) * pixel_size
        out_ptcls.append(f'{micrograph} {x_ang} {y_ang}')
        counter +=1
out_ptcls = sorted(out_ptcls)
with open(outfile, 'w') as f:
    f.write('\n'.join(out_ptcls))
print(f'Found {counter} number of particles and written to {outfile}')
