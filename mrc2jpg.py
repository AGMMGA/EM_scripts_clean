from __future__ import division, absolute_import, print_function
import glob
import os
import sys
import subprocess
import argparse
import errno
import multiprocessing
from PIL import Image
from multiprocessing.dummy import Pool as ThreadPool




class imageConverter(object):
    
    def __init__(self):
        super(imageConverter, self).__init__()
        self.parse()
        self.check = self.check_args()
    
    def parse(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', help='The folder with the input .mrc files. Default: current directory')
        parser.add_argument('-o', help='The folder where the jpg files will be stored. Default: [current]/jpegs')
        parser.add_argument('-f', help='Force overwriting of existing files', 
                            action='store_true')
        parser.add_argument('--scale', help='Scale factor e.g. 4 shrinks by 4 '
                            'times')
        parser.add_argument('--lowpass', help='Lowpass resolution in Angstrom')
        parser.add_argument('--n_cpus', help='How many cpus should be used. Default: all available -1')
        parser.add_argument('--noflip', help='Does NOT rotate and flip the jpg to conform with relion coordinates',
                            action='store_true')
        parser.add_argument('--invert', help='Invert contrast', action='store_true')
        parser.add_argument('--file', help='File containing micrograph names')
        parser.parse_args(namespace=self) 
        return parser
        
    def check_args(self):
        #explicitly setting self.f if not present
        if not self.f:
            self.f = False
        #setting input dir and checking existence if supplied
        #check for input file
        if self.file and not os.path.isfile(self.file):
            sys.exit(f'The input file {self.file} does not exist')
        if not self.i:
            self.i = os.getcwd()
        else:
            if not os.path.isdir(self.i):
                sys.exit('The path {} does not exist. Use -f to create'.format(self.i))
        #Setting default output dir to /jpgs and creating it if not existing. 
        if not self.o:
            self.o = os.path.join(self.i, 'jpgs')
            if not os.path.isdir(self.o):
                os.makedirs(self.o)
        #if output dir is provided, checking that it exists and/or creating it
        else:
            if not os.path.isdir(self.o) and self.f:
                os.makedirs(self.o)
            if not os.path.isdir(self.o) and not self.f:
                sys.exit('The path {} does not exist. Use -f to create'.format(self.o))
        #setting scale factor
        if not self.scale:
            self.scale = ''
        else:
            if self.scale.isdigit():
                self.scale = '--meanshrink {}'.format(self.scale)
            else:
                sys.exit('{} is not a valid scale factor')
        #setting processing options
        if not self.lowpass:
            self.lowpass = ''
        else:
            self.lowpass = self.lowpass.replace('A','')
            if self.lowpass.isdigit():
                self.lowpass = '--process filter.lowpass.gauss:cutoff_freq={}'.format(\
                                                            1/int(self.lowpass))
            else:
                sys.exit('{} is not a valid resolution')
        if self.invert:
            self.invert = '--mult=-1'
        else:
            self.invert = ''
        #checking cpus
        try:
            cpu_max = multiprocessing.cpu_count()
        except NotImplementedError:
            cpu_max = 4
            print ('I cannot detect the number of cpus on the system, defaulting to 4') 
        
        if not self.n_cpus:
            self.n_cpus = cpu_max -1
        else:
            try:
                self.n_cpus = int(self.n_cpus)
            except TypeError:
                sys.exit('please give an integer number for the --n_cpu parameter')
            if self.n_cpus > cpu_max:
                sys.exit('Only {0} CPUs are available on this system. Please make sure that n_cpus <= {0}'.format(cpu_max))
    
    def convert_image(self, mrcfile):
        outfile = os.path.join(self.o, (mrcfile.split('/')[-1].replace('.mrc', '.jpg')))
        if os.path.isfile(outfile) and not self.f:
            raise IOError(errno.EEXIST)
        elif os.path.isfile(outfile) and self.f:
            os.remove(outfile) #otherwise eman might make a stack
        command = 'python2.7 /Xsoftware64/EM/EMAN2/bin/e2proc2d.py ' + \
            '{lowpass} {scale} {invert} {mrc} {jpg}'.format(mrc=mrcfile, 
                                                   jpg=outfile,
                                                   scale = self.scale,
                                                   lowpass = self.lowpass,
                                                   invert = self.invert)
        command = command.split()
        s = subprocess.Popen(command, stdout=subprocess.PIPE, 
                             stderr = subprocess.PIPE)
        _, err = s.communicate()
        #EMAN2 might fail randomly
        if 'Traceback' in str(err) and not self.f:
            sys.exit('EMAN2 failed with the following error: \n\n{}'.format(err))
        print (err)
        print(_)
        print ('Converted {}'.format(outfile.split('/')[-1]))
        #finally, flip horizontal and rotate 180 because EMAN2 chooses different
        #coordinates compared to relion which we will use downstream
        if not self.noflip:
            self.flip_and_rotate(outfile)
            print('Flipped & rotated {}'.format(outfile.split('/')[-1]))
         
    def flip_and_rotate(self, image):
        img =  Image.open(image)
        img = img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_180)
        return img.save(image, "JPEG")
    
    def get_mrc_files(self):
        files = glob.glob(os.path.join(self.i, '*.mrc'))
        if files:
            return files
        else:
            sys.exit('No mrc files found in {}'.format(self.i))
            
    def get_mrc_files_from_file(self, input_file):
        with open (input_file, 'r') as filein:
            files = filein.readlines()
        #checking all files exist, or force flag is set
        for f in files:
            if not os.path.isfile(f) and self.f: #force
                print(f'Warning: file {f} does not exist')
                continue
            elif not os.path.isfile and not self.f:
                sys.exit('File {f} in file list {self.file} does not exist. Aborting. Use -f to force ')
        #checking some files exist
        if not files:
            sys.exit(f'No files found in input file {input_file}')
        return files
    
    def create_images(self, mrclist):
        if not os.path.isdir(self.o):
            os.makedirs(self.o)
        for f in sorted(mrclist):
            try:
                self.convert_image(f)
            except IOError:
                msg = '{} exists. Skipped. Use -f to force overwrite'.format(
                            f.replace('.mrc','.jpg'))
                print(msg)
    
    def make_commands(self, mrclist):
        cmds = []
        for file_ in mrclist:
            outfile = os.path.join(self.o, (file_.split('/')[-1].replace('.mrc', '.jpg')))
            command = 'python /Xsoftware64/EM/EMAN2/bin/e2proc2d.py ' + \
                    '{lowpass} {scale} {mrc} {jpg}'.format(mrc=file_, 
                                                       jpg=outfile,
                                                       scale = self.scale,
                                                       lowpass = self.lowpass)
            cmds.append(command.split())
        return cmds
    
    def create_images_parallel(self, mrclist):
        if not os.path.isdir(self.o):
            os.makedirs(self.o)
        pool = ThreadPool(self.n_cpus)
        _ = pool.map(self.convert_image, mrclist)
        pool.close()
        pool.join()
        
    def main(self):
            if not self.file:
                files = self.get_mrc_files()
            else:
                files = self.get_mrc_files_from_file(self.file)
            self.create_images_parallel(files)
#             self.create_images(files) #testing
    

if __name__ == '__main__':
    i = imageConverter()
    i.main()
    
