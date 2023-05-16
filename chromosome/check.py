#判断编码是否满足前序后序关系

def checkIfRight(individual,prece2,prece1):

    # i是舰载机，j是工序
    # 由于调度的存在 不同区域的舰载机紧前紧后工序有差异
    # -1
    code = individual.codes
    temp = []
    flag = True
    for jzjOp in code:
        jzj = jzjOp[0]
        op = jzjOp[1]
        if jzj > 2:
            prece = prece2
        else:
            prece = prece1
        if prece[op][0] == -1:
            temp.append(jzjOp)
        else:
            for otherOp in prece[op]:
                if [jzj,otherOp,1] not in temp:
                    flag = False
                    break
            if flag:
                temp.append(jzjOp)
        return flag