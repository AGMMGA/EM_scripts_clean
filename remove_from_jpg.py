#!/usr/bin/python

import argparse
import glob
import logging
import os
import shutil
import sys

class Micrograph_remover(object):
    
    def __init__(self):
        super(Micrograph_remover, self).__init__()
        self.parser = self.parse_args()
        self.check = self.check_args()
        self.logger = self.start_logger()
        
    def parse_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('-j','-jpg_folder', help='Folder where the jpgs are'
                            ' located'
                           'Default: current directory')
        parser.add_argument('-m','-micrograph_folder', help='Folder where the mrc'
                            ' are located. Default: ../')
        mode = parser.add_mutually_exclusive_group()
        mode.add_argument('-d', help = 'Delete the unwanted micrographs',
                          action='store_true')
        mode.add_argument('-r', help = 'Rename the unwanted micrographs to '
                          'file.mrc_bad (Default mode)', action='store_true')
        mode.add_argument('--star', help = 'starfile from which micrographs must be removed')
        parser.parse_args(namespace=self)
        return parser
    
    def check_args(self):
        if not hasattr(self, 'star'):
            self.star = None
        #checking jpg folder location
        if not self.j:
            self.j = os.getcwd()
        else:
            if not os.path.isdir(self.j):
                sys.exit('The jpg directory does not exit')                
        #checking micrographs folder location
        if not self.m:
            self.m = os.path.abspath(self.j +'/..')
        else:
            if not os.path.isdir(self.m):
                sys.exit('The micrograph dir {} does not exist'.format(self.m))
        #default is rename files in folder
        if not any((self.star, self.d, self.r)):
            self.r = True
        if hasattr(self, 'star') and not os.path.isfile(self.star):
            sys.exit('{} does not exist. Aborting'.format(self.star))            
        return 1
    
    def get_jpg_list(self):
        jpgs = glob.glob(os.path.join(self.j, '*.jpg'))
        if len(jpgs) == 0:
            sys.exit('No jpg files found in {}'.format(self.j))
        return jpgs
    
    def get_mrc_list(self):
        mrcs = glob.glob(os.path.join(self.m, '*.mrc'))
        return mrcs
    
    def rename_unwanted(self, files):
        for f in files:
            try:
                shutil.move(f, f + '_bad')
            except OSError as e:
                self.logger.error('The file {} could not be renamed'.format(f))
                self.logger.debug('Reason: {}\n\n'.format(str(e)))
    
    def delete_unwanted(self, files):
        for f in files:
            try:
                os.remove(f)
            except OSError as e:
                self.logger.debug('The file {} could not be removed'.format(f))
                self.logger.debug('Reason: {}\n\n'.format(str(e)))

    def start_logger(self):
        log = os.path.join(self.m, '{}remove_from_jpg.log')
        logger = logging.getLogger(__name__) 
        logging.basicConfig(filename = log, level=logging.INFO)
        return logger
    
    def find_extra_mrcs(self, jpgs, mrcs):
        jpgs.sort()
        mrcs.sort()
        jpgs_base = [os.path.basename(os.path.abspath(i)) for i in jpgs]
        mrcs_base = [os.path.basename(os.path.abspath(i)).replace('.mrc','.jpg') 
                     for i in mrcs]
        extra = []
        for i, value in enumerate(mrcs_base):
            if value not in jpgs_base:
                extra.append(mrcs[i])
        return extra
    
    def delete_from_starfile(self, mrcs, starfile):
        to_delete = [os.path.basename(m)[:-4] for m in mrcs] #*.mrc_bad
        with open(self.star, 'r') as f:
            buffer = f.read()
        out = []
        #remove all lines that mention bad micrographs
        for line in buffer.split('\n'):
#             if line in ['\n', 'data_', 'loop_']:
#                 out.append(line)
#                 continue
#             elif line.startswith('_') or line.startswith('#'):
#                 out.append(line)
#                 continue
#             elif not line:
#                 continue
            try:
                filename = os.path.basename(line.split()[0])
            except IndexError: #empty line
                out.append(line)
                continue
            if filename not in to_delete:
                out.append(line)
            #else ignore line and go on
        new_name = os.path.join(os.path.normpath(self.star),
                                (os.path.splitext(starfile)[0] + '_cleaned.star'))
        with open(new_name, 'w') as o:
            o.write('\n'.join(out))            
            
    def get_bad_mrc_list(self):
        return glob.glob(os.path.join(self.m, '*.mrc_bad'))
    
    def main(self):
        jpgs = self.get_jpg_list()
        mrcs = self.get_mrc_list()
        extra_mrcs = self.find_extra_mrcs(jpgs, mrcs)
        if len(extra_mrcs): 
            if self.r:
                self.rename_unwanted(extra_mrcs)
            if self.d:
                self.delete_unwanted(extra_mrcs)
            if self.star:
                self.delete_from_starfile(extra_mrcs, self.star)
                
        elif self.star: #files have already been renamed, maybe starfile still requires processing
            bad_mrcs = self.get_bad_mrc_list()
            self.delete_from_starfile(bad_mrcs, self.star)
        else:
            print ('No micrographs to rename/delete. All mrc files have a counterpart jpg file ')
        
        
if __name__ == '__main__':
    a = Micrograph_remover()
    a.main()