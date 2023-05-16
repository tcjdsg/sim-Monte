import copy
import math
import random
from collections import defaultdict

import numpy as np

from Mythread import myInit
from chromosome.Chromo import Chromosome
from conM import FixedMess
from conM.FixedMess import FixedMes
from Mythread import *
from util import utils
from util.utils import gen_randint


class bso(object):
    def __init__(self,myinit):
        # self.Init = myInit.MyInit(dis_file,order_file)
        self.nSolutions = []
        self.pa = FixedMess.FixedMes
        self.acts = self.pa.Activity_num
        self.init = myinit

        self.DCmin=10
        self.humanNum = self.pa.humanNum
        #决定是否需要替换一个类中心的概率
        self.p_clustering = 0.2
        #决定新个体产生是由一个还是两个老个体所决定的概率
        self.p_generation = 0.8
        #决定由一个类中心还是其它普通个体来生成新个体的概率
        self.p_oneCluster = 0.4
        #决定由两个类中心还是其它两个普通个体来生成新个体的概率
        self.p_twoCluster = 0.5

        self.r_clustering = 0.0
        self.r_generation = 0.0
        self.r_oneCluster = 0.0
        self.r_twoCluster = 0.0

        self.dimension=1
        #初始化k，变异操作控制斜率的参数
        self.k = 25

        self.number_of_clusters = 2
        self.number_of_individuals = FixedMes.populationnumberson

        # 初始化权重
        self.weight1 = 0.5
        self.weight2 = 0.5
        self.clusterCenterIndex=[]
        self.cluster = []
        self.meansList = []

    def RUN(self,i,pop):
        self.Pop = pop
        # 参数初始化
        self.current_evolve_times = i

        self.clustering()
        self.newIndividualGenerate()

        FixedMes.AllFitSon = self.nSolutions
            # 挑选


    def updata(self):
        for i in range(self.number_of_individuals):
            if FixedMes.AllFitSon[i].zonghe < FixedMes.AllFit[i].zonghe:
                FixedMes.AllFit[i] = FixedMes.AllFitSon[i]

    def clustering(self):
        self.clusterCenterIndex=[]
        self.cluster=[]

        for i in range(self.number_of_clusters):
            self.clusterCenterIndex.append(-1)
            self.cluster.append([])

        for i in range(self.number_of_clusters):
            centerIndex = -1
            while True:
                flag = False
                centerIndex = np.random.randint(0,self.number_of_individuals)
                if centerIndex in self.clusterCenterIndex:
                    continue
                #确保随机挑选的类中心之间相距不会太近
                if i!=0:
                    for j in range(0,i):
                        m = i-1-j
                        if self.getdistance(self.Pop[centerIndex],self.Pop[self.clusterCenterIndex[m]])<0.001:
                            flag=True
                            break

                if flag==True:
                    continue
                #如果类中心既未重复也未距离其他类中心太近，跳出循环
                break
            self.clusterCenterIndex[i] = centerIndex

        for i in range(self.number_of_individuals):
            pop=self.Pop[i]
            label = self.getIndividualOfCluster(pop)
            self.cluster[label].append(i)

        oldVar = -1
        newVar = self.getVar()

        while abs(newVar-oldVar)>1:
            self.getCenter()
            oldVar=newVar

            for i in range(self.number_of_clusters):
                self.cluster[i]=[]

            for i in range(self.number_of_individuals):
                pop1=self.Pop[i]
                label = self.getIndividualOfCluster(pop1)
                self.cluster[label].append(i)
            newVar =  self.getVar()

    def getdistance(self,t1,t2):
        res=0.0
        for i in range(self.dimension):
            res+=(t1.zonghe - t2.zonghe)*(t1.zonghe - t2.zonghe)

        return math.sqrt(res)

    def getIndividualOfCluster(self,t):
        label =0
        mindistance = self.getdistance(t,self.Pop[self.clusterCenterIndex[0]])
        for i in range(self.number_of_clusters):
            anotherDistance = self.getdistance(t,self.Pop[self.clusterCenterIndex[i]])
            if anotherDistance<mindistance:
                mindistance =anotherDistance
                label = i

        return label

    def getVar(self):
        var=0.0
        for i in range(self.number_of_clusters):
            l = self.cluster[i]
            for j in range(len(l)):
                var +=self.getdistance(self.Pop[self.clusterCenterIndex[i]],self.Pop[l[j]])

        return var

    def getMeans(self):
        # 清空上次聚类的质心残留
        self.meansList.clear()
        for i in range(self.number_of_clusters):
            cindividual = Chromosome()
            cindividual.lChromosome = []
            clusterSize = len(self.cluster[i])
            for k in range(self.dimension):
                means = 0.0
                for j in range(clusterSize):
                    means += self.Pop[self.cluster[i][j]].f[k]
                means /= clusterSize
                cindividual.lChromosome.append(means)
            self.meansList.append(cindividual)

    #确定类中心
    #下面的实现是基于挑选类中最优个体作为类中心的
    #如果最终算法收敛效果不好，那么可以尝试一下使用质心作为类中心

    def getCenter(self):
        for i in range(self.number_of_clusters):
            bestValue = 99999999999999999
            centerIndex = -1
            l = self.cluster[i]
            for j in range(len(l)):
                curV = self.Pop[l[j]].zonghe
                if curV<bestValue:
                    bestValue =curV
                    centerIndex = l[j]

            self.clusterCenterIndex[i] = centerIndex

    def newIndividualGenerate(self):
        self.nSolutions =[]

        #    判断是否需要随机挑选出来一个类中心去替换掉
        #    这是一种发散操作
        self.r_clustering = random.random()
        if self.r_clustering<self.p_clustering:
            clusterIndex = np.random.randint(0,self.number_of_clusters)
            T = Chromosome()
            T.codes = self.init.encoder()

            replacedObjectIndex = self.clusterCenterIndex[clusterIndex]
            self.Pop[replacedObjectIndex] = T
        for i in range(self.number_of_individuals):
            newObject = Chromosome()

            self.r_generation = random.random()
            #随机挑选一个类去生成新个体
            if(self.r_generation<self.p_generation):
                self.r_oneCluster = random.random()
                clusterIndex = np.random.randint(0,self.number_of_clusters)
                #随机获取一个簇
                if self.r_oneCluster<self.p_oneCluster:
                    #根据刚刚获得的随机类索引，拿到该类的类中心
                    # 对类中心变异
                    individualIndex = self.clusterCenterIndex[clusterIndex]
                    center = self.Pop[individualIndex]

                    #根据类中心执行变异操作
                    self.mutation(center, newObject)
                    self.nSolutions.append(newObject)
                else:
                    #在随机选取的类中我们随机选取一个普通个体，以该个体为根据，加入噪声生成新个体
                    #对单个个体变异
                    clusterSize1 = len(self.cluster[clusterIndex])
                    individualIndex = self.cluster[clusterIndex][np.random.randint(0,clusterSize1)]

                    while len(self.cluster[clusterIndex])!=1 and individualIndex == self.clusterCenterIndex[clusterIndex]:
                        individualIndex = self.cluster[clusterIndex][np.random.randint(0,clusterSize1)]

                    commonObj = self.Pop[individualIndex]
                    self.mutation(commonObj, newObject)
                     #加入新个体集合
                    self.nSolutions.append(newObject)
            else:
                # indi_temp=Swap(select_ind);                                     %将该个体进行交换操作
                #         else
                self.r_twoCluster = random.random()
                # 随机选取两个类
                clusterIndex1 = np.random.randint(0,self.number_of_clusters)
                clusterIndex2 = np.random.randint(0,self.number_of_clusters)
                while clusterIndex1==clusterIndex2:
                    clusterIndex2 = np.random.randint(0, self.number_of_clusters)

                # r_twoCluster < p_twoCluster --> 由两个类中心结合，加入噪声去生成新个体
                # r_twoCluster >= p_twoCluster --> 有两个类中的普通个体交叉，加入噪声去生成新个体
                if (self.r_twoCluster < self.p_twoCluster):
                    individualIndex1 = self.clusterCenterIndex[clusterIndex1]
                    individualIndex2 = self.clusterCenterIndex[clusterIndex2]

                    father = self.Pop[individualIndex1]
                    mother = self.Pop[individualIndex2]

                    self.crossover(father, mother, newObject)

                    self.nSolutions.append(newObject)
                else:
                    clusterSize1 = len(self.cluster[clusterIndex1])
                    clusterSize2 = len(self.cluster[clusterIndex2])

                    individualIndex1 = self.cluster[clusterIndex1][np.random.randint(0,clusterSize1)]

                    individualIndex2 = self.cluster[clusterIndex2][np.random.randint(0,clusterSize2)]

                    while len(self.cluster[clusterIndex1]) != 1 and individualIndex1 == self.clusterCenterIndex[
                        clusterIndex1]:
                        individualIndex1 = self.cluster[clusterIndex1][np.random.randint(0, clusterSize1)]

                    while len(self.cluster[clusterIndex2]) != 1 and individualIndex2 == self.clusterCenterIndex[
                            clusterIndex2]:
                        individualIndex2 = self.cluster[clusterIndex2][np.random.randint(0, clusterSize2)]

                    father = self.Pop[individualIndex1]
                    mother = self.Pop[individualIndex2]

                    self.crossover(father, mother, newObject)

                    self.nSolutions.append(newObject)

    def mutation(self, pop,newObject):

        newpop = copy.deepcopy(pop)
        a = newpop.codes
        duan_code = []
        i = np.random.choice(FixedMes.jzjNumbers, 1, replace=False)
        jzj = i[0]

        poslist = []  # 记录飞机i各工序在a中的位置
        for m in range(self.acts):
            # print("Varition",a[m])
            if a[m][1] == jzj:
                poslist.append(m)
        dr = -1
        TI = [-1]
        Td = [-1]

        try:
            dr = np.random.choice([x for x in range(4, 9)], 1, replace=False)[0]
            TI = np.random.choice([x for x in range(1, FixedMes.planeOrderNum - 3 - dr)], 1, replace=False)

            Td = poslist[TI[0]:TI[0] + dr]

            x1 = Td[0]
            x2 = Td[-1]

            for gongxu in Td:
                duan_code.append(a[gongxu])

            newcode = self.daluan(duan_code)
            for q in range(dr):
                a.pop(Td[q] - q)

            number = [x1 - 1]
            for i in range(dr - 1):
                num = np.random.randint(number[-1] + 1, x2 - (dr - 2 - i))
                number.append(num)
                a.insert(num, newcode[i])

            num = number[-1]
            if (num + 1) < x2:
                number5 = np.random.randint(num + 1, x2 + 1)
                a.insert(number5, newcode[-1])
            if (num + 1) == x2:
                number5 = x2
                a.insert(number5, newcode[-1])
        except:
            print("变异发生了错误。。。。。。")
            print(poslist)
            print(dr)
            print(TI)
            print(Td)

        newObject.codes = newpop.codes


    def crossover(self, pop1, pop2, newObject):
        a = pop1.codes
        b = pop2.codes

        pos = random.randint(1, self.acts - 1)

        temp1 = copy.deepcopy(b[:pos])
        temp2 = copy.deepcopy(a[:pos])
        temp = copy.deepcopy(b[pos:])
        tempx = copy.deepcopy(a[pos:])
        for j in range(self.acts):
            for k in range(len(temp)):
                if a[j][0] == temp[k][0]:
                    temp1 = np.concatenate((temp1, [temp[k]]))
                    break
        # print(i,i+1,len(temp1))

        for j in range(self.acts):
            for k in range(len(tempx)):
                if b[j][0] == tempx[k][0]:
                    temp2 = np.concatenate((temp2, [tempx[k]]))
                    break
        # print(i,i+1,len(temp2))
        # pop1.codes = temp1.tolist()
        # # MyInit.fitness(pop1, [], [], [])
        # pop2.codes = temp2.tolist()
        # # MyInit.fitness(pop2, [], [], [])
        flag = np.random.randint(0,2)
        if flag == 0:
            newObject.codes = temp1.tolist()
        if flag == 1:
            newObject.codes = temp2.tolist()



    #子图拓扑排序

    def daluan(self, duan_code):
        newcode = []
        newActs = defaultdict(lambda: [])
        for c in duan_code:
            newActs[c[0]] = []

        for act in duan_code:
            for i in duan_code:
                if act[0] == i[0]:
                    continue
                else:

                    if len(FixedMes.act_info[i[0]].predecessor) > 0:
                        for o in FixedMes.act_info[i[0]].predecessor:
                            if act[0] == o:
                                newActs[i[0]].append(act[0])

        for a in range(len(duan_code)):
            random_Ei_0 = 0
            Ei_0 = []  # 紧前任务数为0的任务集编号
            for key, Ei in newActs.items():
                Ei_number = len(Ei)

                if Ei_number == 0:
                    Ei_0.append(key)
            random.shuffle(Ei_0)
            try:
                random_Ei_0 = Ei_0[0]
            except:
                print("duluan拓扑邻域发生了错误。。。")

            # self.taskid = taskid
            # self.belong_plane_id = jzjId
            newcode.append(
                [random_Ei_0, FixedMes.act_info[random_Ei_0].belong_plane_id, FixedMes.act_info[random_Ei_0].taskid])
            for key, Ei in newActs.items():
                prece = newActs[key]
                if random_Ei_0 in prece:
                    prece.remove(random_Ei_0)
            del newActs[random_Ei_0]
        return newcode




#
# if __name__ == '__main__':

