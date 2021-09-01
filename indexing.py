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

prefix = '{http://www.mediawiki.org/xml/export-0.10/}'
page_dict = {}
index_dir = "."
words_dict = SortedDict({})  #defaultdict(list)
try_till = None
stopwords = list(nltk_stopwords.words('english'))
url_stopwords = ["www", "com", "http", "https", "net", "org", "html", "ftp", "archives", "pdf", "jpg", "jpeg", "gif", "png", "txt", "redirect"]
punctuations = list(string.punctuation) + [' ', '_', '\t', '\n']
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
    tokens = re.findall("\d+|[\w]+",str(data))  ## remove symbols by split text
    tokens = [str(w).lower() for w in tokens if len(w)>=min_wordlen and len(w)<=max_wordlen]  ## casefolding & utf encoding
    good_tokens = []
    rpun = '[' + re.escape(''.join(punctuations)) + ']'
    rdig = '[' + re.escape(''.join(digits)) + ']'
    for t in tokens:
        temp = re.sub(rpun, '', t)
        temp = re.sub(rdig, '', temp)
        if len(temp) >= min_wordlen and is_english(temp):
            good_tokens.append(temp)
    return good_tokens

def remove_stopwords(words):
    good_words = []
    # rstop = '[' + re.escape(''.join(stopwords)) + ']'
    for w in words:
        # temp = re.sub(rpun, '', t)
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
    # if not content:
    #     return None
    if ctype=='title':
        tokens = tokenize(content)
        words = process_words(tokens,use_lematizer)
        return words
    if ctype=='body':
        text, categories, links, info = get_sections(content)
        text = tokenize(text)
        text = process_words(text,use_lematizer)
        categories = tokenize(categories)
        categories = process_words(categories,use_lematizer)
        links = tokenize(links)
        links = process_words(links,use_lematizer)
        info = tokenize(info)
        info = process_words(info,use_lematizer)
        return text, categories, links, info

# def get_external_links(content):
#     links = ""
#     lines = content.split("==External links==")
#     if len(lines) > 1:
#         lines = lines[1].split("\n")
#         for i in range(len(lines)):
#             if '* [' in lines[i] or '*[' in lines[i] or '[http' in lines[i]:
#                 links += lines[i]
#     return links

def get_sections(content) :
    text, categories, links, info = "", "", "", ""
    # flgt, flgc, flgl, flgi = True, False, False, False
    # print(flgt, flgc, flgl, flgi)
    lines = content.split('\n')
    i = 0
    n = len(lines)
    while i < n:
        # print(lines[i], type(lines[i]))
        if "[[Category" in lines[i]:
            line = lines[i].split("[[Category:")
            if len(line)>1:
                categories += " "+line[1].split(']]')[0]
        elif "{{Infobox" in lines[i]:
            # print(lines[i].split("{{Infobox")[1])
            info += " "+lines[i].split("{{Infobox")[1]
            i += 1
            while i < n and '=' in lines[i]:
                info += " "+lines[i].split('=')[1]
                i += 1
        elif "==External links==" in lines[i]:
            links += " "+lines[i].split("==External links==")[1]
            i += 1
            syms = ['* [', '*[', '*{{', '* {{', 'http']
            rsym = '[' + re.escape(''.join(syms)) + ']'
            while i < n and ('* [' in lines[i] or '*[' in lines[i] or 'http' in lines[i] or '* {{' in lines[i]):
                links += " "+lines[i]
                i += 1
        else:
            text += " "+lines[i]
        i += 1
    return text, categories, links, info

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
            if not pid.text:
                continue
            page_dict[i] = pid.text
            cur_words = process_text(pid.text,'title')
            for w,c in Counter(cur_words).items():
                # curpage_counts[w] = [i,c,0,0,0,0]  ## doc_id, title, text, cat, link, info
                curpage_counts[w] = str(i)+";t"+str(c)
        for ptxt in page.iter(prefix+'text'):
            if not ptxt.text:
                continue
            cur_txt = ptxt.text
            text, categories, links, info = process_text(ptxt.text,'body')
            ## text words
            for w,c in Counter(text).items():
                if w not in curpage_counts:
                    curpage_counts[w] = str(i)+";b"+str(c)
                else:
                    curpage_counts[w] += ";b"+str(c)
            ## category words
            for w,c in Counter(categories).items():
                if w not in curpage_counts:
                    curpage_counts[w] = str(i)+";c"+str(c)
                else:
                    curpage_counts[w] += ";c"+str(c)
            ## links words
            for w,c in Counter(links).items():
                if w not in curpage_counts:
                    curpage_counts[w] = str(i)+";l"+str(c)
                else:
                    curpage_counts[w] += ";l"+str(c)
            ## info words
            for w,c in Counter(info).items():
                if w not in curpage_counts:
                    curpage_counts[w] = str(i)+";i"+str(c)
                else:
                    curpage_counts[w] += ";i"+str(c)
        for w,c in curpage_counts.items():
            temp = words_dict.get(w,0)
            if temp==0:
                temp = []
                # print(temp,type(temp),temp.append(c),c)
            temp.append(c)
            # temp += ""
            words_dict[w] = temp
        if try_till and i==try_till:
            break
        i+=1    
    # print(page_dict)
    write_partial_index()
    write_inverted_index()
    print("total words:",len(words_dict))


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
                cur_line = cur_line + '|' + c
                # cur_line = cur_line + '|' + ",".join([str(x) for x in c])
            f.write(cur_line+'\n')

def downloads():
    nltk.download('wordnet')
    nltk.download('stopwords')


if __name__ == "__main__":
    downloads()
    # print("mansi".encode('utf-8'))
    start = time.time()
    parseXML('enwiki-latest-pages-articles17.xml-p23570393p23716197')
    # data = "ma[ns)] +=ik23}h'a@am!ka,rdh_oble"
    # print(re.findall("\d+|[\w]+",data))
    # print(list(string.punctuation))
    # nltk.download('stopwords')
    # print(nltk_stopwords.words('english'))
    print("time:",time.time()-start)
    # syms = ['* [', '*[', '*{{', '* {{', 'http']
    # rsym = '[' + re.escape(''.join(syms)) + ']'
    # print(rsym)
    # print(re.search(rsym, "man* {{si"))
    # if re.sub(rsym, '', "man*[si"):
    #     print("yes")
    # else:
    #     print("no")

