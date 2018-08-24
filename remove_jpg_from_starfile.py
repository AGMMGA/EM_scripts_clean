import os
import glob

def main():
    os.chdir(jpg_dir)
    jpgs = [os.path.splitext(f)[0] + '.mrc' for f in glob.glob('*.jpg')]
    os.chdir(work_dir)
    with open(starfile, 'r') as f:
        temp = f.readlines() 
    print(temp)
    out = []
    for line in temp:
        if os.path.basename(line.split()[0]) in jpgs:
            out.append(line)
    with open(outfile, 'w') as f:
        f.write('\n'.join(out))


if __name__ == '__main__':
    work_dir = '/local_data/andrea/relion3_benchmark/Select/ctf_res'
    starfile = 'micrographs.star.bak'
    outfile = 'micrographs_clean.star'
    jpg_dir = '/local_data/andrea/relion3_benchmark/Micrographs/jpgs'
    main()