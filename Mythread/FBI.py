#codes.的格式是优先数
import copy
import math
import random
from collections import defaultdict

import numpy as np

from  Mythread.myInit import MyInit
from activity.Activitity import Order

from conM.FixedMess import FixedMes
from draw.people import Draw_gantt
from human.Human import Human


def FBI(codes,allTasks, humans,stations,spaces):
    # MyInit.serialGenerationScheme(allTasks, humans, stations, spaces)
    leftAndRight(codes,allTasks,humans,stations,spaces,"left")
    leftAndRight(codes,allTasks,humans,stations,spaces,"right")



def leftAndRight(codes,allTasks, humans,stations,spaces,flag):
    if flag=="left":
        code = sorted(codes[0],key=lambda x: x[1])
    else:
        code = sorted(codes[1],key=lambda x: x[1])
        maxtime = allTasks[code[-1][0]].ef
        for activity in allTasks:
            tmp1 = activity.es
            tmp2 = activity.ef
            tmp3 = copy.deepcopy(activity.predecessor)
            tmp4 = copy.deepcopy(activity.successor)
            activity.es = (0 - tmp2) + maxtime
            activity.ef = (0 - tmp1) + maxtime
            activity.predecessor = tmp4
            activity.successor = tmp3


    resourceAvailH = FixedMes.total_Huamn_resource
    resourceAvailS = FixedMes.total_station_resource
    resourceAvailSpace = FixedMes.total_space_resource

    for stage in range(0, len(code)):
            selectTaskID = code[stage][0]
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


            recordH = [[] for _ in range(len(resourceAvailH))]

            recordS = [[] for _ in range(len(resourceAvailS))]

            # 计算t时刻正在进行的活动的资源占用总量,当当前时刻大于活动开始时间小于等于活动结束时间时，说明活动在当前时刻占用资源
            while t > startTime :

                resourceSumH = np.zeros(len(resourceAvailH))
                recordH = [[] for _ in range(len(resourceAvailH))]

                resourceSumS = np.zeros(len(resourceAvailS))
                recordS = [[] for _ in range(len(resourceAvailS))]

                resourceSumNew = np.zeros(len(resourceAvailS))

                resourceSumSpace = np.zeros(len(resourceAvailSpace))
                recordSpace = [[] for _ in range(len(resourceAvailSpace))]

                #第舰载机的座舱资源
                if allTasks[selectTaskID].resourceRequestSpace[now_pos-1]>0:
                      for space in spaces[now_pos-1]:

                          if (len(space.OrderOver) == 0):
                              resourceSumSpace[now_pos-1] += 1  # 该类资源可用+1


                          if (len(space.OrderOver) == 1):
                              Activity1 = space.OrderOver[0]

                              # movetime1 = 0 if from_pos == 0 else FixedMes.distance[from_pos][
                              #                                         now_pos] / FixedMes.human_walk_speed
                              # movetime2 = 0 if to_pos == 0 else FixedMes.distance[to_pos][
                              #                                       now_pos] / FixedMes.human_walk_speed

                              if (Activity1.ef +0.01 ) <= t \
                                      or (t + dur + 0.01) <= (Activity1.es):
                                  resourceSumSpace[now_pos-1] += 1  # 该类资源可用+1


                        #遍历船员工序，找到可能可以插入的位置,如果船员没有工作，人力资源可用
                          if(len(space.OrderOver)>=2):
                              flag = False
                              for taskIndex in range(len(space.OrderOver)-1):
                                  Activity1 = space.OrderOver[taskIndex]
                                  Activity2 = space.OrderOver[taskIndex+1]

                                  # from_pos = Activity1.belong_plane_id
                                  # to_pos = Activity2.belong_plane_id
                                  # movetime1 = 0 if from_pos==0 else FixedMes.distance[from_pos][now_pos]/FixedMes.human_walk_speed
                                  # movetime2 = 0 if to_pos==0 else FixedMes.distance[to_pos][now_pos]/FixedMes.human_walk_speed

                                  if (Activity1.ef + 0.01) <= t \
                                     and (t + dur + 0.01 ) <= (Activity2.es):
                                       flag=True
                                       resourceSumSpace[now_pos-1] += 1  # 该类资源可用+1

                                       break

                              if flag==False:
                                  Activity1 = space.OrderOver[0]
                                  Activity2 = space.OrderOver[-1]


                                  if (Activity2.ef + 0.01 ) <= t \
                                          or (t + dur + 0.01) <= (Activity1.es):
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
                              movetime1 = 0 if from_pos == 0 else FixedMes.distance[from_pos][
                                                                      now_pos] / FixedMes.human_walk_speed
                              movetime2 = 0 if to_pos == 0 else FixedMes.distance[to_pos][
                                                                    now_pos] / FixedMes.human_walk_speed

                              if (Activity1.ef + 1 + round(movetime1,1)) <= t \
                                      or (t + dur + 1) <= (Activity1.es - round(movetime2,1)):
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
                                  movetime1 = 0 if from_pos==0 else FixedMes.distance[from_pos][now_pos]/FixedMes.human_walk_speed
                                  movetime2 = 0 if to_pos==0 else FixedMes.distance[to_pos][now_pos]/FixedMes.human_walk_speed

                                  if (Activity1.ef + 1 +  round(movetime1,1)) <= t \
                                     and (t + dur + 1 ) <= (Activity2.es - round(movetime2,1)):
                                       flag=True
                                       resourceSumH[type] += 1  # 该类资源可用+1
                                       recordH[type].append(human)
                                       break

                              if flag==False:
                                  Activity1 = human.OrderOver[0]
                                  Activity2 = human.OrderOver[-1]
                                  from_pos = Activity2.belong_plane_id
                                  to_pos = Activity1.belong_plane_id
                                  movetime2 = 0 if from_pos == 0 else FixedMes.distance[from_pos][
                                                                          now_pos] / FixedMes.human_walk_speed
                                  movetime1 = 0 if to_pos == 0 else FixedMes.distance[to_pos][
                                                                        now_pos] / FixedMes.human_walk_speed

                                  if (Activity2.ef + 1 + round(movetime2,1)) <= t \
                                          or (t + dur + 1) <= (Activity1.es - round(movetime1,1)):
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

                                #说明此刻 油料等资源在使用
                                if t > renewActivity.es and t < renewActivity.ef:
                                    resourceSumNew[type] += 1 # 该类资源可用+1
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

                                        if (Activity1.ef + 0.01 ) <= t \
                                          or (t + dur + 0.01) <= (Activity1.es):
                                            resourceSumS[type] += 1  # 该类资源可用+1
                                            recordS[type].append(station)

                                    if (len(station.OrderOver) >= 2):
                                        flag = False
                                        for taskIndex in range(len(station.OrderOver)-1):
                                            Activity1 = station.OrderOver[taskIndex]
                                            Activity2 = station.OrderOver[taskIndex+1]

                               # from_pos = Activity1.belong_plane_id
                               # to_pos = Activity2.belong_plane_id
                               # movetime1 = 0 if from_pos==0 else FixedMes.distance[from_pos][now_pos]*FixedMes.human_walk_speed
                               # movetime2 = 0 if to_pos==0 else FixedMes.distance[to_pos][now_pos]*FixedMes.human_walk_speed

                                            if (Activity1.ef + 0.01) <= t \
                                        and (t + dur + 0.01 ) <= (Activity2.es):
                                                resourceSumS[type] += 1  # 该类资源可用+1
                                                recordS[type].append(station)
                                                flag = True
                                        if flag == False:
                                            Activity1 = station.OrderOver[-1]
                                            Activity2 = station.OrderOver[0]

                                            if (Activity1.ef + 0.01 ) <= t or (t + 0.01 +dur) <= Activity2.es:
                                                resourceSumS[type] += 1
                                                recordS[type].append(station)


                # 若资源不够，则向后推一个单位时间
                if renewFlag==False or ((resourceSumSpace < allTasks[selectTaskID].resourceRequestSpace).any()) or (resourceSumH < allTasks[selectTaskID].resourceRequestH).any() or (resourceSumS < allTasks[selectTaskID].resourceRequestS).any() :
                        t += 1
                else:
                    break
            # 若符合资源限量则将当前活动开始时间安排在这一时刻
            allTasks[selectTaskID].es = t
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

                    # 更新人员
                    humans[type][index].update(allTasks[selectTaskID])
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
                    # allTasks[selectTaskID].SNums.append(stations[type][index].number)
                    need -= 1

            need = allTasks[selectTaskID].resourceRequestSpace[now_pos-1]
            if need > 0:

                    index = 0

                    # 更新人员
                    spaces[now_pos-1][index].update(allTasks[selectTaskID])
                    # allTasks[selectTaskID].HumanNums.append(humans[type][index].number)
                    need -= 1

            # 局部调度计划ps

    ACTS=sorted(allTasks,key=lambda x: -x.ef)


    maxtime = ACTS[0].ef
    for activity in allTasks:
        tmp1 = activity.es
        tmp2 = activity.ef
        tmp3 = copy.deepcopy(activity.predecessor)
        tmp4 = copy.deepcopy(activity.successor)
        activity.es = (0 - tmp2) + maxtime
        activity.ef = (0 - tmp1) + maxtime
        activity.predecessor = tmp4
        activity.successor = tmp3

    #更新codes
    for taskcode in codes[0]:
        Id=taskcode[0]
        codes[0][Id][1] =allTasks[Id].es
        codes[1][Id][1] = allTasks[Id].ef

