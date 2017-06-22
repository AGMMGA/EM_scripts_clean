from pprint import pprint
import argparse
import os
import json
import sys
from PIL import Image, ImageDraw, ImageFont
from subprocess import Popen, PIPE
import shutil
import glob
from concurrent.futures import ProcessPoolExecutor

class Gautomatcher(object):
    
    def __init__(self):
        super().__init__()
        self.debug = True
        self.parse_arguments()
        self.check_args()
        self.mrc_files = glob.glob(os.path.join(self.mrc_folder, '*.mrc'))
            
    
    def parse_arguments(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--mrc_folder', help='The folder with the input .mrc files.'
                            ' Default: current directory')
        parser.add_argument('--jpg_in_folder', help='The folder with the input .jpg files.'
                            ' Default: [mrc_folder]/jpgs')
        parser.add_argument('--jpg_out_folder', help='The folder where the jpg files will be '
                            'stored. Default: [mrc_folder]')
        parser.add_argument('--star_folder', help='The folder where the star files will '
                            'be stored. Default: [mrc_folder]/annotated')
        parser.add_argument('--matrix_file', help='The file containing the parameters'
                            'to be tested. Default: [mrc_folder]/test.json')
        parser.add_argument('--debug', help='Activate debug mode', action='store_true')
        parser.add_argument('--n_threads', help='Number of parallel threads for'
                            ' execution. Default n=3')
        parser.add_argument('--default_params', help='A json file with starting parameters.'
                            ' Give full path if not in mrc_folder'
                            ' Default: [mrc_folder]/default_gautomatch_paramaters.json')
        parser.add_argument('--apixM', help='Pixel size in Angstrom')
        parser.add_argument('--diameter', help='Particle diameter, in Angstrom')
        parser.parse_args(namespace=self) 
        return parser
    
    def check_args(self):
        #setting mrc_folder default / checking existence
        if not self.mrc_folder:
            self.mrc_folder = os.path.abspath(os.getcwd())
        else:
            if not os.path.isdir(self.mrc_folder):
                sys.exit('The mrc folder {} does not exist. Exiting now.'.format(
                                                                self.mrc_folder))
            self.mrc_folder = os.path.abspath(self.mrc_folder)
        #setting jpg_in_folder default / checking existence
        if not self.jpg_in_folder:
            self.jpg_in_folder = os.path.join(self.mrc_folder, 'jpgs')
        if not os.path.isdir(self.jpg_in_folder):
                sys.exit('The jpg folder {} does not exist. Exiting now.'.format(
                                                            self.jpg_in_folder))
        #setting jpg_in_folder default / creating jpg_in_folder  
        if not self.jpg_out_folder:
            self.jpg_out_folder = self.mrc_folder
        if not os.path.isdir(self.jpg_out_folder):
                os.makedirs(self.jpg_out_folder)
        #setting star_folder default / creating star_folder  
        if not self.star_folder:
            self.star_folder = os.path.join(self.mrc_folder, 'annotated')
        else:
            if not os.path.isdir(self.o):
                os.makedirs(self.o)
        #setting n_threads default
        if not self.n_threads:
            self.n_threads = 3
        #setting test default parameters file / checking existence:
        #more convenient to do it this way than using argparse's default= option
        if not self.default_params:
            self.default_params = os.path.join(self.mrc_folder, 
                                               'default_gautomatch_parameters.json')
        if not os.path.isfile(self.default_params):
            msg = f'The matrix file {self.default_params} does not exist. Exiting now.'
            sys.exit(msg)
        self.default = self._import_parameters(self.default_params)
        self._check_default_parameters(self.default)
        #setting test matrix file / checking existence:
        if not self.matrix_file:
            self.matrix_file = os.path.join(self.mrc_folder, 'test.json')
            self.test = self._import_parameters(self.matrix_file)
        if not os.path.isfile(self.matrix_file):
            msg = f'The matrix file {self.matrix_file} does not exist. Exiting now.'
            sys.exit(msg)
        #pixel size can be set via command line, or via defaults file. 
        #command line overrides default file
        #needs to be type float
        if not self.apixM:
            self.apixM = self.default['apixM'] #already float
        else:
            self.apixM = float(self.apixM)
        #particle diameter can be set via command line, or via defaults file. 
        #command line overrides default file
        #needs to be float type
        if not self.diameter:
            self.diameter = self.default['diameter'] #already float
        #box size for drawing on image
        self.box_size = float(self.diameter / self.apixM)
        
    def pick_mrc(self, mrc):
        try:
            parms = self.test.copy() #otherwise we end up polluting def_parms
            parms['filein'] = mrc 
            print('Processing {}'.format(mrc))
            for par in self.test:
                new_jpg = self.copy_jpg(mrc, self.mrc_folder, par)
                print('Created {}'.format(new_jpg))
                count = 1
                coords = {}
                #iterating over each parameter to test    
                for value in self.test[par]:
                    #creating folder and link names
                    basename = '{}_{}'.format(par, value)
                    out_folder = os.path.join(self.star_folder, basename)
                    starfile = '{}_automatch.star'.format(os.path.basename(mrc).replace('.mrc', ''))
                    starfile = os.path.join(self.star_folder, basename, starfile)
                    print(f'Running gautomatch with {par} at {value}')
                    #doing the actual picking via gautomatch
                    linkname = self.prepare_gautomatch_folder(parms['filein'],
                                                               out_folder)
                    self.run_gautomatch(par, value, linkname)
                    #collect picked coordinates
                    coords[str(count)] = self.read_coords(starfile)
                    count += 1
                #create figure legend and annotate
                text_legend = self.create_legend(par, self.test[par])
                self.annotate_image(new_jpg, coords, text_legend)
            print('Done processing {}'.format(mrc))
        except Exception as e:
            print(e.__name__)
            print(e)
    
    def prepare_gautomatch_folder(self, mrc, subfolder):
        '''
        gautomatch automatically generates filenames based on the name of the input
        inside the current working directory. so we make a subdirectory and run 
        gautomatch from there, thus avoiding the overwriting of output files
        '''
        linkname = os.path.basename(mrc)
        try:
            os.mkdir(subfolder)
        except FileExistsError:
            pass #while self.testing
        os.chdir(subfolder)
        try:
            os.symlink(mrc, 
                       linkname)
        except FileExistsError:
            print('Uh oh cannot link to image')
            raise
        return linkname   
    
    def run_gautomatch(self, parameter, value, linkname):
