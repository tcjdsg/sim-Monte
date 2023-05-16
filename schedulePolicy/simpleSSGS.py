import copy
import math

import numpy as np

from conM.FixedMess import FixedMes


def simpleSSGS(allTasks, codes, humans, stations, spaces, LR):
    w = 0.000001

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

    # 记录资源转移
    resourceAvailH = FixedMes.total_Huamn_resource
    resourceAvailS = FixedMes.total_station_resource
    resourceAvailSpace = FixedMes.total_space_resource

    resourceAvail = np.concatenate((resourceAvailH,resourceAvailS, resourceAvailSpace), axis=0)

    ps = [0]  # 局部调度计划初始化

    allTasks[0].es = 0  # 活动1的最早开始时间设为0
    allTasks[0].ef = allTasks[0].es + allTasks[0].duration
    en = allTasks[0].successor
    en.append(0)

    for stage in range(0, len(code)):
        selectTaskID = code[stage][0]
        nowResourceRequest = np.concatenate((allTasks[selectTaskID].resourceRequestH, allTasks[selectTaskID].resourceRequestS, allTasks[selectTaskID].resourceRequestSpace),axis=0)
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
        t = startTime + w

        recordS = [[] for _ in range(len(resourceAvailS))]
        while t <= startTime + allTasks[selectTaskID].duration:
            resourceSum = np.zeros(len(resourceAvail))
            for taskIDA in ps:
                resourceRequest = np.concatenate((allTasks[taskIDA].resourceRequestH,allTasks[taskIDA].resourceRequestS, allTasks[taskIDA].resourceRequestSpace), axis=0)

                if allTasks[taskIDA].es + w <= t <= allTasks[taskIDA].es + allTasks[taskIDA].duration:
                    resourceSum = resourceSum + resourceRequest
            # 加上当前阶段需要安排的活动的资源占用，对比总资源限量是否超过
            resourceSum = resourceSum + nowResourceRequest
            # 若超出资源限量，则向后推一个单位时间
            if (resourceSum > resourceAvail).any():
                startTime += 0.1
                t = startTime + w
            else:
                resourceSumS = np.zeros(len(resourceAvailS))

                for type in range(len(resourceAvailS)):
                    for station in stations[type]:
                    # 舰载机在这个加油站的覆盖范围内：
                        if now_pos in FixedMes.constraintS_JZJ[type][station.zunumber]:
                            if (len(station.OrderOver) == 0):
                                resourceSumS[type] += 1  # 该类资源可用+1
                                recordS[type].append(station)

                            if (len(station.OrderOver) == 1):
                                Activity1 = station.OrderOver[0]

                                if (Activity1.ef + 0.01) <= t \
                                    or (t + dur + 0.01) <= (Activity1.es):
                                    resourceSumS[type] += 1  # 该类资源可用+1
                                    recordS[type].append(station)

                            if (len(station.OrderOver) >= 2):
                                flag = False
                                for taskIndex in range(len(station.OrderOver) - 1):
                                    Activity1 = station.OrderOver[taskIndex]
                                    Activity2 = station.OrderOver[taskIndex + 1]


                                    if (Activity1.ef + 0.01) <= t \
                                        and (t + dur + 0.01) <= (Activity2.es):
                                        resourceSumS[type] += 1  # 该类资源可用+1
                                        recordS[type].append(station)
                                        flag = True
                                if flag == False:
                                    Activity1 = station.OrderOver[-1]
                                    Activity2 = station.OrderOver[0]

                                    if (Activity1.ef + 0.01) <= t or (t + 0.01 + dur) <= Activity2.es:
                                        resourceSumS[type] += 1
                                        recordS[type].append(station)
                if (resourceSumS < allTasks[selectTaskID].resourceRequestS).any():
                    startTime += 0.1
                    t = startTime + 0.1
                else:
                    t += 0.1
            # 若符合资源限量则将当前活动开始时间安排在这一时刻
        allTasks[selectTaskID].es = startTime
        allTasks[selectTaskID].ef = startTime + allTasks[selectTaskID].duration
        # priorityToUse.remove(selectTaskID)  # 更新优先序列
        # # 更新合格活动集合en，和局部调度计划ps
        en.remove(selectTaskID)
        ps.append(selectTaskID)
        # for taskToAdd in allTasks[selectTaskID].successor:
        #     if set(allTasks[taskToAdd].predecessor) < set(ps):
        #         en.append(taskToAdd)

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

        # need = allTasks[selectTaskID].resourceRequestSpace[now_pos - 1]
        # if need > 0:
        #     index = 0
        #
        #     # 更新人员
        #     spaces[now_pos - 1][index].update(allTasks[selectTaskID])
        #     # allTasks[selectTaskID].HumanNums.append(humans[type][index].number)
        #     need -= 1

        # 局部调度计划ps
        ps.append(selectTaskID)

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

        # 更新codes
        for taskcode in codes[0]:
            Id = taskcode[0]
            codes[0][Id][1] = allTasks[Id].es
            codes[1][Id][1] = allTasks[Id].ef
            allTasks[Id].priority = allTasks[Id].es


if __name__ == '__main__':
    print_hi('Python')
