from rankFunc import simpleRanking, authorityRanking
import numpy as np
from netWork import netWork
import random
import time
import heapq

from collections import defaultdict


import csv

"""
RankClus算法主类

初始化参数：
data: 数据文件路径

算法运行接口pipe：

pipe(iterNum = 25, K = 15, rankT = 10, alpha = 0.95, emT = 5)

iterNum: 限制总迭代次数
K: 聚类数目
rankT：权威排名的迭代计算次数
alpha：权威排名的参数
emT：EM估计算法的迭代次数

"""
class rankClus(object):
    

    """
    """
    def __init__(self, data):
        self.network = netWork(data)
        self.pub2author, self.author2author, self.author2pub, self.publication = self.network.buildGraph()

    """
    将每个目标对象随机地赋予一个1到K的聚类标签，产生目标对象的初始聚类
    """
    def initialGroup(self, K = 15):
        initialGroup = {i : list() for i in range(K) }
        pub = list(self.publication)
        print('publication num :', len(pub))
        for i in range(K):
            initialGroup[i].append(pub.pop(random.randint(0, len(pub) - 1)))
        pub = set(pub)
        for p in pub:
            initialGroup[random.randint(0,K - 1)].append(p)
        
        return initialGroup

    """
    每次 调整/初始化 聚类后判断是否存在空的聚类
    """
    def isEmpty(self, group_list):
        result = False
        K=15
        for i in range(K):
            if len(group_list[i]) == 0:
                result = True
                break
        return result
    
    """
    EM算法，进行参数估计，得到每个聚类对于每个刊物的后验分布Pi
    输入排名分数和聚类
    """
    def EM(self, rank_pub, rank_author, pubGroup, pub2author, author2author, author2pub, emT = 5, K = 15):
        
        sum_cross = float(0)
        # 初始化后验 p_k
        p_k = np.zeros(K)
        sum_pub = 0.0
        for i in range(K):
            for pub in pubGroup[i]:
                for author in pub2author[pub]:
                    p_k[i] += pub2author[pub][author]
                    sum_pub += pub2author[pub][author]
        for i in range(K):
            p_k[i] /= float(sum_pub)

        new_p_k = np.zeros(K)
        #参数优化过程
        while emT > 0:
            emT -= 1
            condition_p_k = {}
            for pub in pub2author:
                condition_p_k[pub] = {}
                for author in pub2author[pub]:
                    condition_p_k[pub][author] = {}

                    sum_cross += pub2author[pub][author]
                    
                    sump = float(0)
                    for k in range(K):
                        tmp = rank_pub[k][pub] * rank_author[k][author] * p_k[k]
                        sump += tmp
                        condition_p_k[pub][author][k] = tmp
                    for k in range(K):
                        condition_p_k[pub][author][k] /= sump
            
            for k in range(K):
                for pub in pub2author:
                    for author in pub2author[pub]:
                        new_p_k[k] += condition_p_k[pub][author][k] * pub2author[pub][author]

            new_p_k /= sum_cross
            p_k = new_p_k
            new_p_k = np.zeros(K)
        
        #使用Bayes规则计算每个刊物属于每个聚类的概率分布： Pi(pub) = [p1, p2, ., pk]
        Pi = {}
        for pub in pub2author:
            normalization = float(0)
            Pi[pub] = np.zeros(K)
            for k in range(K):
                tmp = rank_pub[k][pub] * p_k[k]
                normalization += tmp
                Pi[pub][k] = tmp
            Pi[pub] /= normalization
        return Pi
    

    """
    用后验分布的余弦相似度来度量刊物与聚类中心的距离
    """
    def sim(self, x, y):
        num = np.sum(x * y)
        denom = np.linalg.norm(x) * np.linalg.norm(y)  
        cos = float(num) / denom #余弦值  
        return cos 

    """
    输入聚类中心与刊物，返回距离最近的聚类中心下标
    """
    def findMax(self, x, center, K = 15):
        max_sim = self.sim(x, center[0])
        it = 0
        for i in range(1, K):
            simt = self.sim(x, center[i])
            if simt > max_sim:
                it = i
                max_sim = simt
        return it

    """
    输入每个聚类对于每个刊物的后验分布Pi，对聚类进行调整，将刊物归类为
    距离它最近的聚类中心对应的类别
    """
    def adjustGroup(self, Pi, pubGroup, K = 15):
        center = {}
        newGroup = {i : list() for i in range(K) }
        for i in range(K):
            center[i] = np.zeros(K)
            for pub in pubGroup[i]:
                center[i] += Pi[pub]
            center[i] /= float(len(pubGroup[i]))
        for pub in Pi:
            newGroup[self.findMax(Pi[pub], center, K)].append(pub)
        return newGroup

    """
    算法运行接口，接受参数设置
    
    iterNum: 限制总迭代次数
    K: 聚类数目
    rankT：权威排名的迭代计算次数
    alpha：权威排名的参数
    emT：EM估计算法的迭代次数

    """
    def pipe(self, iterNum = 25, K = 15, rankT = 10, alpha = 0.95, emT = 5):
        time1 = time.time()
        group = self.initialGroup(K)
        time2 = time.time()
        print('Initial finished:', time2 - time1, 's')
        rank_pub = {}
        rank_author = {}
        
        iters = 0

        while iters < iterNum:
            time1 = time.time()
            
            print('authorityRanking start:')
            for i in range(K):
                #rank_pub[i], rank_author[i], tmp= authorityRanking(group[i], self.pub2author, self.author2author, self.author2pub, rankT, alpha)
                rank_author[i], rank_pub[i],tmp= authorityRanking(self.author2pub, self.pub2author, self.author2author,group[i],  rankT, alpha)             
            time3 = time.time()
            print('authorityRanking end:', time3 - time1)
            Pi = self.EM(rank_pub, rank_author, group, self.pub2author, self.author2author,self.author2pub, emT, K)
            time4 = time.time()
            print('EM :', time4 - time3)
            new_group = self.adjustGroup(Pi, group, K)
            del group
            group = new_group
            if self.isEmpty(group):
                group = self.initialGroup(K)
                print('Empty group !')
                iters = 0
            else:
                iters += 1
            time2 = time.time()
            print('Do clustering at epoch :', iters ,time2 - time1)
        
        for i in range(K):
            rank_author, rank_pub, rank_pub_part = authorityRanking(self.author2pub, self.pub2author, self.author2author,group[i],  rankT, alpha)
            top_10_pub = heapq.nlargest(10, rank_pub_part.items(), lambda x: x[1])
            print('Group  '+str(i))
            for confer in top_10_pub:
                print(confer[0])
            top_10_author = heapq.nlargest(10, rank_author.items(), lambda x: x[1])
            print('* * * * * * *')
            for author in top_10_author:
                print(author[0])
            print('- - - - - - - - - - - - - - - - - ')    

timestart = time.time()
test = rankClus('../data/data_resolved.txt')
test.pipe()
timeend = time.time()
print('RankClus runs:', timeend - timestart)