#         cmd = 'gautomatch --apixM 1.76 --diameter 160 --speed {speed} --boxsize {boxsize} --min_dist {min_dist} --cc_cutoff {cc_cutoff} --lsigma_D {lsigma_D} --lsigma_cutoff {lsigma_cutoff} --lave_D {lave_d} --lave_max {lave_max} --lave_min {lave_min} --lp {lp} --hp {hp} {link}'.format(**parameter_set, link = linkname)
        test = f'--{parameter} {value}'
        print(test)
        default = ' '.join([f'--{p} {v}' for p, v in self.default.items() if p != parameter])
        cmd = f'gautomatch {default} {test} {linkname}'
        with Popen(cmd.split(), stdout = PIPE, stderr = PIPE) as gautomatch:
            print(f'Running gautomatch on {linkname}')
            out_ga, err = gautomatch.communicate()
            print(f'Ran gautomatch on {linkname}')
#             print(out_ga)
#             print(err)
        boxfile = '{}_automatch.box'.format(os.path.splitext(linkname)[0])
        with Popen(['wc', boxfile], stdout=PIPE, stderr=PIPE) as wc:
            out, err = wc.communicate()
            count = out.split()[0]
        os.chdir(self.mrc_folder)
        print(f'Picked {count} particles on {linkname}')
        return 1
            
    def prepare_subfolders(self):
        #make subfolders && clean annotated subfolder
        try:
            os.mkdir(self.jpg_in_folder)
        except FileExistsError:
            pass
        try:
            os.mkdir(self.star_folder)
        except FileExistsError:
            shutil.rmtree(self.star_folder)
            os.mkdir(self.star_folder)
    
    def check_jpgs_are_present(self):
        t = os.path.join(self.jpg_in_folder, '*.jpg')
        jpg_filenames = [os.path.basename(i).replace('.jpg', '') 
                         for i in glob.glob(t)]
        mrc_filenames = [os.path.basename(i).replace('.mrc', '') 
                         for i in self.mrc_files]
        return set(mrc_filenames) <= set(jpg_filenames)

    def draw_circles(self, coords, box_size, radius, image, thickness = 5,
                         color = '#00ff00'):
            '''
            coords = [(x0,y0),...(xn,yn)] where x and y specify the center of the binding box
            radius = radius of the ellipse to be drawn
            image = the image where you want the ellipse to be drawn
            thickness = how thick the border of the ellipse should be
            outline = color of the outline
            '''
            draw = ImageDraw.Draw(image)
            for set in coords:
                for i in range(thickness):
                    center_x = set[0]
                    center_y = set[1]
                    #relion gives the xy of the center of the circle; 
                    #PIL wants the xy of upper left corner of the binding box
                    draw.ellipse((center_x-radius-i, center_y-radius+i, 
                                  center_x+radius+i, center_y+radius-i),
                                  outline=color)
            return image
    
    def write_on_image(self, image, text, posxy, color='#00ff00'):
        font_file = '/usr/share/fonts/truetype/ubuntu-font-family/UbuntuMono-R.ttf'
        font = ImageFont.truetype(font_file, size=100)
        draw = ImageDraw.Draw(image)
        draw.text(posxy, text, font=font, fill=color)
        return image
    
    def read_coords(self, starfile):
        coords = []
        with open(starfile, 'r') as f:
            for line in f:
                if line[0].isdigit():
                    coords.append((int(line.split()[0]),
                                   int(line.split()[1])))
        return coords
    
    def open_as_rgb(self, grayscale_image):
        img =  Image.open(grayscale_image)
    #     img.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_180)
        rgbimage = Image.new('RGB', img.size)
        rgbimage.paste(img)
        return rgbimage
        
    def create_legend(self, par,grid):
        text_legend = {'1': '{} = {}'.format(par, grid[0]),
                  '2': '{} = {}'.format(par, grid[1]),
                  '3': '{} = {}'.format(par, grid[2])}
        return text_legend
    
    def copy_jpg(self, mrc, out_folder, par):
        original_jpg =os.path.join(self.jpg_in_folder, 
                                   os.path.basename(mrc).replace('mrc', 'jpg')) 
        new_jpg = os.path.basename(original_jpg).replace('.jpg', '_{}.jpg').format(par)
        new_jpg = os.path.join(self.mrc_folder, new_jpg)
        shutil.copy(original_jpg, new_jpg)
        return new_jpg
    
    def annotate_image(self, jpg, coords, text_legend):
        radius = int(self.box_size)
        colors = {'1': '#00ff00',
                  '2': '#ff0000',
                  '3': '#0000ff'}
        text_pos= {'1': (30,30),
                  '2': (30,120),
                  '3': (30,190)}
        for i in ['1','2','3']:
            rgbimage = self.open_as_rgb(jpg)
            rgbimage = self.draw_circles(coords[i], self.box_size, radius, rgbimage,
                                    color= colors[i])
            rgbimage = self.write_on_image(rgbimage, text_legend[i], text_pos[i], 
                                      color = colors[i])
            rgbimage.save(jpg)
            radius += 6 
        
    def run_parallel(self):
        with ProcessPoolExecutor(max_workers=3) as executor:
            executor.map(self.pick_mrc, self.mrc_files)
            
    def _run_sequential(self):
        #for debugging purposes since parallelization suppresses errors
        for f in self.mrc_files:
            self.pick_mrc(f)   
            
    def _import_parameters(self,parms_file):
        '''
        reads a json file with default parameters (i.e. not under test)
        returns a dictionary in the form {"param":value}
        where value can be int, float, str, [] or None as required
        '''
        with open(parms_file, 'r') as f:
            params = json.load(f)
        
        p = params.copy()
        for key, value in params.items():
            if value == 'None':
                del(p[key])
                continue
            if '[' in value:
                try:
                    p[key]=(eval(value))
                except ValueError:
                    msg = f'Malformed list of test parameters:\n {key}:{value}'
                    sys.exit(msg)
            try:
                if '.' in value:
                    p[key]=float(value)
                else:
                    p[key]=int(value) 
            except ValueError:
                continue
        return p
    
    def _check_default_parameters(self, default_parms):
        '''
        input: a dictionary of parameters as defined by _import_parameters.
        checks that the default parameters are sane or throws an exception
        checks performed:
        1 - some parameters are input files -> check existence
        '''
        to_check = ['exclusive_picking','excluded_suffix','global_excluded_box','T']
        for key in to_check:
            try: #these keys will only exist if the user specifies them. 
                if not os.path.isfile(default_parms[key]): #The values are files. We check they exist
                    msg=f'file not found for {key} in default parameters file {default_parms}'
                    sys.exit(msg)
            except KeyError:
                pass 
                    
    
    def main(self):
#         assert self.check_jpgs_are_present(), 'Some jpg files are missing'
        self.prepare_subfolders()
        too_many_parms_msg = 'For practical reasons, I can only iterate over n==3 values of each parameter'
        for par in self.test:
            assert len(self.test[par]) == 3, too_many_parms_msg 
        print(f'The script will iterate over the following parameters: {self.test}')
        if self.debug:
            self._run_sequential() #debug_mode
        else:
            self.run_parallel()
    
if __name__ == '__main__':
    g = Gautomatcher()
    g.main()


