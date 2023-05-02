from time import sleep, time
import krpc
import math

class PID:

    def __init__(self, P, I, D):
        self.last_dx = 0
        self.ix = 0
        self.P = P
        self.I = I
        self.D = D

    def PID(self, target, input):

        dx = target - input
        self.ix = self.ix + dx
        # 积分与误差同向，快速调整
        # if(dx > 0 ):
        #     if(self.ix < 0):
        #         self.ix = 0
        # if(dx < 0 ):
        #     if(self.ix > 0):
        #         self.ix = 0
        # 积分限幅
        if(self.ix > 100):
            self.ix = 100
        if(self.ix < -100):
            self.ix = -100
        ddx = (dx - self.last_dx)/0.02
        self.last_dx = dx

        # print("\rerror:%.1f"%dx,"ix:%.1f"%self.ix,"ddx%.1f"%ddx,end='\r')
        return self.P*dx + self.I*self.ix + self.D*ddx