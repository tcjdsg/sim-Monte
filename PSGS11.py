import heapq
from multiprocessing import Pool
#
# class Task:
#     def __init__(self, name, run_time, resources):
#         self.name = name
#         self.run_time = run_time
#         self.resources = resources
#
#     async def run(self):
#         # 执行任务的代码
#         pass
#
# class Scheduler:
#     def __init__(self, max_resources):
#         self.max_resources = max_resources
#         self.running_tasks = []
#         self.waiting_tasks = []
#
#     def add_task(self, task):
#         heapq.heappush(self.waiting_tasks, task)
#
#     def can_run(self, task):
#         return sum(task.resources) <= self.max_resources
#
#     def schedule_tasks(self):
#         while True:
#             while len(self.running_tasks) < self.max_resources and self.waiting_tasks:
#                 task = heapq.heappop(self.waiting_tasks)
#                 if self.can_run(task):
#                     self.running_tasks.append(task)
#                 else:
#                     heapq.heappush(self.waiting_tasks, task)
#                     break
#
#             if not self.running_tasks:
#                 break
#
#             finished_tasks = []
#             for task in self.running_tasks:
#                 task.run_time -= 1
#                 if task.run_time == 0:
#                     finished_tasks.append(task)
#
#             for task in finished_tasks:
#                 self.running_tasks.remove(task)
#
#     def run(self, tasks):
#         # 将所有任务添加到等待队列中
#         for t in tasks:
#             self.add_task(t)
#
#         pool = Pool(processes=len(tasks))
#         result = pool.map_async(lambda x: x.run(), tasks)
#         result.wait()


# class TaskOrder:
#     def __init__(self, name, run_time, resources):
#         self.name = name
#         self.run_time = run_time
#         self.remaining_time = run_time
#         self.resources = resources
#
#     def __lt__(self, other):
#         return self.remaining_time < other.remaining_time
#
#     def __eq__(self, other):
#         return self.remaining_time == other.remaining_time
#
#     def __gt__(self, other):
#         return self.remaining_time > other.remaining_time
#
#     def execute(self):
#         # 执行任务的代码
#         pass

class PSGSScheduler:
    def __init__(self, max_resources):
        self.max_resources = max_resources
        self.running_tasks = []
        self.waiting_tasks = []

    def can_run(self, task):
        return sum(task.resources) <= self.max_resources

    def schedule_tasks(self):
        while self.waiting_tasks or self.running_tasks:
            while self.waiting_tasks and self.can_run(self.waiting_tasks[0]):
                task = self.waiting_tasks[0]
                heapq.heappush(self.running_tasks, task)
                heapq.heappop(self.waiting_tasks)

            for task in self.running_tasks:
                task.remaining_time -= 1
                task.execute()

            while self.running_tasks and self.running_tasks[0].remaining_time == 0:
                heapq.heappop(self.running_tasks)

    def add_task(self, task):
        heapq.heappush(self.waiting_tasks, task)

    def run(self, tasks):
        for task in tasks:
            self.add_task(task)

        self.schedule_tasks()


if __name__ == '__main__':
    max_resources = 2

    tasks = [
        Task('Task1', 5, [1, 1]),
        Task('Task2', 2, [1, 1]),
        Task('Task3', 1, [1, 2]),
        Task('Task4', 3, [2, 1]),
        Task('Task5', 4, [1, 3]),
        Task('Task6', 2, [2, 2]),
    ]

    scheduler = PSGSScheduler(max_resources)
    scheduler.run(tasks)
if __name__ == '__main__':
    max_resources = 2

    tasks = [
        Task('Task1', 5, [1, 1]),
        Task('Task2', 2, [1, 1]),
        Task('Task3', 1, [1, 2]),
        Task('Task4', 3, [2, 1]),
        Task('Task5', 4, [1, 3]),
        Task('Task6', 2, [2, 2]),
    ]

    scheduler = Scheduler(max_resources)
    scheduler.run(tasks)