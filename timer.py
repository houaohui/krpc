from time import sleep, time
import krpc
import math
import global_var as gl

class RepeatedTimer(object):
    def __init__(self, interval, function, *args, **kwargs):
        self.interval = interval
        self.function = function
        self.is_running = False
        self.args = args
        self.kwargs = kwargs
        self.start_time = 0

    def start(self):
        space_scenter = gl.get_value('space_center')
        ut = space_scenter.ut
        self.start_time = int(ut * 1000)
        self.is_running = True

    def run(self):
        space_scenter = gl.get_value('space_center')
        ut = space_scenter.ut
        now = int(ut * 1000)
        delt_ms = now - self.start_time
        if delt_ms > self.interval:
            # print(delt_ms)
            self.start_time = now
            self.function(*self.args, **self.kwargs)

    def stop(self):
        self.is_running = False


class mytimer:
    def __init__(self):
        self.start_time = 0
        self.once = False
        pass

    def start_once(self):
        space_scenter = gl.get_value('space_center')
        ut = space_scenter.ut
        if (self.once == False):
            self.once = True
            self.start_time = int(ut*1000)

    def ms(self):
        space_scenter = gl.get_value('space_center')
        ut = space_scenter.ut
        return int(ut * 1000) - self.start_time


class mission:
    def __init__(self, strfirst, strend, parpare_func, loopfunction, condition, delaly_time):
        self.str_start = strfirst
        self.start_time = 0
        self.parpare_func = parpare_func
        self.loop_func = loopfunction
        self.condition = condition
        self.str_end = strend
        self.finished_delaytime = delaly_time

    def start(self):
        space_scenter = gl.get_value('space_center')
        ut = space_scenter.ut
        self.start_time = int(ut*1000)

    def time_havepassed(self, ms):
        space_scenter = gl.get_value('space_center')
        ut = space_scenter.ut
        now = int(ut * 1000)
        delt_ms = now - self.start_time
        return delt_ms > ms


class mission_sheduler:

    def __init__(self):
        self.mission_list = []
        self.stage = 0
        self.over = False
        self.delay_time = 0
        self.delay_start = 0
        self.next = False
        self.list_length = 0

    def add_mission(self, mission):
        self.mission_list.append(mission)
        self.list_length += 1

    #
    def start(self):
        if (self.list_length == 0):
            print("No mission")
            return
        # 任务前打印
        print(self.mission_list[self.stage].str_start)
        # 任务开始
        self.mission_list[self.stage].start()  # 记录任务开始时间
        self.mission_list[self.stage].parpare_func()  # 启动准备程序

    def run(self):
        space_scenter = gl.get_value('space_center')
        ut = space_scenter.ut
        now = int(ut * 1000)
        
        if (self.over == True):
            return

        # 满足条件切换任务
        if (self.next == False and self.mission_list[self.stage].condition() == True):
            # 任务后打印
            print(self.mission_list[self.stage].str_end)
            # 任务结束后保持时间
            self.delay_time = self.mission_list[self.stage].finished_delaytime
            self.delay_start = int(ut*1000)
            self.next = True  # 允许任务切换

        # 延时切换任务
        if (self.next == True and now - self.delay_start > self.delay_time):
            self.next = False
            self.stage += 1
            # print('self.stage:', self.stage)
            # 任务调度结束
            if (self.stage == self.list_length):
                print('mission finished')
                self.over = True
                return
            # 任务前打印
            print(self.mission_list[self.stage].str_start)
            # 任务开始
            self.mission_list[self.stage].start()  # 记录任务开始时间
            self.mission_list[self.stage].parpare_func()  # 启动准备程序
        elif (self.next == True):
            print("delay:(%d)" % (int(now - self.delay_start)/1000), end='\r')

        # 运行循环任务程序
        self.mission_list[self.stage].loop_func()

    def over(self):
        return self.over
