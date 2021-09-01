import xml.etree.ElementTree as et
from sortedcontainers import SortedDict
from collections import Counter, defaultdict
import re
import nltk
import string
from nltk.stem import WordNetLemmatizer
from Stemmer import Stemmer
from nltk.corpus import stopwords as nltk_stopwords
import time
import linecache
import json

qwords_dict = SortedDict({})
stopwords = list(nltk_stopwords.words('english'))
vocab_fname = 'inverted_index.txt'
vocab_file = open('inv.txt')
with open('meta.txt') as f:
    total_words = int(f.readline().strip())
# total_words=3
output_dict = {}
stemmer = Stemmer('english')

def binary_search (l, r, w):
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
    word = stemmer.stemWord(orgword.lower())
    # print(word)
    if word in stopwords:
        # print("stop")
        return
    cur_line = binary_search(0,total_words,word)
    if cur_line == -1:
        # print("-1")
        return
    cur_list = cur_line.split('|')
    if not cur_list[0] == word:
        return
    temp_dict = {'title':[], 'infobox':[], 'category':[], 'link':[], 'body':[]}
    for i in range(1,len(cur_list)):
        print("#",cur_list[i].split(';',1))
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
            temp_dict[key] = ["No doc"]
    output_dict[orgword] = temp_dict


if __name__ == "__main__":
    qfile = open('query.txt', 'r')
    queries = qfile.readlines()
    # word = "World Cup"
    # if re.search(r'[t|b|c|e|i]{1,}:', word):
    #     t = list(word.split(':')[0])
    #     print(t)
    for q in queries:
        qwlist = q.strip().split(' ')
        # print(qwlist)
        for w in qwlist: 
            # print(w)
            if ':' in w:
                cw = w.split(':')[1]
            else:
                cw = w
            if cw:
                search_word(cw)
    print(output_dict)
    with open('output.json', 'w') as f:
        f.write(json.dumps(output_dict))
