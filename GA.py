import copy
import math
import sys

from Mythread import myRun,myInit
from chromosome.Chromo import Chromosome
from conM import FixedMess
from conM.FixedMess import FixedMes
from draw.people import Draw_gantt
from edges.Edge import Edge
from util.utils import fast_non_dominated_sort, crowding_distance, writeTxt


class Ga(object):
    def __init__(self,dis_file,order_file):
        self.Init = myInit.MyInit(dis_file,order_file)
        self.pa = FixedMess.FixedMes
        self.run = myRun.MyRun()
        self.DCmin=10
        self.humanNum = self.pa.humanNum
    def Run(self):
        Num = self.humanNum
        dataEdge = Edge()
        dcNextAll = []
        dc=self.first(dataEdge)
        # while self.DCmin>0:
        #     self.DCmin-=1
        #     oldHuman = copy.deepcopy(FixedMes.total_Huamn_resource)
        #     Num = Num+1
        #     dcNext = [math.inf for i in range(FixedMes.Human_resource_type)]
        #     chnext = [Chromosome() for i in range(FixedMes.Human_resource_type)]
        #     dcNextIndex = [math.inf,math.inf]
        #     bestc = Chromosome()
        #
        #     diff = math.inf
        #     for k in range(FixedMes.Human_resource_type):
        #
        #         self.Init.InitPopulation()
        #         FixedMes.total_Huamn_resource[k] = oldHuman[k]+1
        #         print("各类型人员组成: ",FixedMes.total_Huamn_resource)
        #         for it in range(self.pa.ge):
        #             self.run.RUN(it)
        #             if it > 0:
        #                 print("---第{}代----Time:{}---avr:{}---move:{}---".format(it, round(self.pa.Avufit[it][0], 1),
        #                                                                     self.pa.Avufit[it][1],
        #                                                                    round(self.pa.Avufit[it][2], 1)))
        #         chromosomes = self.saveFor0Best()
        #         for ch in chromosomes:
        #             cont = ch.WorkTime*FixedMes.targetWeight[0]+ch.variance*FixedMes.targetWeight[1]+ch.movetime*FixedMes.targetWeight[2]
        #             # print(cont , )
        #             if cont< dcNext[k]:
        #                 dcNext[k] = cont
        #                 chnext[k] = ch
        #
        #         if (dcNext[k] < dcNextIndex[1]):
        #              dcNextIndex[0] = k
        #              dcNextIndex[1] = dcNext[k]
        #              bestc = copy.deepcopy(chnext[k])
        #
        #         FixedMes.total_Huamn_resource[k] = oldHuman[k]
        #
        #     FixedMes.total_Huamn_resource[int(dcNextIndex[0])]+=1
        #     dcNextAll.append(dcNext)
        #     diff = dc - int (dcNextIndex[1])
        #     dc = int (dcNextIndex[1])
        #
        #     print("边际增益----------：",diff)
        #
        #     dataEdge.edgeSum.append(dc)
        #     dataEdge.edgeUp.append(diff)
        #     dataEdge.it.append(dataEdge.it[-1] + 1)
        #     dataEdge.worktime.append(bestc.WorkTime)
        #     dataEdge.var.append(bestc.variance)
        #
        #     dataEdge.movetime.append(bestc.movetime)
        #
        #     dataEdge.gene.append(bestc.codes)
        #     dataEdge.group.append(copy.deepcopy(FixedMes.total_Huamn_resource))
        #
        # self.writeArrayList(dcNextAll,Num)
        # self.writedataEdge(dataEdge,Num)

    def first(self,dataEdge):
        self.Init.InitPopulation()
        print("各类型人员组成: ", FixedMes.total_Huamn_resource)
        for it in range(self.pa.ge):
            self.run.RUN(it)
            if it > 0:
                print("---第{}代----Time:{}---avr:{}---move:{}---".format(it, round(self.pa.Avufit[it][0], 1),
                                                                          self.pa.Avufit[it][1],
                                                                          round(self.pa.Avufit[it][2], 1)))
        chromosomes = self.saveFor0Best()
        res=0
        choose = Chromosome()
        for ch in chromosomes:
            cont = ch.WorkTime * FixedMes.targetWeight[0] + ch.variance * FixedMes.targetWeight[1] + ch.movetime * \
                   FixedMes.targetWeight[2]
            # print(cont , )
            if cont >res:
                res = cont
                choose = ch

        dataEdge.edgeSum.append(res)
        dataEdge.edgeUp.append(res)
        dataEdge.it.append(FixedMes.humanNum)
        dataEdge.worktime.append(choose.WorkTime)
        dataEdge.var.append(choose.variance)

        dataEdge.movetime.append(choose.movetime)

        dataEdge.gene.append(choose.codes)
        dataEdge.group.append(copy.deepcopy(FixedMes.total_Huamn_resource))
        return res


    def writeArrayList(self,dcNextAll , nowHuman):
        ds = "output/paretoFor0" + nowHuman + ".txt"
        aimValue = 5
        content=[]
        printContent = []

        for i in range(aimValue):
            content.append([])
            printContent.append("")

        for i in range(len(dcNextAll)-1,-1,-1):
            content[0].append(str(nowHuman))
            nowHuman-=1
            content[1].append(str(dcNextAll[i][0]))
            content[2].append(str(dcNextAll[i][1]))
            content[3].append(str(dcNextAll[i][2]))
            content[4].append(str(dcNextAll[i][3]))


        for i in range(len(content)):
            str2 = ''.join(content[i])
            printContent[i]=str2
        writeTxt(ds,printContent)

    def writedataEdge(self,dataEdge,nowHuman):
        ds = "src/output/dataEdge6aim" + nowHuman + ".txt"
        aimValue = 6
        content=[]
        printContent = []

        for i in range(aimValue):
            content.append([])
            printContent.append("")

        for i in range(len(dataEdge.it)-1,-1,-1):
            content[0].append(str(dataEdge.it[i]))
            content[1].append(str(dataEdge.edgeSum[i]))
            content[2].append(str(dataEdge.edgeUp[i]))
            content[3].append(str(dataEdge.worktime[i]))
            content[4].append(str(dataEdge.var[i]))
            content[5].append(str(dataEdge.movetime[i]))


        for i in range(len(content)):
            str2 = ''.join(content[i])
            printContent[i]=str2
        writeTxt(ds,printContent)

        ds = "output/dataEdgegroup" + nowHuman + ".txt"
        aimValue = FixedMes.Human_resource_type
        content = []
        printContent = []
        for i in range(aimValue):
            content.append([])
            printContent.append("")

        for i in range(len(dataEdge.group)):
            for j in range(aimValue):
                content[j].append(dataEdge.group[j])

        for i in range(len(content)):
            str2 = ''.join(content[i])
            printContent[i]=str2
        writeTxt(ds,printContent)

        ds = "output/dataEdgegene" + nowHuman + ".txt"
        aimValue = len(dataEdge.gene)
        content = []
        printContent = []
        for i in range(aimValue):
            content.append([])
            printContent.append("")

        for i in range(aimValue):
                content[i].append(dataEdge.gene[i])
        for i in range(len(content)):
            str2 = ''.join(content[i])
            printContent[i]=str2
        writeTxt(ds,printContent)

    # / **
    # * @ param
    # conPopulation
    # 传入染色体集合
    # * @ return 传出第0层的染色体
    # * /
    def saveFor0Best(self):
        NDset = fast_non_dominated_sort(FixedMes.AllFit)
        FixedMes.bestHumanNumberTarget.append(NDset[0])
        return NDset[0]


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
   g=Ga("C:/Users/29639/Desktop/sim/dis.csv","C:/Users/29639/Desktop/sim/dis.csv")
   g.Run()