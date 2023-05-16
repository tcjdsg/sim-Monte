from matplotlib import pyplot as plt
import matplotlib.patches as mpatches

from conM.FixedMess import FixedMes


def Draw_gantt(shebei):
    colors = ['b', 'c', 'g', 'k', 'm', 'r', 'y', 'grey','0.1','0.2','0.3','0.4','0.5','0.6','0.7','0.8']
    number=0
    for i in range(len(shebei)):
        for j in range(len(shebei[i])):
            number += 1

            for order in shebei[i][j].OrderOver:
                job = order.belong_plane_id
                gongxu = order.taskid
                time1= order.es
                time2= order.ef
                if (time2 - time1) != 0:
                   plt.barh(number, time2 - time1-0.1,
                     left=time1, color=colors[job])
                news = str(gongxu)
                infmt = '(' + str(job ) + ',' + news + ')'
                if (time2 - time1)!=0:
                   plt.text(x=time1, y=number-0.1 , s=infmt, fontsize=8,
                       color='white')

    label_name = ['JOB' + str(i ) for i in FixedMes.jzjNumbers]
    patches = [mpatches.Patch(color=colors[i], label=label_name[i]) for i in range(len(label_name))]
    plt.legend(handles=patches, loc=4)
    # plt.yticks([i + 1 for i in range(people_number)])
    plt.show()