from time import sleep, time
import krpc
import math
import global_var as gl
from math import sin, cos, pi
from pid import PID
from timer import RepeatedTimer, mission_sheduler, mission, mytimer

from mission import msin1_cond, msin1_func, msin1_ppr, msin2_cond, msin2_func, msin2_ppr, msin3_cond, msin3_func, msin3_ppr, msin4_ppr, msin4_func, msin4_cond

gl._init()
gl.set_value('targetAltitude', 1000)
gl.set_value('altitude', 0)  # 垂直向下高度
gl.set_value('mean_altitude', 0)  # 海平面高度
gl.set_value('velocity', 0)
gl.set_value('pre_launch_altitude',0)


conn = krpc.connect(name='Sub-orbital flight')
vessel = conn.space_center.active_vessel
space_center = conn.space_center
body = vessel.orbit.body
gl.set_value('vessel', vessel)
gl.set_value('space_center', space_center)
gl.set_value('conn', conn)
# gl.set_value('ut',space_center.ut) 这样获取的值不能跟新

flight_info = vessel.flight()
reference_frame = vessel.orbit.body.reference_frame

############################## VBA 大楼顶部参考系 ####################################
create_relative = conn.space_center.ReferenceFrame.create_relative

# 经纬高度 of the VAB
landing_latitude = -(0+(5.0/60)+(48.38/60/60))
landing_longitude = -(74+(37.0/60)+(12.2/60/60))
landing_altitude = 111

# 地固系的位置
# Determine landing site reference frame
# (orientation: x=zenith, y=north, z=east)
landing_position = body.surface_position(
    landing_latitude, landing_longitude, body.reference_frame)
q_long = (
    0,
    sin(-landing_longitude * 0.5 * pi / 180),
    0,
    cos(-landing_longitude * 0.5 * pi / 180)
)
q_lat = (
    0,
    0,
    sin(landing_latitude * 0.5 * pi / 180),
    cos(landing_latitude * 0.5 * pi / 180)
)
# 得到以VBA发射台为原点 x=zenith, y=north, z=east的坐标系
landing_reference_frame = create_relative(
                                # 经纬度变换
                                create_relative(
                                    create_relative(
                                        body.reference_frame,
                                        landing_position,
                                        q_long),

                                    (0, 0, 0),
                                    q_lat),
                          (landing_altitude, 0, 0))

# Draw axes
# 标记单位轴 报错
# conn.drawing.add_line((0, 0, 0), (1, 0, 0), landing_reference_frame)
# conn.drawing.add_line((0, 0, 0), (0, 1, 0), landing_reference_frame)
# conn.drawing.add_line((0, 0, 0), (0, 0, 1), landing_reference_frame)
################################### VBA 大楼顶部参考系 ############################################
# 0-360度 0度在y轴上
def angle_of_vector_between_Yaxis(x1,y1):
    x2 = 0
    y2 = 1
    dp = x1*x2 + y1*y2
    if dp == 0:
        return 0
    um = math.sqrt(x1**2 + y1**2)
    vm = math.sqrt(x2**2 + y2**2)
    angle_0_180 = math.acos(dp / (um*vm)) * (180. / math.pi)
    if(x1 < 0):
        return 360 - angle_0_180
    else:
        return angle_0_180



def get_g_of_altitude():
    gl.set_value('mean_altitude',mean_altitude())
    return body.gravitational_parameter/(mean_altitude() + 600000)**2


def getThisHeightTarget_V(hx):
    abs_h = abs(hx)
    g = get_g_of_altitude()
    # print(g)
    if (hx > 0):
        g = g*0.8
        target_v = math.sqrt(2*g*abs_h)
        return target_v
    else:
        F = vessel.max_thrust
        m = vessel.mass
        a = F/m - g
        a = a*0.3
        target_v = math.sqrt(2*a*abs_h)
        return -target_v


# def caculate(argv):
#     targetAltitude = gl.get_value('targetAltitude')
#     target_speed = pid_altitude.PID(targetAltitude, altitude())

#     velocity = vessel.flight(vessel.orbit.body.reference_frame).velocity
#     vessel.control.throttle = pid_speed.PID(target_speed*100, -velocity[2])


