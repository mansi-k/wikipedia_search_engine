import xml.etree.ElementTree as et
from sortedcontainers import SortedDict
from collections import Counter
import re
import nltk
import string
from nltk.stem import WordNetLemmatizer
from Stemmer import Stemmer
from nltk.corpus import stopwords as nltk_stopwords

prefix = '{http://www.mediawiki.org/xml/export-0.10/}'
page_dict = {}
index_dir = "."
words_dict = SortedDict({})
try_till = 200
stopwords = list(nltk_stopwords.words('english'))
url_stopwords = ["www", "com", "http", "https", "net", "org", "html", "ftp", "archives", "pdf", "jpg", "jpeg", "gif", "png", "txt", "redirect"]
punctuations = list(string.punctuation) + [' ', '\t', '\n']
digits = [str(x) for x in range(10)]
max_wordlen = 12
min_wordlen = 3
use_lematizer = False

stemmer = Stemmer('english')
lemmatizer = WordNetLemmatizer()

def is_english(word):
    try:
        str(word).encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def tokenize(data):
    tokens = re.findall("\d+|[\w]+",data)  ## remove symbols by split text
    tokens = [str(w).lower() for w in tokens if len(w)>=min_wordlen and len(w)<=max_wordlen]  ## casefolding & utf encoding
    # i = 0
    good_tokens = []
    for t in tokens:
        temp = ""
        for c in t:
            c = str(c)
            if (c in digits) or (not is_english(c)):
                continue
            temp += c
        if len(temp) >= min_wordlen:
            good_tokens.append(temp)
        # i += 1
    return good_tokens

def remove_stopwords(words):
    good_words = []
    for w in words:
        if w in stopwords or w in url_stopwords:
            continue
        good_words.append(w)
    return good_words

def process_words(words,lem):
    words = remove_stopwords(words)
    words = [stemmer.stemWord(w) for w in words]
    if lem:
        words = [lemmatizer.lemmatize(w) for w in words]        
    return words

def process_text(content,ctype):
    global use_lematizer
    tokens = tokenize(content)
    words = process_words(tokens,use_lematizer)
    # print(words)
    return words



def parseXML(xmlfile):
    global page_dict, try_till
    tree = et.parse(xmlfile)
    root = tree.getroot()
    i=0
    for page in root.iter(prefix+'page'):
        # print(elem.tag, elem.attrib)
        curpage_counts = {}
        page_dict[i] = ""
        for pid in page.iter(prefix+'title'):
            page_dict[i] = pid.text
            cur_words = process_text(pid.text,'title')
            for w,c in Counter(cur_words).items():
                curpage_counts[w] = [i,0,0]
                curpage_counts[w][1] += c
        for ptxt in page.iter(prefix+'text'):
            cur_txt = ptxt.text
            cur_words = process_text(ptxt.text,'body')
            for w,c in Counter(cur_words).items():
                if w not in curpage_counts:
                    curpage_counts[w] = [i,0,0]
                curpage_counts[w][2] += c
        for w,c in curpage_counts.items():
            if w not in words_dict:
                words_dict[w] = []
            words_dict[w].append(c)
            # print(ptxt.text)
            # print("\n=====================================================================================\n\n")
        if i==try_till:
            break
        i+=1    
    # print(page_dict)
    write_partial_index()
    write_inverted_index()
    print(words_dict)


def write_partial_index():
    global page_dict, index_dir
    with open(index_dir+'/partial_index.txt', 'w') as f:
        for key in page_dict:
            f.write(str(key)+"|"+page_dict[key]+'\n')

def write_inverted_index():
    global words_dict, index_dir
    with open(index_dir+'/inverted_index.txt', 'w') as f:
        for w,cl in words_dict.items():
            cur_line = w
            for c in cl:
                cur_line = cur_line + '|' + ",".join([str(x) for x in c])
            f.write(cur_line+'\n')

def downloads():
    nltk.download('wordnet')
    nltk.download('stopwords')


if __name__ == "__main__":
    ##downloads()
    parseXML('enwiki-latest-pages-articles17.xml-p23570393p23716197')
    # data = "ma[ns)] +=ik23}h'a@am!ka,r"
    # print(re.findall("\d+|[\w]+",data))
    # print(list(string.punctuation))
    # nltk.download('stopwords')
    # print(nltk_stopwords.words('english'))


