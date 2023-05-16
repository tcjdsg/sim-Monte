import random
import numpy as np


class Encode:
    def __init__(self, Task, Qutity, Interrupt):
        self.Task = Task
        self.Qutity = Qutity
        self.Interrupt = Interrupt

    def Chromosome1(self):
        chromosome1 = []  # 任务列表,染色体1

        for a in range(self.Qutity):
            Ei_0 = []  # 紧前任务数为0的任务编号集合
            for key, Ei in self.Task.items():  # 搜索所有任务(遍历字典中的key和value)
                # Ei即为每个任务的紧前任务集合
                Ei_number = len(Ei) - 1  # 每个任务的紧前任务数量，减1是因为所有都包含了0任务
                if Ei_number == 0:
                    Ei_0.append(key)
            random.shuffle(Ei_0)
            random_Ei_0 = Ei_0[0]  # 随机取一个 = 随机打乱list取第一个

            chromosome1.append(random_Ei_0)

            for key, Ei in self.Task.items():
                if random_Ei_0 in Ei:
                    Ei.remove(random_Ei_0)
            del self.Task[random_Ei_0]
        return chromosome1

    def Chromosome(self):
        chromosome1 = self.Chromosome1()
        chromosome2 = []
        for i in chromosome1:
            b = self.Interrupt[i]
            chromosome2.append(b)
        chromosome = np.hstack((chromosome1, chromosome2))
        return chromosome