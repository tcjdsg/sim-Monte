
# num_activities,
# num_resource_type,
# total_resource,
# activities
"""
初始化，包括加载数据
初始化编码

"""
import copy
import math
import random
from collections import defaultdict

import numpy as np

from chromosome.Chromo import Chromosome
from conM.FixedMess import FixedMes

from human.Human import Human
from read.preprocess import InitM
from schedulePolicy.simpleSSGS import simpleSSGS
from space.Space import Space
from station.Station import Station

#5/11添加优先数标志
class MyInit(object):

    def __init__(self,filenameDis,filenameJob):
        self.geneN = 0
        self.activities = {}
        self.Init = InitM(filenameDis,filenameJob)

    def InitPopulation(self):

        FixedMes.distance = self.Init.readDis()
        self.activities = self.Init.readData()
        self.geneN = FixedMes.Activity_num
        FixedMes.act_info = self.activities
        num = 0
        print("正在生成种群。。。。")
        while num < FixedMes.populationnumber:

            iter = Chromosome()
            codes = self.encoder()
            iter.setcodes(codes)
            humanState = []
            stationState = []
            spaceState= []
            orderState = defaultdict(list)
            # MyInit.fitness(iter, humanState, stationState,spaceState)

            # if(iter.WorkTime<FixedMes.lowTime):
                # print("第 " + str(num) + " 个粒子")
                # print(iter.WorkTime)
            FixedMes.AllFit[num] = copy.deepcopy(iter)
            num+=1

    def encoder(self):
        numbers = len(self.activities)
        cloneA = copy.deepcopy(self.activities)
        chromosome = []
        for a in range(numbers):
            Ei_0 = []  # 紧前任务数为0的任务集编号
            for key, Ei in cloneA.items():
                prece = cloneA[key].predecessor
                if prece is None:
                    continue
                Ei_number = len(prece)

                if Ei_number == 0:
                    Ei_0.append(key)
            random.shuffle(Ei_0)
            random_Ei_0 = Ei_0[0]

            chromosome.append([random_Ei_0,cloneA[random_Ei_0].belong_plane_id,cloneA[random_Ei_0].taskid])
            self.activities[random_Ei_0].priority = a
            for key, Ei in cloneA.items():
                prece = cloneA[key].predecessor
                if random_Ei_0 in prece:
                    prece.remove(random_Ei_0)
            del cloneA[random_Ei_0]
        return chromosome

    #按实数编码
    def encoderReal(self):
        numbers = len(self.activities)
        cloneA = copy.deepcopy(self.activities)
        chromosome = []
        right=[]
        random_Ei_0 = 0

        index=0

        for a in range(numbers):
            Ei_0 = []  # 紧前任务数为0的任务集编号
            for key, Ei in cloneA.items():
                prece = cloneA[key].predecessor
                if prece is None:
                    continue

                Ei_number = len(prece)

                if Ei_number == 0:
                    Ei_0.append(key)
            random.shuffle(Ei_0)
            random_Ei_0 = Ei_0[0]
            # self.taskid = taskid
            # self.belong_plane_id = jzjId
            start = index+random.random()
            chromosome.append([random_Ei_0,start])
            right.append([random_Ei_0,start+self.activities[random_Ei_0].duration])
            self.activities[random_Ei_0].priority = start

            index+=1
            for key, Ei in cloneA.items():
                prece = cloneA[key].predecessor
                if random_Ei_0 in prece:
                    prece.remove(random_Ei_0)
            del cloneA[random_Ei_0]
        return [chromosome,right]
    @staticmethod
    def decoder (Humans, acs):
        finishTimee = acs[FixedMes.Activity_num-1].ef
        workTime = []
        movetime=0
        for typeH in Humans:
            f=[]
            for human in typeH:
                movetime+=human.getmovetime()
                f.append(human.alreadyworkTime)

            f_var = np.var(np.array(f))
            workTime.append(f_var)
        stdev = sum(workTime)

        return finishTimee,stdev,movetime,

    '''
    :param chromosome: 
    :param iter: 
    :param Humans: 
    :param Orders: 
    :return: 
    '''

    @staticmethod
    def simplefitness(iter,Humans,Stations,Spaces):
        MyInit.initMess(Humans,Stations,Spaces)
        # initMessOrder(Orders, activities)
        simpleSSGS(FixedMes.act_info,iter.codes, Humans,Stations,Spaces,"left")
        WorkTime = FixedMes.act_info[FixedMes.Activity_num-1].ef
        return WorkTime

    @staticmethod
    def fitness(iter,Humans,Stations,Spaces):
        MyInit.initMess(Humans,Stations,Spaces)
        # initMessOrder(Orders, activities)
        newAct = MyInit.serialGenerationScheme(copy.deepcopy(FixedMes.act_info),iter.codes, Humans,Stations,Spaces,"left")
        iter.WorkTime = newAct[FixedMes.Activity_num-1].ef

        # iter.WorkTime,iter.variance,iter.movetime = MyInit.decoder(Humans,newAct)
        # Draw_gantt(Humans)
        iter.setf()
        return Humans,Stations,Spaces ,iter.WorkTime,newAct


    @staticmethod
    def initMess(Humans,Stations,Spaces):
        number = 0

        for i in range(FixedMes.Human_resource_type):
            Humans.append([])
            for j in range(FixedMes.total_Huamn_resource[i]):
                # ij都是从0开头 ,number也是

                Humans[i].append(Human([i,j,number]))
                number += 1

        number = 0

        for i in range(FixedMes.station_resource_type):
            Stations.append([])
            for j in range(FixedMes.total_station_resource[i]):
                # ij都是从0开头 ,number也是
                Stations[i].append(Station([i,j,number]))
                number += 1

        number = 0

        for i in range(FixedMes.space_resource_type):
            Spaces.append([])
            for j in range(FixedMes.total_space_resource[i]):
                # ij都是从0开头 ,number也是
                Spaces[i].append(Space(j))


    @staticmethod
    def initMessOrder(Orders,activities):

        # for i in range(jzjNums):
        #     Orders.append([])
        for key ,ac in activities.items():
            jzjN = ac.belong_plane_id
            Orders[jzjN].append(ac)

    '''
    串行调度生成机制，传入所有活动，资源限量，优先序列
    :param allTasks:
    :param resourceAvail:
    :param priority:
    :return:
    '''

    @staticmethod
    def serialGenerationScheme(allTasks, codes, humans,stations,spaces,LR):

        # 记录资源转移
        priorityToUse = codes
        resourceAvailH = FixedMes.total_Huamn_resource
        resourceAvailS = FixedMes.total_station_resource

        ps = [0]  # 局部调度计划初始化

        allTasks[0].es = 0  # 活动1的最早开始时间设为0
        allTasks[0].ef = allTasks[0].es + allTasks[0].duration

        for stage in range(0, len(priorityToUse)):
            selectTaskID = priorityToUse[stage][0]
            earliestStartTime = 0

            '''
            需要考虑移动时间
            '''
            now_pos = allTasks[selectTaskID].belong_plane_id
            dur = allTasks[selectTaskID].duration
            for preTaskID in allTasks[selectTaskID].predecessor:
                if allTasks[preTaskID].ef > earliestStartTime:
                    earliestStartTime = allTasks[preTaskID].ef

            startTime = earliestStartTime
            # 检查满足资源限量约束的时间点作为活动最早开始时间，即在这一时刻同时满足活动逻辑约束和资源限量约束
            t = startTime

            resourceSumH = np.zeros(len(resourceAvailH))
            recordH = [[] for _ in range(len(resourceAvailH))]
            resourceSumS = np.zeros(len(resourceAvailS))
            recordS = [[] for _ in range(len(resourceAvailS))]
            resourceAvailSpace = FixedMes.total_space_resource

            # 计算t时刻正在进行的活动的资源占用总量,当当前时刻大于活动开始时间小于等于活动结束时间时，说明活动在当前时刻占用资源
            while t >=startTime :

                resourceSumH = np.zeros(len(resourceAvailH))
                recordH = [[] for _ in range(len(resourceAvailH))]
                resourceSumS = np.zeros(len(resourceAvailS))
                recordS = [[] for _ in range(len(resourceAvailS))]
                resourceSumSpace = np.zeros(len(resourceAvailSpace))
                resourceSumNew = np.zeros(len(resourceAvailS))

                #第舰载机的座舱资源
                if allTasks[selectTaskID].resourceRequestSpace[now_pos-1]>0:
                      for space in spaces[now_pos-1]:
                          if (len(space.OrderOver) == 0):
                              resourceSumSpace[now_pos-1] += 1  # 该类资源可用+1
                          if (len(space.OrderOver) == 1):
                              Activity1 = space.OrderOver[0]
                              if (Activity1.ef ) <= t \
                                      or (t + dur ) <= (Activity1.es):
                                  resourceSumSpace[now_pos-1] += 1  # 该类资源可用+1

                        #遍历船员工序，找到可能可以插入的位置,如果船员没有工作，人力资源可用
                          if(len(space.OrderOver)>=2):
                              flag = False
                              for taskIndex in range(len(space.OrderOver)-1):
                                  Activity1 = space.OrderOver[taskIndex]
                                  Activity2 = space.OrderOver[taskIndex+1]
                                  if (Activity1.ef ) <= t \
                                     and (t + dur) <= (Activity2.es):
                                       flag=True
                                       resourceSumSpace[now_pos-1] += 1  # 该类资源可用+1
                                       break

                              if flag==False:
                                  Activity1 = space.OrderOver[0]
                                  Activity2 = space.OrderOver[-1]

                                  if (Activity2.ef  ) <= t \
                                          or (t + dur ) <= (Activity1.es):
                                      resourceSumSpace[now_pos-1]  += 1  # 该类资源可用+1
                                      # recordH[type].append(human)

                for type in range(len(resourceAvailH)):
                    if allTasks[selectTaskID].resourceRequestH[type]>0:
                      for human in humans[type]:

                          if (len(human.OrderOver) ==0):
                              resourceSumH[type] += 1  # 该类资源可用+1
                              recordH[type].append(human)

                          if (len(human.OrderOver) ==1):
                              Activity1 = human.OrderOver[0]
                              from_pos = Activity1.belong_plane_id
                              to_pos = Activity1.belong_plane_id
                              movetime1 = 0
                              movetime2 = 0

                              if (Activity1.ef  + round(movetime1,1)) <= t \
                                      or (t + dur) <= (Activity1.es - round(movetime2,1)):
                                  resourceSumH[type] += 1  # 该类资源可用+1
                                  recordH[type].append(human)

                        #遍历船员工序，找到可能可以插入的位置,如果船员没有工作，人力资源可用
                          if(len(human.OrderOver)>=2):
                              flag = False
                              for taskIndex in range(len(human.OrderOver)-1):
                                  Activity1 = human.OrderOver[taskIndex]
                                  Activity2 = human.OrderOver[taskIndex+1]

                                  from_pos = Activity1.belong_plane_id
                                  to_pos = Activity2.belong_plane_id
                                  movetime1 = 0
                                  movetime2 = 0

                                  if (Activity1.ef +  round(movetime1,1)) <= t \
                                     and (t + dur) <= (Activity2.es - round(movetime2,1)):
                                       flag=True
                                       resourceSumH[type] += 1  # 该类资源可用+1
                                       recordH[type].append(human)
                                       break

                              if flag==False:
                                  Activity1 = human.OrderOver[0]
                                  Activity2 = human.OrderOver[-1]
                                  from_pos = Activity2.belong_plane_id
                                  to_pos = Activity1.belong_plane_id
                                  movetime2 = 0
                                  movetime1 = 0

                                  if (Activity2.ef  + round(movetime2,1)) <= t \
                                          or (t + dur ) <= (Activity1.es - round(movetime1,1)):
                                      resourceSumH[type] += 1  # 该类资源可用+1
                                      recordH[type].append(human)

                renewFlag = True
                for type in range(len(resourceAvailS)):
                    if allTasks[selectTaskID].resourceRequestS[type] > 0:
                        renewFlag = True
                        for station in stations[type]:
                            # 找到当前所有正在工作的设备，计算资源占用数
                            for taskIndex in range(len(station.OrderOver)):
                                renewActivity = station.OrderOver[taskIndex]

                                # 说明此刻油料等资源在使用
                                if t > renewActivity.es and t < renewActivity.ef:
                                    resourceSumNew[type] += 1  # 该类资源占用+1
                                    break

                        if resourceSumNew[type] >= FixedMes.total_renew_resource[type]:
                            renewFlag = False  # 满了
                            break #这个时间不可用

                for type in range(len(resourceAvailS)):
                    if allTasks[selectTaskID].resourceRequestS[type]>0:
                      for station in stations[type]:
                          # 舰载机在这个加油站的覆盖范围内：
                          if now_pos in FixedMes.constraintS_JZJ[type][station.zunumber]:
                              if (len(station.OrderOver) == 0):
                                  resourceSumS[type] += 1  # 该类资源可用+1
                                  recordS[type].append(station)

                              if (len(station.OrderOver) == 1):
                                  Activity1 = station.OrderOver[0]

                                  if (Activity1.ef ) <= t \
                                          or (t + dur ) <= (Activity1.es):
                                      resourceSumS[type] += 1  # 该类资源可用+1
                                      recordS[type].append(station)

                              if (len(station.OrderOver) >= 2):
                                  flag = False
                                  for taskIndex in range(len(station.OrderOver)-1):
                                      Activity1 = station.OrderOver[taskIndex]
                                      Activity2 = station.OrderOver[taskIndex+1]

                                      if (Activity1.ef ) <= t \
                                        and (t + dur ) <= (Activity2.es):
                                        resourceSumS[type] += 1  # 该类资源可用+1
                                        recordS[type].append(station)
                                        flag = True

                                  if flag == False:
                                      Activity1 = station.OrderOver[-1]
                                      Activity2 = station.OrderOver[0]

                                      if (Activity1.ef ) <= t or (t +dur) <= Activity2.es:
                                          resourceSumS[type] += 1
                                          recordS[type].append(station)


                # 若资源不够，则向后推一个单位时间
                if (renewFlag == False) or ((resourceSumSpace < allTasks[selectTaskID].resourceRequestSpace).any()) or (resourceSumH < allTasks[selectTaskID].resourceRequestH).any() or (resourceSumS < allTasks[selectTaskID].resourceRequestS).any() :
                        t += 0.1
                else:
                    break
            # 若符合资源限量则将当前活动开始时间安排在这一时刻
            allTasks[selectTaskID].es = t
            allTasks[selectTaskID].ef = t + dur

            for type in range(len(resourceAvailH)):

                need = allTasks[selectTaskID].resourceRequestH[type]
                while need > 0:
                    alreadyWorkTime = 9999999999999
                    index = 0
                    for nowHuman in recordH[type]:
                        if nowHuman.alreadyworkTime < alreadyWorkTime:
                            alreadyWorkTime = nowHuman.alreadyworkTime
                            index = nowHuman.zunumber

                    for idn in range(len(recordH[type])):
                        if recordH[type][idn].zunumber == index:
                            recordH[type].remove(recordH[type][idn])
                            break
                    # 更新人员
                    humans[type][index].update(allTasks[selectTaskID])
                    allTasks[selectTaskID].HumanNums.append([type, index])
                    # allTasks[selectTaskID].HumanNums.append(humans[type][index].number)
                    need -= 1

                # 分配 根据 record 分配
            for type in range(len(resourceAvailS)):

                need = allTasks[selectTaskID].resourceRequestS[type]
                if need > 0:
                    alreadyWorkTime = math.inf
                    index = 0
                    for nowStaion in recordS[type]:
                        if nowStaion.alreadyworkTime < alreadyWorkTime:
                            alreadyWorkTime = nowStaion.alreadyworkTime
                            index = nowStaion.zunumber

                    # 更新
                    stations[type][index].update(allTasks[selectTaskID])
                    allTasks[selectTaskID].SheiBei.append([type, index])
                    # allTasks[selectTaskID].SNums.append(stations[type][index].number)
                    need -= 1

            need = allTasks[selectTaskID].resourceRequestSpace[now_pos-1]
            if need > 0:
                index = 0
                spaces[now_pos-1][index].update(allTasks[selectTaskID])
                # allTasks[selectTaskID].HumanNums.append(humans[type][index].number)
                need -= 1

            # 局部调度计划ps
            ps.append(selectTaskID)

        return allTasks

    @staticmethod
    def serialGenerationScheme1(allTasks, codes, humans,stations,spaces,LR):

        w=0.00000000001
        code = codes
        #
        # if LR == "left":
        #     code = sorted(codes[0], key=lambda x: x[1])
        # else:
        #     code = sorted(codes[1], key=lambda x: -x[1])
        #     maxtime = allTasks[code[0][0]].ef
        #     for act in allTasks.keys():
        #         tmp1 = allTasks[act].es
        #         tmp2 = allTasks[act].ef
        #         tmp3 = copy.deepcopy(allTasks[act].predecessor)
        #         tmp4 = copy.deepcopy(allTasks[act].successor)
        #         allTasks[act].es = (0 - tmp2) + maxtime
        #         allTasks[act].ef = (0 - tmp1) + maxtime
        #         allTasks[act].predecessor = tmp4
        #         allTasks[act].successor = tmp3

        # 记录资源转移
        resourceAvailH = FixedMes.total_Huamn_resource
        resourceAvailS = FixedMes.total_station_resource
        resourceAvailSpace = FixedMes.total_space_resource

        ps = [0]  # 局部调度计划初始化

        allTasks[0].es = 0  # 活动1的最早开始时间设为0
        allTasks[0].ef = allTasks[0].es + allTasks[0].duration

        for stage in range(0, len(code)):
            selectTaskID = code[stage][0]
            earliestStartTime = 0

            resourceRequest = allTasks[selectTaskID].resourceRequestSpace + allTasks[selectTaskID].resourceRequestH + \
                              allTasks[selectTaskID].resourceRequestS
            flag = True
            for i in range(len(resourceRequest)):
                if i > 0:
                    flag = False
                    break
            if flag == True:
                continue
            '''
            需要考虑移动时间
            '''
            now_pos = allTasks[selectTaskID].belong_plane_id
            dur = allTasks[selectTaskID].duration
            for preTaskID in allTasks[selectTaskID].predecessor:
                if allTasks[preTaskID].ef > earliestStartTime:
                    earliestStartTime = allTasks[preTaskID].ef
            startTime = earliestStartTime
            # 检查满足资源限量约束的时间点作为活动最早开始时间，即在这一时刻同时满足活动逻辑约束和资源限量约束
            t = startTime
            recordH = [[] for _ in range(len(resourceAvailH))]
            recordS = [[] for _ in range(len(resourceAvailS))]
            recordSpace = [[] for _ in range(len(resourceAvailSpace))]

            # 计算t时刻正在进行的活动的资源占用总量,当当前时刻大于活动开始时间小于等于活动结束时间时，说明活动在当前时刻占用资源
            while t >= startTime :

                resourceSumH = np.zeros(len(resourceAvailH))
                recordH = [[] for _ in range(len(resourceAvailH))]

                resourceSumS = np.zeros(len(resourceAvailS))
                recordS = [[] for _ in range(len(resourceAvailS))]

                resourceSumNew = np.zeros(len(resourceAvailS))

                resourceSumSpace = np.zeros(len(resourceAvailSpace))
                recordSpace = [[] for _ in range(len(resourceAvailSpace))]

                # #第舰载机的座舱资源
                # if allTasks[selectTaskID].resourceRequestSpace[now_pos-1]>0:
                #       for space in spaces[now_pos-1]:
                #
                #           if (len(space.OrderOver) == 0):
                #               resourceSumSpace[now_pos-1] += 1  # 该类资源可用+1
                #
                #           if (len(space.OrderOver) == 1):
                #               Activity1 = space.OrderOver[0]
                #
                #               if (Activity1.ef ) <= t \
                #                       or (t + dur ) <= (Activity1.es):
                #                   resourceSumSpace[now_pos-1] += 1  # 该类资源可用+1
                #
                #
                #         #遍历船员工序，找到可能可以插入的位置,如果船员没有工作，人力资源可用
                #           if(len(space.OrderOver)>=2):
                #               flag = False
                #               for taskIndex in range(len(space.OrderOver)-1):
                #                   Activity1 = space.OrderOver[taskIndex]
                #                   Activity2 = space.OrderOver[taskIndex+1]
                #
                #                   if (Activity1.ef ) <= t \
                #                      and (t + dur) <= (Activity2.es):
                #                        flag=True
                #                        resourceSumSpace[now_pos-1] += 1  # 该类资源可用+1
                #
                #                        break
                #
                #               if flag==False:
                #                   Activity1 = space.OrderOver[0]
                #                   Activity2 = space.OrderOver[-1]
                #
                #                   if (Activity2.ef  ) <= t \
                #                           or (t + dur ) <= (Activity1.es):
                #                       resourceSumSpace[now_pos-1]  += 1  # 该类资源可用+1
                #                       # recordH[type].append(human)


                for type in range(len(resourceAvailH)):
                    if allTasks[selectTaskID].resourceRequestH[type]>0:
                      for human in humans[type]:
                          if (len(human.OrderOver) ==0):
                              resourceSumH[type] += 1  # 该类资源可用+1
                              recordH[type].append(human)

                          if (len(human.OrderOver) ==1):
                              Activity1 = human.OrderOver[0]
                              from_pos = Activity1.belong_plane_id
                              to_pos = Activity1.belong_plane_id
                              # movetime1 = 0 if from_pos == 0 else FixedMes.distance[from_pos][
                              #                                         now_pos] / FixedMes.human_walk_speed
                              # movetime2 = 0 if to_pos == 0 else FixedMes.distance[to_pos][
                              #                                       now_pos] / FixedMes.human_walk_speed

                              if (Activity1.ef  ) <= t \
                                      or (t + dur ) <= (Activity1.es ):
                                  resourceSumH[type] += 1  # 该类资源可用+1
                                  recordH[type].append(human)

                        #遍历船员工序，找到可能可以插入的位置,如果船员没有工作，人力资源可用
                          if(len(human.OrderOver)>=2):
                              flag = False
                              for taskIndex in range(len(human.OrderOver)-1):
                                  Activity1 = human.OrderOver[taskIndex]
                                  Activity2 = human.OrderOver[taskIndex+1]

                                  from_pos = Activity1.belong_plane_id
                                  to_pos = Activity2.belong_plane_id
                                  # movetime1 = 0 if from_pos==0 else FixedMes.distance[from_pos][now_pos]/FixedMes.human_walk_speed
                                  # movetime2 = 0 if to_pos==0 else FixedMes.distance[to_pos][now_pos]/FixedMes.human_walk_speed

                                  if (Activity1.ef  ) <= t \
                                     and (t + dur ) <= (Activity2.es ):
                                       flag=True
                                       resourceSumH[type] += 1  # 该类资源可用+1
                                       recordH[type].append(human)
                                       break

                              if flag==False:
                                  Activity1 = human.OrderOver[0]
                                  Activity2 = human.OrderOver[-1]
                                  from_pos = Activity2.belong_plane_id
                                  to_pos = Activity1.belong_plane_id
                                  # movetime2 = 0 if from_pos == 0 else FixedMes.distance[from_pos][
                                  #                                         now_pos] / FixedMes.human_walk_speed
                                  # movetime1 = 0 if to_pos == 0 else FixedMes.distance[to_pos][
                                  #                                       now_pos] / FixedMes.human_walk_speed
                                  #
                                  if (Activity2.ef ) <= t \
                                          or (t + dur ) <= (Activity1.es ):
                                      resourceSumH[type] += 1  # 该类资源可用+1
                                      recordH[type].append(human)

                renewFlag = True
                for type in range(len(resourceAvailS)):
                    if allTasks[selectTaskID].resourceRequestS[type]>0:
                        renewFlag = True
                        for station in stations[type]:
                             # 找到当前所有正在工作的设备，计算资源占用数
                             for taskIndex in range(len(station.OrderOver)):
                                 renewActivity = station.OrderOver[taskIndex]

                                 # 说明此刻油料等资源在使用
                                 if t > renewActivity.es and t < renewActivity.ef:
                                     resourceSumNew[type] += 1 # 该类资源占用+1
                                     break

                        if resourceSumNew[type]==FixedMes.total_renew_resource[type]:
                            renewFlag = False #满了
                        if renewFlag==True:
                            for station in stations[type]:
                          # 舰载机在这个加油站的覆盖范围内：
                                if now_pos in FixedMes.constraintS_JZJ[type][station.zunumber]:

                                    if (len(station.OrderOver) == 0):
                                        resourceSumS[type] += 1  # 该类资源可用+1
                                        recordS[type].append(station)

                                    if (len(station.OrderOver) == 1):
                                        Activity1 = station.OrderOver[0]

                                        if (Activity1.ef ) <= t \
                                          or (t + dur ) <= (Activity1.es):
                                            resourceSumS[type] += 1  # 该类资源可用+1
                                            recordS[type].append(station)

                                    if (len(station.OrderOver) >= 2):
                                        flag = False
                                        for taskIndex in range(len(station.OrderOver)-1):
                                            Activity1 = station.OrderOver[taskIndex]
                                            Activity2 = station.OrderOver[taskIndex+1]

                                            if (Activity1.ef ) <= t \
                                        and (t + dur ) <= (Activity2.es):
                                                resourceSumS[type] += 1  # 该类资源可用+1
                                                recordS[type].append(station)
                                                flag = True
                                        if flag == False:
                                            Activity1 = station.OrderOver[-1]
                                            Activity2 = station.OrderOver[0]

                                            if (Activity1.ef ) <= t or (t + dur) <= Activity2.es:
                                                resourceSumS[type] += 1
                                                recordS[type].append(station)



                # 若资源不够，则向后推一个单位时间
                if renewFlag==False or ((resourceSumSpace < allTasks[selectTaskID].resourceRequestSpace).any()) or (resourceSumH < allTasks[selectTaskID].resourceRequestH).any() or (resourceSumS < allTasks[selectTaskID].resourceRequestS).any() :
                        t = t+1
                else:
                    break
            # 若符合资源限量则将当前活动开始时间安排在这一时刻
            allTasks[selectTaskID].es = round(t,1)
            allTasks[selectTaskID].ef = t + dur

            # 人员分配 根据 record 分配
            for type in range(len(resourceAvailH)):

                need = allTasks[selectTaskID].resourceRequestH[type]
                while need > 0:
                    alreadyWorkTime = math.inf
                    index = 0
                    for nowHuman in recordH[type]:
                        if nowHuman.alreadyworkTime < alreadyWorkTime:
                            alreadyWorkTime = nowHuman.alreadyworkTime
                            index = nowHuman.zunumber

                    for idn in range(len(recordH[type])):
                        if recordH[type][idn].zunumber == index:
                            recordH[type].remove(recordH[type][idn])
                            break
                    # 更新人员
                    humans[type][index].update(allTasks[selectTaskID])
                    allTasks[selectTaskID].HumanNums.append([type,index])
                    # allTasks[selectTaskID].HumanNums.append(humans[type][index].number)
                    need -= 1

            # 分配 根据 record 分配
            for type in range(len(resourceAvailS)):

                need = allTasks[selectTaskID].resourceRequestS[type]
                if need > 0:
                    alreadyWorkTime = math.inf
                    index = 0
                    for nowStaion in recordS[type]:
                        if nowStaion.alreadyworkTime < alreadyWorkTime:
                            alreadyWorkTime = nowStaion.alreadyworkTime
                            index = nowStaion.zunumber

                    # 更新
                    stations[type][index].update(allTasks[selectTaskID])
                    allTasks[selectTaskID].SheiBei.append([type, index])
                    # allTasks[selectTaskID].SNums.append(stations[type][index].number)
                    need -= 1



            need = allTasks[selectTaskID].resourceRequestSpace[now_pos-1]
            if need > 0:

                    index = 0

                    spaces[now_pos-1][index].update(allTasks[selectTaskID])
                    # allTasks[selectTaskID].HumanNums.append(humans[type][index].number)
                    need -= 1

            # 局部调度计划ps
            ps.append(selectTaskID)
            allTasks[selectTaskID].priority = allTasks[selectTaskID].es

        ACTS = copy.deepcopy(allTasks)
        ACTS = sorted(ACTS.items(), key=lambda x: -x[1].ef)
        if LR != "left":
                maxtime = ACTS[0][1].ef
                for act in allTasks.keys():
                    tmp1 = allTasks[act].es
                    tmp2 = allTasks[act].ef
                    tmp3 = copy.deepcopy(allTasks[act].predecessor)
                    tmp4 = copy.deepcopy(allTasks[act].successor)
                    allTasks[act].es = (0 - tmp2) + maxtime
                    allTasks[act].ef = (0 - tmp1) + maxtime
                    allTasks[act].predecessor = tmp4
                    allTasks[act].successor = tmp3


        return allTasks

    # @staticmethod
    # def parellGenerationScheme(allTasks, codes, humans, stations, spaces, LR):
    #
    #     code = codes
    #     #
    #     # if LR == "left":
    #     #     code = sorted(codes[0], key=lambda x: x[1])
    #     # else:
    #     #     code = sorted(codes[1], key=lambda x: -x[1])
    #     #     maxtime = allTasks[code[0][0]].ef
    #     #     for act in allTasks.keys():
    #     #         tmp1 = allTasks[act].es
    #     #         tmp2 = allTasks[act].ef
    #     #         tmp3 = copy.deepcopy(allTasks[act].predecessor)
    #     #         tmp4 = copy.deepcopy(allTasks[act].successor)
    #     #         allTasks[act].es = (0 - tmp2) + maxtime
    #     #         allTasks[act].ef = (0 - tmp1) + maxtime
    #     #         allTasks[act].predecessor = tmp4
    #     #         allTasks[act].successor = tmp3
    #
    #     # 记录资源转移
    #     resourceAvailH = FixedMes.total_Huamn_resource
    #     resourceAvailS = FixedMes.total_station_resource
    #     resourceAvailSpace = FixedMes.total_space_resource
    #
    #     ps = [0]  # 局部调度计划初始化
    #     en = [codes[i][0] for i in range(FixedMes.Activity_num)] # 等待完成
    #
    #     allTasks[0].es = 0  # 活动1的最早开始时间设为0
    #     allTasks[0].ef = allTasks[0].es + allTasks[0].duration
    #
    #     manzu = []
    #
    #
    #
    #     while len(en)>0:
    #         time = 0
    #         manzu = checkCondition(ps,en)
    #         #满足资源限制和优先级的工序里面挑
    #
    #
    #
    #
    #
    #         '''
    #         需要考虑移动时间
    #         '''
    #         now_pos = allTasks[selectTaskID].belong_plane_id
    #         dur = allTasks[selectTaskID].duration
    #         for preTaskID in allTasks[selectTaskID].predecessor:
    #             if allTasks[preTaskID].ef > earliestStartTime:
    #                 earliestStartTime = allTasks[preTaskID].ef
    #
    #         startTime = earliestStartTime
    #         # 检查满足资源限量约束的时间点作为活动最早开始时间，即在这一时刻同时满足活动逻辑约束和资源限量约束
    #         t = startTime
    #         recordH = [[] for _ in range(len(resourceAvailH))]
    #
    #         recordS = [[] for _ in range(len(resourceAvailS))]
    #         recordSpace = [[] for _ in range(len(resourceAvailSpace))]
    #
    #         # 计算t时刻正在进行的活动的资源占用总量,当当前时刻大于活动开始时间小于等于活动结束时间时，说明活动在当前时刻占用资源
    #         while t >= startTime:
    #
    #             resourceSumH = np.zeros(len(resourceAvailH))
    #             recordH = [[] for _ in range(len(resourceAvailH))]
    #
    #             resourceSumS = np.zeros(len(resourceAvailS))
    #             recordS = [[] for _ in range(len(resourceAvailS))]
    #
    #             resourceSumNew = np.zeros(len(resourceAvailS))
    #
    #             resourceSumSpace = np.zeros(len(resourceAvailSpace))
    #             recordSpace = [[] for _ in range(len(resourceAvailSpace))]
    #
    #             # 第舰载机的座舱资源
    #             if allTasks[selectTaskID].resourceRequestSpace[now_pos - 1] > 0:
    #                 for space in spaces[now_pos - 1]:
    #
    #                     if (len(space.OrderOver) == 0):
    #                         resourceSumSpace[now_pos - 1] += 1  # 该类资源可用+1
    #
    #                     if (len(space.OrderOver) == 1):
    #                         Activity1 = space.OrderOver[0]
    #
    #                         if (Activity1.ef) <= t \
    #                                 or (t + dur) <= (Activity1.es):
    #                             resourceSumSpace[now_pos - 1] += 1  # 该类资源可用+1
    #
    #                     # 遍历船员工序，找到可能可以插入的位置,如果船员没有工作，人力资源可用
    #                     if (len(space.OrderOver) >= 2):
    #                         flag = False
    #                         for taskIndex in range(len(space.OrderOver) - 1):
    #                             Activity1 = space.OrderOver[taskIndex]
    #                             Activity2 = space.OrderOver[taskIndex + 1]
    #
    #                             if (Activity1.ef) <= t \
    #                                     and (t + dur) <= (Activity2.es):
    #                                 flag = True
    #                                 resourceSumSpace[now_pos - 1] += 1  # 该类资源可用+1
    #
    #                                 break
    #
    #                         if flag == False:
    #                             Activity1 = space.OrderOver[0]
    #                             Activity2 = space.OrderOver[-1]
    #
    #                             if (Activity2.ef) <= t \
    #                                     or (t + dur) <= (Activity1.es):
    #                                 resourceSumSpace[now_pos - 1] += 1  # 该类资源可用+1
    #                                 # recordH[type].append(human)
    #
    #             for type in range(len(resourceAvailH)):
    #                 if allTasks[selectTaskID].resourceRequestH[type] > 0:
    #                     for human in humans[type]:
    #                         if (len(human.OrderOver) == 0):
    #                             resourceSumH[type] += 1  # 该类资源可用+1
    #                             recordH[type].append(human)
    #
    #                         if (len(human.OrderOver) == 1):
    #                             Activity1 = human.OrderOver[0]
    #                             from_pos = Activity1.belong_plane_id
    #                             to_pos = Activity1.belong_plane_id
    #                             # movetime1 = 0 if from_pos == 0 else FixedMes.distance[from_pos][
    #                             #                                         now_pos] / FixedMes.human_walk_speed
    #                             # movetime2 = 0 if to_pos == 0 else FixedMes.distance[to_pos][
    #                             #                                       now_pos] / FixedMes.human_walk_speed
    #
    #                             if (Activity1.ef) <= t \
    #                                     or (t + dur) <= (Activity1.es):
    #                                 resourceSumH[type] += 1  # 该类资源可用+1
    #                                 recordH[type].append(human)
    #
    #                         # 遍历船员工序，找到可能可以插入的位置,如果船员没有工作，人力资源可用
    #                         if (len(human.OrderOver) >= 2):
    #                             flag = False
    #                             for taskIndex in range(len(human.OrderOver) - 1):
    #                                 Activity1 = human.OrderOver[taskIndex]
    #                                 Activity2 = human.OrderOver[taskIndex + 1]
    #
    #                                 from_pos = Activity1.belong_plane_id
    #                                 to_pos = Activity2.belong_plane_id
    #                                 # movetime1 = 0 if from_pos==0 else FixedMes.distance[from_pos][now_pos]/FixedMes.human_walk_speed
    #                                 # movetime2 = 0 if to_pos==0 else FixedMes.distance[to_pos][now_pos]/FixedMes.human_walk_speed
    #
    #                                 if (Activity1.ef) <= t \
    #                                         and (t + dur) <= (Activity2.es):
    #                                     flag = True
    #                                     resourceSumH[type] += 1  # 该类资源可用+1
    #                                     recordH[type].append(human)
    #                                     break
    #
    #                             if flag == False:
    #                                 Activity1 = human.OrderOver[0]
    #                                 Activity2 = human.OrderOver[-1]
    #                                 from_pos = Activity2.belong_plane_id
    #                                 to_pos = Activity1.belong_plane_id
    #                                 # movetime2 = 0 if from_pos == 0 else FixedMes.distance[from_pos][
    #                                 #                                         now_pos] / FixedMes.human_walk_speed
    #                                 # movetime1 = 0 if to_pos == 0 else FixedMes.distance[to_pos][
    #                                 #                                       now_pos] / FixedMes.human_walk_speed
    #                                 #
    #                                 if (Activity2.ef) <= t \
    #                                         or (t + dur) <= (Activity1.es):
    #                                     resourceSumH[type] += 1  # 该类资源可用+1
    #                                     recordH[type].append(human)
    #
    #             renewFlag = True
    #             for type in range(len(resourceAvailS)):
    #                 if allTasks[selectTaskID].resourceRequestS[type] > 0:
    #                     renewFlag = True
    #                     #
    #                     # # for station in stations[type]:
    #                     # #     # 找到当前所有正在工作的设备，计算资源占用数
    #                     # #     for taskIndex in range(len(station.OrderOver)):
    #                     # #         renewActivity = station.OrderOver[taskIndex]
    #                     # #
    #                     # #         #说明此刻 油料等资源在使用
    #                     # #         if t > renewActivity.es and t < renewActivity.ef:
    #                     # #             resourceSumNew[type] += 1 # 该类资源可用+1
    #                     # #             break
    #                     #
    #                     # if resourceSumNew[type]==FixedMes.total_renew_resource[type]:
    #                     #     renewFlag = False #满了
    #                     if renewFlag == True:
    #                         for station in stations[type]:
    #                             # 舰载机在这个加油站的覆盖范围内：
    #                             if now_pos in FixedMes.constraintS_JZJ[type][station.zunumber]:
    #
    #                                 if (len(station.OrderOver) == 0):
    #                                     resourceSumS[type] += 1  # 该类资源可用+1
    #                                     recordS[type].append(station)
    #
    #                                 if (len(station.OrderOver) == 1):
    #                                     Activity1 = station.OrderOver[0]
    #
    #                                     if (Activity1.ef) <= t \
    #                                             or (t + dur) <= (Activity1.es):
    #                                         resourceSumS[type] += 1  # 该类资源可用+1
    #                                         recordS[type].append(station)
    #
    #                                 if (len(station.OrderOver) >= 2):
    #                                     flag = False
    #                                     for taskIndex in range(len(station.OrderOver) - 1):
    #                                         Activity1 = station.OrderOver[taskIndex]
    #                                         Activity2 = station.OrderOver[taskIndex + 1]
    #
    #                                         if (Activity1.ef) <= t \
    #                                                 and (t + dur) <= (Activity2.es):
    #                                             resourceSumS[type] += 1  # 该类资源可用+1
    #                                             recordS[type].append(station)
    #                                             flag = True
    #                                     if flag == False:
    #                                         Activity1 = station.OrderOver[-1]
    #                                         Activity2 = station.OrderOver[0]
    #
    #                                         if (Activity1.ef) <= t or (t + dur) <= Activity2.es:
    #                                             resourceSumS[type] += 1
    #                                             recordS[type].append(station)
    #
    #             # 若资源不够，则向后推一个单位时间
    #             if renewFlag == False or ((resourceSumSpace < allTasks[selectTaskID].resourceRequestSpace).any()) or (
    #                     resourceSumH < allTasks[selectTaskID].resourceRequestH).any() or (
    #                     resourceSumS < allTasks[selectTaskID].resourceRequestS).any():
    #                 t = round(t + 0.1, 1)
    #             else:
    #                 break
    #         # 若符合资源限量则将当前活动开始时间安排在这一时刻
    #         allTasks[selectTaskID].es = round(t, 1)
    #         allTasks[selectTaskID].ef = t + dur
    #
    #         # 人员分配 根据 record 分配
    #         for type in range(len(resourceAvailH)):
    #
    #             need = allTasks[selectTaskID].resourceRequestH[type]
    #             while need > 0:
    #                 alreadyWorkTime = math.inf
    #                 index = 0
    #                 for nowHuman in recordH[type]:
    #                     if nowHuman.alreadyworkTime < alreadyWorkTime:
    #                         alreadyWorkTime = nowHuman.alreadyworkTime
    #                         index = nowHuman.zunumber
    #
    #                 for idn in range(len(recordH[type])):
    #                     if recordH[type][idn].zunumber == index:
    #                         recordH[type].remove(recordH[type][idn])
    #                         break
    #
    #                 # 更新人员
    #                 humans[type][index].update(allTasks[selectTaskID])
    #                 allTasks[selectTaskID].HumanNums.append([type, index])
    #                 # allTasks[selectTaskID].HumanNums.append(humans[type][index].number)
    #                 need -= 1
    #
    #         # 分配 根据 record 分配
    #         for type in range(len(resourceAvailS)):
    #
    #             need = allTasks[selectTaskID].resourceRequestS[type]
    #             if need > 0:
    #                 alreadyWorkTime = math.inf
    #                 index = 0
    #                 for nowStaion in recordS[type]:
    #                     if nowStaion.alreadyworkTime < alreadyWorkTime:
    #                         alreadyWorkTime = nowStaion.alreadyworkTime
    #                         index = nowStaion.zunumber
    #
    #                 # 更新
    #                 stations[type][index].update(allTasks[selectTaskID])
    #                 allTasks[selectTaskID].SheiBei.append([type, index])
    #                 # allTasks[selectTaskID].SNums.append(stations[type][index].number)
    #                 need -= 1
    #
    #         need = allTasks[selectTaskID].resourceRequestSpace[now_pos - 1]
    #         if need > 0:
    #             index = 0
    #
    #             # 更新人员
    #             spaces[now_pos - 1][index].update(allTasks[selectTaskID])
    #             # allTasks[selectTaskID].HumanNums.append(humans[type][index].number)
    #             need -= 1
    #
    #         # 局部调度计划ps
    #         ps.append(selectTaskID)
    #         allTasks[selectTaskID].priority = allTasks[selectTaskID].es
    #
    #     ACTS = copy.deepcopy(allTasks)
    #     ACTS = sorted(ACTS.items(), key=lambda x: -x[1].ef)
    #     if LR != "left":
    #         maxtime = ACTS[0][1].ef
    #         for act in allTasks.keys():
    #             tmp1 = allTasks[act].es
    #             tmp2 = allTasks[act].ef
    #             tmp3 = copy.deepcopy(allTasks[act].predecessor)
    #             tmp4 = copy.deepcopy(allTasks[act].successor)
    #             allTasks[act].es = (0 - tmp2) + maxtime
    #             allTasks[act].ef = (0 - tmp1) + maxtime
    #             allTasks[act].predecessor = tmp4
    #             allTasks[act].successor = tmp3
    #
    #     # 更新codes
    #     # for taskcode in codes[0]:
    #     #         Id = taskcode[0]
    #     #         codes[0][Id][1] = allTasks[Id].es
    #     #         codes[1][Id][1] = allTasks[Id].ef
    #     #
    #     # codes[0] = sorted(codes[0],key = lambda x:x[0])
    #     # codes[1] = sorted(codes[1],key = lambda x:x[0])
    #
    #     return allTasks




if __name__ == '__main__':
    m = MyInit("C:/Users/29639/Desktop/sim/dis.csv","C:/Users/29639/Desktop/sim/dis.csv")
    m.InitPopulation()
    a=[[0,1,2],[[2,3,1]]]
    b=[[1,1,2],[[2,3,1]]]


    print(a==b)












