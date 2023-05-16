import GA1
import PSGS11
from BSO import bso
from draw import people
from draw.people import Draw, Draw1
from util.utils import *
from GA1 import Ga
from Mythread import myInit
from conM.FixedMess import FixedMes

from schedulePolicy.CreatCpc import PSGS, newAON


class BigSim():
    def __init__(self,dis_file,order_file):
        self.dis_file = dis_file
        self.order_file = order_file


        self.Ns = 20
        self.Nmin  = 10
        self.Nmax = 100
        self.r = 10

        self.Q = 100000  # 最大调度次数
        # self.popNum = self.pa.populationnumberson
        self.Cmax = 60

        FixedMes.lowTime = self.Cmax
        # print()
        self.Init = myInit.MyInit(self.dis_file, self.order_file)
        self.Algorithm = GA1.Ga()

    def RUN(self,i):
        FixedMes.my()
        self.Init.InitPopulation()
        self.pa = FixedMes
        self.Activities = FixedMes.act_info
        self.popNum =FixedMes.populationnumber
        self.schedulePolicy = PSGS(self.pa.total_renew_resource, self.Activities)

        print("各类型人员组成: ", self.pa.total_Huamn_resource)
        allCount = 0
        g = 0

        while allCount < self.Q:

            g += 1
            allCount += 1
            Ecmaxs = []
            Ec = []
            Prs = []
            Vs = []

            self.Ns = min(self.Nmax,self.Nmin*(1+int(g/self.r)))

            if g==1:
                self.pops = FixedMes.AllFit
            if g > 1:
                self.Algorithm.RUN(g, FixedMes.AllFit)
                self.pops = FixedMes.AllFitSon

            for pop in self.pops:
                Human = []
                Station = []
                space = []
                _,_,_,workTime,act_info = self.Init.fitness(pop, Human, Station, space)
                pop.WorkTime = workTime
                Ec.append(workTime)
                edge = newAON(Human, Station, space, act_info)

                count = self.Ns
                SUM = 0
                p=0
                while count > 0:
                        newworkTime = CPM(edge)
                        if newworkTime < self.Cmax:
                            p+=1
                        SUM += newworkTime
                        allCount += 1
                        count -= 1

                Ecmax = SUM/self.Ns
                Pr = p/self.Ns
                pop.Ecmax = Ecmax
                pop.Pr = Pr
                pop.setf()
                Ecmaxs.append(Ecmax)
                Prs.append(Pr)
                Vs.append(0)
            if g > 1:
                self.Algorithm.updata()

            if len(Ecmaxs)>0:
                print("---第{}代---cmax:{}---Ecmaxs:{}---Prs:{}---Vs:{}---".format(g, round(sum(Ec) / len(Ec), 3),round(sum(Ecmaxs) / len(Ecmaxs), 3),
                                                                         round(sum(Prs) / len(Prs), 3),
                                                                         round(sum(Vs) / len(Vs), 3)))

        sortFit = sorted(FixedMes.AllFit,key=lambda x:x.zonghe)
        pop = sortFit[0]
        Human = []
        Station = []
        space = []
        SUM = 0
        p = 0
        _, _, _, workTime, act_info = self.Init.fitness(pop, Human, Station, space)
        Draw1(Human)
        Draw1(Station)
        pop.WorkTime = workTime
        edge = newAON(Human, Station, space, act_info)
        count = 3000

        while count > 0:
            newworkTime = CPM(edge)
            if newworkTime < self.Cmax:
                p += 1
            SUM += newworkTime
            count -= 1

        Ecmax = SUM / 3000
        Pr = p / 3000
        pop.Ecmax = Ecmax
        pop.Pr = Pr

        # Draw1(Human)
        # Draw1(Station)

        print(pop.Ecmax)
        print(pop.Pr)
        print(pop.WorkTime)
        return Ecmax , Pr

if __name__ == '__main__':
    JZJsim = BigSim("C:/Users/29639/Desktop/sim/dis.csv","C:/Users/29639/Desktop/sim/dis.csv")
    Ecmaxs = []
    Prs = []
    for i in range(1):
        Ecmax, Pr = JZJsim.RUN(i)
        Ecmaxs.append(Ecmaxs)
        Prs.append(Pr)

    print(".....Emax.{}....".format(sum(Ecmaxs) / len(Ecmaxs)))
    print(".....Pr.{}....".format(sum(Prs) / len(Prs)))