if __name__ == "__main__":
    def FBI(codes, allTasks, humans, stations, spaces):
        # MyInit.serialGenerationScheme(allTasks, humans, stations, spaces)
        leftAndRight(codes, allTasks, humans, stations, spaces, "left")
        leftAndRight(codes, allTasks, humans, stations, spaces, "right")


    def leftAndRight(codes, allTasks, humans, stations, spaces, LR):
        if LR == "left":
            code = sorted(codes[0], key=lambda x: x[1])
        else:
            code = sorted(codes[1], key=lambda x: -x[1])
            maxtime = allTasks[code[0][0]].ef
            for act in allTasks.keys():
                tmp1 = allTasks[act].es
                tmp2 = allTasks[act].ef
                tmp3 = copy.deepcopy(allTasks[act].predecessor)
                tmp4 = copy.deepcopy(allTasks[act].successor)
                allTasks[act].es = (0 - tmp2) + maxtime
                allTasks[act].ef = (0 - tmp1) + maxtime
                allTasks[act].predecessor = tmp4
                allTasks[act].successor = tmp3


        resourceAvailH = [2]
        resourceAvailS = [0]


        for stage in range(0, len(code)):
            selectTaskID = code[stage][0]
            earliestStartTime = 0

            '''
            需要考虑移动时间
            '''

            dur = allTasks[selectTaskID].duration
            for preTaskID in allTasks[selectTaskID].predecessor:
                if allTasks[preTaskID].ef > earliestStartTime:
                    earliestStartTime = allTasks[preTaskID].ef

            startTime = earliestStartTime
            # 检查满足资源限量约束的时间点作为活动最早开始时间，即在这一时刻同时满足活动逻辑约束和资源限量约束
            t = startTime+0.001

            recordH = [[] for _ in range(len(resourceAvailH))]

            # recordS = [[] for _ in range(len(resourceAvailS))]

            # 计算t时刻正在进行的活动的资源占用总量,当当前时刻大于活动开始时间小于等于活动结束时间时，说明活动在当前时刻占用资源
            while t > startTime:

                resourceSumH = np.zeros(len(resourceAvailH))
                recordH = [[] for _ in range(len(resourceAvailH))]

                for type in range(len(resourceAvailH)):
                    if allTasks[selectTaskID].resourceRequestH[type] > 0:
                        for human in humans[type]:

                            if (len(human.OrderOver) == 0):
                                resourceSumH[type] += 1  # 该类资源可用+1
                                recordH[type].append(human)

                            if (len(human.OrderOver) == 1):
                                Activity1 = human.OrderOver[0]
                                from_pos = Activity1.belong_plane_id
                                to_pos = Activity1.belong_plane_id
                                movetime1 = 0
                                movetime2 = 0

                                if (Activity1.ef + 0.001 + round(movetime1, 1)) <= t \
                                        or (t + dur +  0.001) <= (Activity1.es - round(movetime2, 1)):
                                    resourceSumH[type] += 1  # 该类资源可用+1
                                    recordH[type].append(human)

                            # 遍历船员工序，找到可能可以插入的位置,如果船员没有工作，人力资源可用
                            if (len(human.OrderOver) >= 2):
                                flag = False
                                for taskIndex in range(len(human.OrderOver) - 1):
                                    Activity1 = human.OrderOver[taskIndex]
                                    Activity2 = human.OrderOver[taskIndex + 1]

                                    from_pos = Activity1.belong_plane_id
                                    to_pos = Activity2.belong_plane_id
                                    movetime1 = 0
                                    movetime2 = 0

                                    if (Activity1.ef +  0.001 + round(movetime1, 1)) <= t \
                                            and (t + dur +  0.001) <= (Activity2.es - round(movetime2, 1)):
                                        flag = True
                                        resourceSumH[type] += 1  # 该类资源可用+1
                                        recordH[type].append(human)
                                        break

                                if flag == False:
                                    Activity1 = human.OrderOver[0]
                                    Activity2 = human.OrderOver[-1]
                                    from_pos = Activity2.belong_plane_id
                                    to_pos = Activity1.belong_plane_id
                                    movetime2 = 0
                                    movetime1 = 0

                                    if (Activity2.ef +  0.001 + round(movetime2, 1)) <= t \
                                            or (t + dur +  0.001) <= (Activity1.es - round(movetime1, 1)):
                                        resourceSumH[type] += 1  # 该类资源可用+1
                                        recordH[type].append(human)

                if (resourceSumH < allTasks[selectTaskID].resourceRequestH).any():
                    t += 0.1
                else:
                    break
            # 若符合资源限量则将当前活动开始时间安排在这一时刻
            allTasks[selectTaskID].es = t
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

                    # 更新人员
                    # print(type,index)
                    humans[type][index].update(allTasks[selectTaskID])
                    # allTasks[selectTaskID].HumanNums.append(humans[type][index].number)
                    need -= 1

            # # 分配 根据 record 分配
            # for type in range(len(resourceAvailS)):
            #
            #     need = allTasks[selectTaskID].resourceRequestS[type]
            #     if need > 0:
            #         alreadyWorkTime = math.inf
            #         index = 0
            #         for nowStaion in recordS[type]:
            #             if nowStaion.alreadyworkTime < alreadyWorkTime:
            #                 alreadyWorkTime = nowStaion.alreadyworkTime
            #                 index = nowStaion.zunumber
            #
            #         # 更新
            #         stations[type][index].update(allTasks[selectTaskID])
            #         # allTasks[selectTaskID].SNums.append(stations[type][index].number)
            #         need -= 1
            #
            # need = allTasks[selectTaskID].resourceRequestSpace[now_pos - 1]
            # if need > 0:
            #     index = 0
            #
            #     # 更新人员
            #     spaces[now_pos - 1][index].update(allTasks[selectTaskID])
            #     # allTasks[selectTaskID].HumanNums.append(humans[type][index].number)
            #     need -= 1

            # 局部调度计划ps

        ACTS = copy.deepcopy(allTasks)
        ACTS = sorted(ACTS.items(), key=lambda x: -x[1].ef)
        if LR!="left":
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

        # 更新codes
        for taskcode in codes[0]:
            Id = taskcode[0]
            codes[0][Id][1] = allTasks[Id].es
            codes[1][Id][1] = allTasks[Id].ef

    def encoderReal(activities):
        numbers = len(activities)
        cloneA = copy.deepcopy(activities)
        chromosome = []
        right=[]


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
            start = random_Ei_0 + random.random()
            chromosome.append([random_Ei_0,start])
            right.append([random_Ei_0,start + activities[random_Ei_0].duration])

            for key, Ei in cloneA.items():
                prece = cloneA[key].predecessor
                if random_Ei_0 in prece:
                    prece.remove(random_Ei_0)
            del cloneA[random_Ei_0]
        return [chromosome,right]


    activities = {}

    preActDict = defaultdict(lambda: [])
    for i in range(1, 11):
        preActDict[i].append(0)
    index = 0

    # 构建任务网络

    OrderTime=[0,2,3,1,2,5,2,1,3,4,0]
    OrderInputMes=[0,1,1,1,1,2,1,1,1,1,0]

    SucOrder=[[],
              [5,6,8,10],
              [6,8,9,10],
              [6,8,9,10],
              [7,9,10],
              [9,10],

              [8,9,10],
              [9,10],
              [10],
              [10],
              []]

    for j in range(9):
            index += 1
            taskId = j + 1
            duration = OrderTime[taskId]
            resourceH = [0]
            # nt()pri
            resourceH[0] = OrderInputMes[taskId]

            SUCOrder = SucOrder[taskId]


            task = Order(index, taskId, duration, resourceH, [], [], SUCOrder, 1)

            activities[index] = task
            for s in SUCOrder:
                preActDict[s].append(index)

    for act in activities.keys():
        activities[act].predecessor = preActDict[act]

    SUCOrder = [i for i in range(1, 11)]
    resourceH = [0]


    activities[0] = Order(0, 0, 0, resourceH, [], [], SUCOrder, 0)
    activities[0].predecessor = []
    activities[index + 1] = Order(0, 0, 0, resourceH, [], [], [], 0)
    activities[index + 1].predecessor = [i for i in range(10)]

    Humans=[[]]
    Humans[0].append(Human([0, 0, 0]))
    Humans[0].append(Human([0, 1, 1]))


    # codes = encoderReal(activities)
    codes=[[[0,0],[1,3],[2,0],[3,2],[4,0],[5,7],[6,5],[7,11],[8,11],[9,12],[10,16]],
           [[0,0],[1,5],[2,3],[3,3],[4,2],[5,11],[6,7],[7,12],[8,14],[9,16],[10,16]]]
    from matplotlib import pyplot as plt
    import matplotlib.patches as mpatches

    from conM.FixedMess import FixedMes


    def Draw_gantt(all_people):
        colors = ['b', 'c', 'g', 'k', 'm', 'r', 'y', 'grey', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8']
        number = 0
        for i in range(len(all_people)):
            for j in range(len(all_people[i])):
                index=j+1


                for order in all_people[i][j].OrderOver:

                    gongxu = order.taskid
                    time1 = order.es
                    time2 = order.ef

                    if (time2 - time1) != 0:
                        print(int(time2) - int(time1))
                        plt.barh(int(index), int(time2) - int(time1),
                                 left=int(time1), color=colors[gongxu])
                    news = str(gongxu)
                    infmt = '(' + news + ')'
                    if (time2 - time1) != 0:
                        plt.text(x=int(time1), y=int(index) - 0.1, s=infmt, fontsize=8,
                                 color='white')

        # plt.yticks([i + 1 for i in range(people_number)])
        plt.show()

    leftAndRight(codes, activities, Humans, [], [], "left")

    Humans=[[]]
    Humans[0].append(Human([0, 0, 0]))
    Humans[0].append(Human([0, 1, 1]))
    leftAndRight(codes, activities, Humans, [], [], "right")


    Humans = [[]]
    Humans[0].append(Human([0, 0, 0]))
    Humans[0].append(Human([0, 1, 1]))

    leftAndRight(codes, activities, Humans, [], [], "left")
    Draw_gantt(Humans)



    # 活动数int， 资源数int， 资源限量np.array， 所有活动集合dic{活动代号：活动对象}


