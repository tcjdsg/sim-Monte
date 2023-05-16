from matplotlib import pyplot as plt
import matplotlib.patches as mpatches

from conM.FixedMess import FixedMes


def Draw1(all_people):
    colors = ['b', 'c', 'g', 'k', 'm', 'r', 'y', 'grey','0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8']
    number=0
    for i in range(len(all_people)):
        for j in range(len(all_people[i])):
            number += 1

            for order in all_people[i][j].OrderOver:
                job = order.belong_plane_id
                gongxu = order.taskid
                id = order.id
                time1= order.es
                time2= order.ef
                if (time2 - time1) != 0:
                   plt.barh(number, time2 - time1-0.1,
                     left=time1, color=colors[job])
                news = str(gongxu)
                infmt = '(' + str(job ) + ',' + news + str(id)+')'
                if (time2 - time1)!=0:
                   plt.text(x=time1, y=number-0.1 , s=infmt, fontsize=8,
                       color='white')

    label_name = ['JOB' + str(i ) for i in FixedMes.jzjNumbers]
    patches = [mpatches.Patch(color=colors[i+1], label=label_name[i]) for i in range(len(label_name))]
    plt.legend(handles=patches, loc=4)
    plt.show()
    # plt.yticks([i + 1 for i in range(people_number)])


def Draw(all_people,sebei):
    fig = plt.figure()
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    colors = ['b', 'c', 'g', 'k', 'm', 'r', 'y', 'grey', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8']
    number = 0
    for i in range(len(all_people)):
         for j in range(len(all_people[i])):
             number += 1

             for order in all_people[i][j].OrderOver:
                 job = order.belong_plane_id
                 gongxu = order.taskid
                 time1 = order.es
                 time2 = order.ef
                 if (time2 - time1) != 0:
                     ax1.barh(number, time2 - time1 - 0.1,
                              left=time1, color=colors[job])
                 news = str(gongxu)
                 infmt = '(' + str(job) + ',' + news + ')'
                 if (time2 - time1) != 0:
                     ax1.text(x=time1, y=number - 0.1, s=infmt, fontsize=8,
                              color='white')

    label_name = ['JOB' + str(i) for i in FixedMes.jzjNumbers]
    patches = [mpatches.Patch(color=colors[i], label=label_name[i]) for i in range(len(label_name))]
    ax1.legend(handles=patches, loc=4)

    number = 0
    for i in range(len(sebei)):
        for j in range(len(sebei[i])):
            number += 1

            for order in sebei[i][j].OrderOver:
                job = order.belong_plane_id
                gongxu = order.taskid
                time1 = order.es
                time2 = order.ef
                if (time2 - time1) != 0:
                    ax2.barh(number, time2 - time1 - 0.1,
                             left=time1, color=colors[job])
                news = str(gongxu)
                infmt = '(' + str(job) + ',' + news + ')'
                if (time2 - time1) != 0:
                    ax2.text(x=time1, y=number - 0.1, s=infmt, fontsize=8,
                             color='white')

    label_name = ['JOB' + str(i) for i in FixedMes.jzjNumbers]
    patches = [mpatches.Patch(color=colors[i], label=label_name[i]) for i in range(len(label_name))]
    ax2.legend(handles=patches, loc=4)

    plt.show()
