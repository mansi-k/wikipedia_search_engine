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
    # i = 0
    good_tokens = []
    rpun = '[' + re.escape(''.join(punctuations)) + ']'
    rdig = '[' + re.escape(''.join(digits)) + ']'
    for t in tokens:
        temp = re.sub(rpun, '', t)
        temp = re.sub(rdig, '', temp)
        # for c in t:
        #     c = str(c)
        #     if (c in digits) or (not is_english(c)) or (c in punctuations):
        #         continue
        #     temp += c
        if len(temp) >= min_wordlen and is_english(temp):
            good_tokens.append(temp)
        # i += 1
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
    if ctype=='title':
        tokens = tokenize(content)
        words = process_words(tokens,use_lematizer)
    if ctype=='body':
        external_links = get_external_links(content)
        categories = get_categories(content)
    # print(words)
    return words

def get_external_links(content):
    links = ""
    lines = content.split("==External links==")
    if len(lines) > 1:
        lines = lines[1].split("\n")
        for i in range(len(lines)):
            if '* [' in lines[i] or '*[' in lines[i] or '[http' in lines[i]:
                links += lines[i]
    return links

def get_sections(content) :
    text, categories, links, info = [], [], [], []
    flgt, flgc, flgl, flgi = True, False, False, False
    print(flgt, flgc, flgl, flgi)
    lines = content.split('\n')
    i = 0
    # while i < len(lines):


def get_categories(content):  
  info, bodyText, category, links = [], [], [], []
  flagtext = 1
  lines = data.split('\n')
  # pdb.set_trace()
  for i in xrange(len(lines)):
    if '{{infobox' in lines[i]:
      flag = 0
      temp = lines[i].split('{{infobox')[1:]
      info.extend(temp)
      while True:
            if '{{' in lines[i]:
                flag += lines[i].count('{{')
            if '}}' in lines[i]:
                flag -= lines[i].count('}}')
            if flag <= 0:
                break
            i += 1
            try:
                info.append(lines[i])
            except:
                break
    elif flagtext:
      if '[[category' in lines[i] or '==external links==' in lines[i]:
        flagtext = 0
      bodyText.extend(lines[i].split())

    else:
      if "[[category" in lines[i]:
        line = data.split("[[category:")
        if len(line)>1:
            category.extend(line[1:-1])
            temp = line[-1].split(']]')
            category.append(temp[0])
    #   pdb.set_trace()

  # Process category, info and bodyText
  category = cleanup_list(category, already_lowercase=True)
  info = cleanup_list(info, already_lowercase=True)
  bodyText = cleanup_list(bodyText, already_lowercase=True)

  # Count frequencies of all the words in the respective sections
  info = create__word_to_freq_defaultdict(info)
  bodyText = create__word_to_freq_defaultdict(bodyText)
  category = create__word_to_freq_defaultdict(category)

  return info, bodyText, category

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
            temp = words_dict.get(w,0)
            if temp==0:
                temp = []
                # print(temp,type(temp),temp.append(c),c)
            temp.append(c)
            words_dict[w] = temp
        if try_till and i==try_till:
            break
        i+=1    
    # print(page_dict)
    write_partial_index()
    write_inverted_index()
    # print(words_dict)


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
    # print("mansi".encode('utf-8'))
    # start = time.time()
    # parseXML('enwiki-latest-pages-articles17.xml-p23570393p23716197')
    # data = "ma[ns)] +=ik23}h'a@am!ka,rdh_oble"
    # print(re.findall("\d+|[\w]+",data))
    # print(list(string.punctuation))
    # nltk.download('stopwords')
    # print(nltk_stopwords.words('english'))
    # print("time:",time.time()-start)


