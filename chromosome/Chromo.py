
class Chromosome():
    def __init__(self):
        self.codes = []
        self.WorkTime = 999999999
        self.variance = 9999.0
        self.movetime = 9999.0

        self.Maxfagiue = 0
        self.Ecmax = 100
        self.Pr = 0.0
        self.np=0
        self.sp=[]

        self.f=None       #适应度
        self.rank = -1    #用于多目标
        self.crowding_distance = -1
        self.zonghe = 9999999999
        # self.cal=SSGS     #解码方式。串行、并行
        # self.pa=paramater()  #参数配置

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def setcodes(self,codes):
            self.codes=codes


    def __gt__(self, other):
        if self.rank > other.rank:
            return True
        if self.rank==other.rank and self.crowding_distance < other.crowding_distance:
            return True
        return  False
    def setf(self):

        # FinishTime, all,Allpeople,_,_ = decoder(self.codes,People,self.pa)
        #
        # Junheng = getJunheng(Allpeople)

        self.zonghe = 10**7*(1.0-self.Pr) + self.Ecmax

        # self.newf =[self.Ecmax,self.Pr,self.WorkTime]
        self.f=[self.Pr,self.Ecmax]
        return self.f