def caculate2(argv):
# 高度控制
    gl.set_value('altitude', altitude())
    targetAltitude = gl.get_value('targetAltitude')
    target_v = getThisHeightTarget_V(targetAltitude-altitude())
    velocity = vessel.flight(reference_frame).vertical_speed
    gl.set_value('velocity',velocity)
    delt_v = velocity - target_v

    F = vessel.max_thrust
    m = vessel.mass
    a = 0
    g = get_g_of_altitude()
    if(targetAltitude-altitude() > 0):
        a = g*0.8
    else:
        a = (F/m - g)*0.3
    print("     高度:%.1f " % altitude(), "速度:%.1f " % vessel.flight(
        reference_frame).speed, "油门:%.2f " % vessel.control.throttle, "deltV:%.1f " % delt_v,
        "velocity%.1f " % velocity, "a:%.f " % a, "m:%.f" % m, "F:%.1f" % F, end='\r')
    # caculate PID
    # if (ms.over == False):
    if(F == 0):
        F = float('inf')
    # vessel.control.throttle = pid_height.PID(0, delt_v) + m*g/F
    vessel.control.throttle = pid_height.PID(0, delt_v)

    # 位置控制
    speed_x = vessel.flight(landing_reference_frame).velocity[2]
    speed_y = vessel.flight(landing_reference_frame).velocity[1]

    now_x = vessel.position(landing_reference_frame)[2]
    now_y = vessel.position(landing_reference_frame)[1]
    # print("n_x:%.1f"%now_x,"n_y:%.1f"%now_y,)

    # x方向,计算x方向的目标速度
    tar_x_speed = pid_xy.PID(0,now_x)
    # y方向,计算y方向的目标速度
    tar_y_speed = pid_xy.PID(0,now_y)
    # print("tspeed_x:%.1f"%tar_x_speed,"tspeed_y:%.1f"%tar_y_speed,)


    x_acc = pid_xy_speed.PID(tar_x_speed,speed_x)
    y_acc = pid_xy_speed.PID(tar_y_speed,speed_y)
    # print("acc_x:%.1f"%x_acc,"acc_y:%.1f"%y_acc,)

    # x_out = -pid_xy_acc.PID(0,x_acc)
    # y_out = -pid_xy_acc.PID(0,y_acc)
    
    x_out = x_acc
    y_out = y_acc
    # print("out_x:%.1f"%x_out,"out_y:%.1f"%y_out)
    # 根据目标速度合成方向
    tar_angle = angle_of_vector_between_Yaxis(x_out,y_out)
    # print("angle:%.1f"%tar_angle)
    vessel.auto_pilot.target_heading = tar_angle
    # 通过绝对值计算倾角大小，记在该方向上施加的加速度
    abs_error = math.sqrt(x_out**2 + y_out**2)
    out_acc = abs(pid_pitch.PID(0,abs_error))
    if(out_acc > 35):
        out_acc = 35
    vessel.auto_pilot.target_pitch = 90 - out_acc



vessel.control.throttle = 0
vessel.control.activate_next_stage()
vessel.auto_pilot.target_pitch_and_heading(90, 90)
vessel.auto_pilot.engage()

msin1 = mission('\nmsin1 start\n', '\nmsin1 end hoding 5s\n',
                msin1_ppr, msin1_func, msin1_cond, 5000)
msin2 = mission('\nmsin2 start\n', '\nmsin2 end \n',
                msin2_ppr, msin2_func, msin2_cond, 0000)
msin3 = mission('\nmsin3 start\n', '\nmsin3 end hoding 2s\n',
                msin3_ppr, msin3_func, msin3_cond, 0000)
msin4 = mission('\nlanding start\n', '\nlanged end\n',
                msin4_ppr, msin4_func, msin4_cond, 0)
ms = mission_sheduler()
ms.add_mission(msin1)
# ms.add_mission(msin2)
# ms.add_mission(msin3)
ms.add_mission(msin4)
ms.start()


pid_xy = PID(0.1,0,0)
pid_xy_speed = PID(1,0,0.001)


pid_pitch = PID(1, 0, 0.00)

# pid_altitude = PID(0.03, 0, 0.1)
# pid_speed = PID(0.01, 0, 0.002)
pid_height = PID(0.1, 0.000, 0.0)



mean_altitude = conn.add_stream(getattr, flight_info, 'mean_altitude')

with conn.stream(getattr, flight_info, 'mean_altitude') as altitude:
    gl.set_value('pre_launch_altitude',altitude())
    rt = RepeatedTimer(10, caculate2, "")
    rt.start()
    try:
        while True:
            rt.run()
            ms.run()
            # print("(%.1f, %.1f, %.1f)"%vessel.position(landing_reference_frame))
            # print(angle_of_vector_between_Yaxis())
            # print(body.gravitational_parameter/(mean_altitude + 600000)**2) # 测量g
            # print(body.gravitational_parameter,"aaaa")
            # print(space_center.g,"gggg")
            # print(vessel.situation,vessel.situation == space_center.VesselSituation.landed)
            # print("ut:%f"%space_center.ut)
            # print("(%.1f, %.1f, %.1f)"%vessel.position(reference_frame))
            # print(body.gravitational_parameter/(-vessel.position(reference_frame)[2])**2)
            # print(math.sqrt(body.gravitational_parameter/9.81))
            # vessel.auto_pilot.target_pitch_and_heading()
            pass
    finally:
        rt.stop()


#        右方                  北方              高度
# (159780.412613073, -1018.4072280004623, -578409.4365506402)

# 往右
# (159793.31700708732, -1018.160835593939, -578405.2258461241)
# 往左
# (159767.27429005445, -1018.275744378567, -578412.3614123369)

# 往下
# (159780.79059593394, -1027.8156818896534, -578409.2856779026)
# 往上
# (159780.62555716533, -1011.6887883692982, -578409.3982780502)
