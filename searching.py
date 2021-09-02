# import xml.etree.ElementTree as et
# from sortedcontainers import SortedDict
# from collections import Counter, defaultdict
import re
import nltk
import string
# from nltk.stem import WordNetLemmatizer
from Stemmer import Stemmer
from nltk.corpus import stopwords as nltk_stopwords
import time
import linecache
import json
import sys

# qwords_dict = SortedDict({})
stopwords = list(nltk_stopwords.words('english'))
# vocab_fname = 'inverted_index.txt'
# vocab_file = ""
total_words=3
with open('meta.txt') as f:
    total_words = int(f.readline().strip())
output_dict = {}
stemmer = Stemmer('english')
default_res = {'title':["No doc found"], 'infobox':["No doc found"], 'category':["No doc found"], 'link':["No doc found"], 'body':["No doc found"]}

def binary_search (l, r, w):
    global vocab_fname
    if r >= l:
        mid = (l + r) // 2
        # vocab_file.seek(mid)
        # cur_line = vocab_file.readline().strip()
        cur_line = linecache.getline(vocab_fname,mid).strip()
        # print("++++"+cur_line)
        cur_word = cur_line.split('|',1)[0]
        if  cur_word == w:
            return cur_line
        elif cur_word > w:
            return binary_search(l, mid-1, w)
        else:
            return binary_search(mid+1, r, w)  
    else:
        return -1

def search_word(orgword):
    global default_res
    word = orgword.lower()
    # print(word)
    if word in stopwords:
        output_dict[orgword] = default_res
        return
    word = stemmer.stemWord(word)
    # print(word)
    cur_line = binary_search(0,total_words,word)
    if cur_line == -1:
        output_dict[orgword] = default_res
        return
    cur_list = cur_line.split('|')
    if not cur_list[0] == word:
        return
    temp_dict = {'title':[], 'infobox':[], 'category':[], 'link':[], 'body':[]}
    for i in range(1,len(cur_list)):
        # print("#",cur_list[i].split(';',1))
        cur_id, cur_cnts = cur_list[i].split(';',1) 
        if 't' in cur_cnts:
            temp_dict['title'].append(cur_id)
        if 'i' in cur_cnts:
            temp_dict['infobox'].append(cur_id)
        if 'c' in cur_cnts:
            temp_dict['category'].append(cur_id)
        if 'l' in cur_cnts:
            temp_dict['link'].append(cur_id)
        if 'b' in cur_cnts:
            temp_dict['body'].append(cur_id)    
    for key in temp_dict:
        if len(temp_dict[key])==0:
            temp_dict[key] = ["No doc found"]
    output_dict[orgword] = temp_dict


if __name__ == "__main__":
    global vocab_fname, vocab_file
    if len(sys.argv)!= 3:
        print("Usage : python3 searching.py ../inverted_indexes/2020201026 query")
        sys.exit(0)
    vocab_fname = sys.argv[1]+'/index.txt'
    # vocab_file = open(vocab_fname)
    qwlist = sys.argv[2].strip().split(' ')
    # print(qwlist)
    for w in qwlist: 
        # print(w)
        if ':' in w:
            cw = w.split(':')[1]
        else:
            cw = w
        # print(cw)
        if cw:
            search_word(cw)
    print(output_dict)
    # with open('output.json', 'w') as f:
    #     f.write(json.dumps(output_dict))
