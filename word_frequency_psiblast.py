import os
import matplotlib.pyplot as plt
import numpy as np
import re
from bs4 import BeautifulSoup

def plot_frequencies(final_text):
    freq={}
#     match_pattern = re.findall(r'\b[a-z]{1,15}\b', final_text)
    try:
        match_pattern = final_text.split()
    except AttributeError as e:
        if isinstance(final_text, list):
            match_pattern = final_text
        else:
            raise e
    for word in match_pattern:
        count=freq.get(word,0)
        freq[word]=count + 1
    frequency_list = freq.keys()
    for words in frequency_list:
        print(words + ' -> ' + str(freq[words]))
    results = []
    for word in frequency_list:
        tuple_ = (word, freq[word])
        results.append(tuple_)
    byFreq=sorted(results, key=lambda word: word[1], reverse=True)
    words_names=[]
    words_count=[]
    for (word, freq) in byFreq[:]:
        print (word, freq)
        words_names.append(word)
        words_count.append(freq)
    # Plot histogram using matplotlib bar()
    plt.ylabel('Words')
    plt.xlabel('Frequency')
    indexes = np.arange(len(words_names) )
    width = .4
    plt.barh(indexes, words_count, width)
    plt.yticks(indexes + width * .4, words_names)
    plt.tick_params(labelsize='small')
    #plt.legend()
#     plt.tight_layout()
    plt.show()

def parse_result(xml_file):    
    with open (xml_file, 'r') as f:
        soup = BeautifulSoup(f.read(), 'lxml')
    descriptions = soup.find_all('hit_def')
    tags = []
    for text in descriptions:
        for tag in text:
            clean = ['\[.*\]',
                     'isoform X[0-9]',
                     'transcript variant X[0-9]',
                     'Full=',
                     'AltName:',
                     'RecName:',
                     'isoform [A-Za-z]',
                     'partial',
                     'isoform [0-9]',
                     '[A-Z0-9]+_[A-Za-z0-9]+'
                     ]
            t = tag
            for pattern in clean: 
                t = re.sub(pattern, '', t) #remove species names
            tags.append(t) 
#     tags = list(set(tags))
    words = ''.join(tags)
    return tags, words
            
    

def main(xml_file):
    tags, words = parse_result(xml_file)
    x = plot_frequencies(words)
    y = plot_frequencies(tags)
    plt.show()


    
if __name__ == '__main__':
    xml_file = os.path.abspath(r'/mnt/home/a.murachelli/Downloads/nassos.xml')
    main(xml_file)