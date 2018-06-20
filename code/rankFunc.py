
from collections import defaultdict


"""
排名函数提供了用于区别对象在聚类中重要性的排名分数，也作为特征提取工具用以提
高聚类的质量。这里实现了论文中提到的Simple Ranking 和 Authority Ranking

pubFamily: 聚类，publication的列表
"""

"""
Siple ranking: 简单将排名分数表达为作者或刊物出现的频率
"""

def simpleRanking(pubFamily, pub2author, author2author, author2pub):
    rank_author = defaultdict(float)
    rank_pub = defaultdict(float)
    sum_W = float(0)

    for pub in pubFamily:
        rank_pub[pub] = float(0)
        for author in pub2author[pub]:
            tmp = float(pub2author[pub][author])
            rank_author[author] = rank_author.setdefault(author, float(0)) + tmp
            sum_W += tmp
            rank_pub[pub] += tmp
    
    for pub in pubFamily:
        rank_pub[pub] = rank_pub[pub] / sum_W

    for author in author2pub:
        rank_author[author] = rank_author[author] / sum_W

    return rank_pub, rank_author 


"""
Authority ranking: 基于这样的假设：1、排名靠前的作者在排名靠前的刊物
发表了许多的论文；2、排名靠前的刊物吸引许多排名靠前的作者的论文。
作者排名和刊物排名相互迭代计算
返回在当前聚类条件下刊物的排名、作者的排名、在聚类里的刊物的排名
"""

def authorityRanking(author2pub,pub2author,author2author,group,T=10,alpha=0.95):
    rank_pub_whin = defaultdict(float)
    rank_pub, rank_author = simpleRanking(group, pub2author, author2author, author2pub)
    while T > 0:
        T -= 1
        sumConferScore = 0.0
        for confer in group:
            conferScore = 0.0
            for author in pub2author[confer]:
                conferScore += (
                    pub2author[confer][author] * rank_author[author])
            rank_pub_whin[confer] = conferScore
            sumConferScore += conferScore
        for confer in rank_pub_whin:
            rank_pub_whin[confer] = rank_pub_whin[confer] / float(
                sumConferScore) 
        last_rank_author = rank_author.copy()
        for author in rank_author:
            rank_author[author] = 0.0
        for confer in group:
            for author in pub2author[confer]:
                rank_author[author] += (
                    pub2author[confer][author] * rank_pub_whin[confer] *
                    (alpha))
        for author in rank_author:
            for co_author in author2author[author]:
                rank_author[author] += (
                    last_rank_author[co_author] *
                    (1 - alpha) * author2author[author][co_author])
        sumAuthorScore = 0.0
        for author in rank_author:
            sumAuthorScore += rank_author[author]
        for author in rank_author:
            rank_author[author] /= float(sumAuthorScore)

    sumConferScore = 0
    for confer in pub2author:
        conferScore = 0
        for author in pub2author[confer]:
            conferScore += (
                pub2author[confer][author] * rank_author[author])
        rank_pub[confer] = conferScore
        sumConferScore += conferScore
    for confer in rank_pub:
        rank_pub[confer] = rank_pub[confer] / float(sumConferScore)
    
    return rank_author, rank_pub, rank_pub_whin








