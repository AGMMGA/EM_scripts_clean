import os

def main():
    os.chdir(workdir)
    with open(starfile, 'r') as f:
        temp = f.readlines()
    filenames = [os.path.basename(line.split()[0]) 
                 for line in temp 
                 if line.strip() 
                 if not line.startswith('_')
                 if not line.rstrip().endswith('_')]
    
    with open(outfile, 'w') as f:
        f.write('\n'.join(filenames))


if __name__ == '__main__':
    workdir = '/local_data/andrea/relion3_benchmark/Select/ctf_res'
    starfile = 'micrographs.star'
    outfile = 'names.txt'
    main()