import copy
import heapq
import random
import queue

from conM import FixedMess
from util.utils import CPM


def newAON(Humanss,Stations,Spacess,Activities):


    edge = []
    for _, activity in FixedMess.FixedMes.act_info.items():
        id = activity.id

        for toid in activity.successor:
            edge.append((id, toid))

    # print("原始边",edge)

    for humans in Humanss:
        for human in humans:
            add(edge,human.OrderOver)
    for stations in Stations:
        for station in stations:
            add(edge,station.OrderOver)

    for spaces in Spacess:
        for space in spaces:
            add(edge, space.OrderOver)

    # 这里面就包含了新的约束，但是燃气等资源约束暂时还未考虑
    return edge


def add(edge, OrderOver):
    Order = sorted(OrderOver, key = lambda x:x.es)

    for activityNum in range(len(Order)):
        frontActivity = Order[activityNum]
        if activityNum < len(Order) - 1:  # 说明这个人后面还有任务要干
                backActivity = Order[activityNum + 1]
                frontId = frontActivity.id
                backId = backActivity.id
                edge.append((frontId,backId))
# = [5,8,2,4,6]
from conM.FixedMess import FixedMes

class PSGS():
    def __init__(self,total_renew_resource,newedge):
        self.total_renew_resource = total_renew_resource
        self.newedge = newedge
        self.running= queue.PriorityQueue()
        self.already =[]
        self.waiting =queue.PriorityQueue()
        self.nowTime=0
        self.IdTime = []



    def start(self):
        self.idTime = [0.0 for i in range(FixedMess.FixedMes.Activity_num)]

        for _, activity in FixedMess.FixedMes.act_info.items():
            if activity.taskid == 1:
                self.idTime[activity.id] = 0
            elif activity.taskid == FixedMess.FixedMes.planeOrderNum:
                self.idTime[activity.id] = 0
            else:
                # idTime[activity.id] = round(FixedMess.FixedMes.getTime(activity.taskid) *100,1)
                self.idTime[activity.id] = FixedMess.FixedMes.OrderTime[activity.taskid]

    def addWaiting(self,cloneA):
        Ei_0=[]
        for key, Ei in cloneA.items():
                prece = cloneA[key].predecessor
                if prece is None:
                        continue
                Ei_number = len(prece)

                if Ei_number == 0:
                    Ei_0.append(key)
                    self.waiting.put(self.Activities[key].priority, self.Activities[key])

                    for findkey, _ in cloneA.items():
                        prece = cloneA[findkey].predecessor
                        if key in prece:
                            prece.remove(key)
                    del cloneA[key]

    def addRunning(self):
        reNewNeed = copy.deepcopy(self.total_renew_resource)

        while not self.waiting.empty():
            flag = True
            index=0
            activity = self.waiting.get()
            for type in range(len(reNewNeed)):
                reNewNeed[type] = reNewNeed[type] - activity.resourceRequestS[type]
                if reNewNeed[type] < 0:
                    index = type
                    flag = False
                    break
            if flag == False:
                self.waiting.put(activity.priority, activity)
                reNewNeed[index] = reNewNeed[index] + activity.resourceRequestS[index]
                break
            else:
                activity.es = self.nowTime
                activity.ef = self.nowTime + activity.duration
                self.running.put(activity.ef, activity)

    def run(self,newActivities):
        n = len(self.Activities)
        cloneA = copy.deepcopy(newActivities)

        while n>0:
            try:
                self.addWaiting(cloneA)
                self.addRunning()
                if not self.running.empty():
                    self.nowTime=self.running.get().ef #最先结束的先出列
                    n=n-1
                else:print("running队列为空？？？")
            except:
                print("An error occured")

        return self.nowTime



def print_hi(name):
    print(f'Hi, {name}')


if __name__ == '__main__':
    print_hi('Python')
