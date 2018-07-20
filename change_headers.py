import os

filename = '/home/andrea/Downloads/usp48.fasta'
s = 'mrglvrem'
i=1

def uniquify(i):
    with open(filename, 'r') as f_in:
        with open(filename + '_corrected', 'w') as out:
            for line in f_in:
                if line.startswith('>'):
                    new_line = line.replace('\n','') + '_' + str(i) + '\n'
                    out.write(new_line)
                    i+=1
                else:
                    out.write(line)
            
def uniquify_trim(pos):
    i = 0
    with open(filename, 'r') as f_in:
        with open(filename + '_trimmed', 'w') as out:
            for line in f_in:
                if line.startswith('>'):
                    new_line = line.replace('\n','') + '_' + str(i) + '\n'
                    out.write(new_line)
                    i+=1
                else:
                    out.write(line[pos:])
                    
def find_shit(pattern):
    with open(filename, 'r') as f_in:
        for line in f_in:
            if pattern.upper() in line:
                return line.find(pattern.upper())
                
                    
#   
uniquify_trim(find_shit('ialiwps'))