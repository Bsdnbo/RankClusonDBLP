
import csv
import numpy as np
import time
from collections import defaultdict

"""
使用领接字典的结构来存储 刊物-作者 作者-作者 作者-刊物 的信息，其中
字典的值分别表示该作者在该刊物上发表的论文数、两作者发表论文的合作次
数、该作者在该刊物上发表的论文数
"""
class netWork(object):


    def __init__(self, data):
        self.data = data
    

    """
    建立双异构信息网络，返回刊物-作者 作者-作者 作者-刊物权值
    """
    def buildGraph(self):
        data = self.data
        dataFile = open(data, 'r')
        csvData = csv.reader(dataFile)
        authors = set()
        publication = set()
        author2pub = {}
        pub2author = {}
        author2author = {}

        for line in csvData:
            publication.add(line[0])
            for i in range(len(line)):
                if i != 0 :
                    authors.add(line[i])
        
        dataFile.seek(0)



        for author in authors:
            author2pub[author] = {}
            author2author[author] = defaultdict(int)
        for pub in publication:
            pub2author[pub] = {}

        csvData = csv.reader(dataFile)
        count = 0
        for line in csvData:
            count += 1
            #if count% 10000==0:
                #print(count)
            for i in range(len(line)-1):
                pub2author[line[0]][line[i+1]] = pub2author[line[0]].setdefault(line[i+1], 0) + 1 
                author2pub[line[i+1]][line[0]] = author2pub[line[i+1]].setdefault(line[0], 0) + 1 
                for j in range(i+1,len(line)-1):
                    author2author[line[i+1]][line[j+1]] += 1
                    author2author[line[j+1]][line[i+1]] += 1
        dataFile.close()
        return pub2author, author2author, author2pub, publication
