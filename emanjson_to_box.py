import json
import os
import glob
import sys

def main(input,out_dir, box_size):
    
    input_files = glob.glob(input) 
    if not input_files:
        msg = (f'No files with pattern {input} found')
        sys.exit(msg)
        
    for file_ in input_files:
        with open(file_, 'r') as f:
            j_object = json.load(f) 
        
        out_file = os.path.join(out_dir, os.path.basename(file_).split('_info.json')[0] + '.box')
#         out_name = os.path.splitext(os.path.basename(file_))[0] + '.box'
#         out_file = os.path.join(out_dir, out_name)
        with open(out_file, 'w') as out:
            for ptcl in j_object['boxes']:
                x,y = ptcl[:2]
                out.write(f'{x}\t{y}\t{box_size}\t{box_size}\n')

if __name__ == '__main__':
    input_dir = '/local_data/tassos/JBP3_neg_stain/info'
    input_file = '20170614-JBP3NegStain__???_info.json'
    input = os.path.join(input_dir, input_file)
    out_dir = '/local_data/tassos/JBP3_neg_stain/Tati_pick'
    box_size = 96
    main(input,out_dir, box_size)