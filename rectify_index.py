import sys
import tempfile
import os
import heapq
import contextlib
import linecache 
import time
import string
import copy

file_lengths = []
output_files = []
file_readtill = []
output_dir = ""
total_words = 0

class WordCount(object):
    def __init__(self,val,fno):
        self.word, self.counts = val.split('|',1)
        self.file_no = fno
        self.word = self.word.strip()
        self.counts = self.counts.strip()
    def __lt__(self,other):
        return self.word < other.word

def create_inverted_index():
    global total_words
    myheap = []
    for fnum in range(len(file_lengths)):  ## read first line from each intermediate index file
        file_readtill.append(1)
        with open(output_dir+"/index"+str(fnum)+".txt") as curfile:
            firstline = curfile.readline()
            heapq.heappush(myheap,WordCount(firstline,fnum))
    for a in ['0']+list(string.ascii_lowercase):  ## create final index files
        outfile = open(output_dir+"/invindex_"+a+".txt",'w+')
        output_files.append(outfile)
    topmin = heapq.heappop(myheap)
    # file_readtill[topmin.file_no] += 1
    # print(len(myheap))
    while(True):
        if(len(myheap)==0):
            finished = 0
            for fnum in range(len(file_lengths)):
                if file_readtill[fnum] >= file_lengths[fnum]:
                    finished += 1
                else:
                    new_line = linecache.getline(output_dir+"/index"+str(fnum)+".txt",file_readtill[fnum]+1).strip()
                    # print("********",file_readtill[topmin.file_no],file_lengths[topmin.file_no],new_line)
                    heapq.heappush(myheap,WordCount(new_line,fnum))
                    file_readtill[fnum] += 1
            if finished == len(file_lengths):
                char1 = topmin.word[0]
                if char1.isnumeric():
                    output_files[0].write(topmin.word+"|"+topmin.counts+"\n")
                else:
                    output_files[ord(char1)-ord('a')+1].write(topmin.word+"|"+topmin.counts+"\n")
                total_words += 1
                break
        cur_element = copy.deepcopy(topmin)
        print(cur_element.file_no, cur_element.word, len(myheap))
        if file_readtill[topmin.file_no] < file_lengths[topmin.file_no]:  ## check if lines in that file are over
            new_line = linecache.getline(output_dir+"/index"+str(topmin.file_no)+".txt",file_readtill[topmin.file_no]+1).strip()
            heapq.heappush(myheap,WordCount(new_line,topmin.file_no))
            file_readtill[topmin.file_no] += 1
        topmin = heapq.heappop(myheap)
        while(topmin.word == cur_element.word) :
            cur_element.counts += '|'+topmin.counts
            if file_readtill[topmin.file_no] < file_lengths[topmin.file_no]:  ## check if lines in that file are over
                new_line = linecache.getline(output_dir+"/index"+str(topmin.file_no)+".txt",file_readtill[topmin.file_no]+1).strip()
                heapq.heappush(myheap,WordCount(new_line,topmin.file_no))
                file_readtill[topmin.file_no] += 1
            if(len(myheap)==0):
                break
            topmin = heapq.heappop(myheap)
        char1 = cur_element.word[0]
        if char1.isnumeric():
            output_files[0].write(cur_element.word+"|"+cur_element.counts+"\n")
        else:
            output_files[ord(char1)-ord('a')+1].write(cur_element.word+"|"+cur_element.counts+"\n")
        total_words += 1
    for f in output_files:
        f.close()
        
    
if __name__ == "__main__":
    output_dir = sys.argv[1]
    with open(output_dir+"/meta_index.txt") as mf:
        for line in mf:
            file_lengths.append(int(line.strip().split()[1]))
    print("a")
    create_inverted_index()
    print(total_words)
    print(file_lengths)
    print(file_readtill)
    