from time import sleep, time
import global_var as gl
import krpc
import math
from timer import mytimer


def is_in_target_height(target_height, speed):
    altitude = gl.get_value('altitude')
    # print("altitude:%.1f"%altitude,"targetH:%.1f"%target_height)
    return abs(altitude-target_height) < 1 and abs(speed) < 0.3


def msin1_ppr():
    print("set targetAltitude: 10000\n")
    gl.set_value('targetAltitude', 10000)

once = False
def msin1_func():
    global once
    velocity = gl.get_value('velocity')
    vessel = gl.get_value('vessel')
    altitude = gl.get_value('altitude')
    targetAltitude = gl.get_value('targetAltitude')
    if(velocity > 1):
        vessel.control.gear = False
    if(altitude > targetAltitude*0.8 and once ==False):
        once = True
        vessel.control.activate_next_stage()


def msin1_cond():
    targetAltitude = gl.get_value('targetAltitude')
    velocity = gl.get_value('velocity')
    return is_in_target_height(targetAltitude, velocity)


def msin2_ppr():
    print("set targetAltitude: 250\n")
    gl.set_value('targetAltitude', 250)

def msin2_func():
    pass


def msin2_cond():
    targetAltitude = gl.get_value('targetAltitude')
    velocity = gl.get_value('velocity')
    return is_in_target_height(targetAltitude, velocity)


def msin3_ppr():
    print("set targetAltitude: 100\n")
    gl.set_value('targetAltitude', 100)
    vessel = gl.get_value('vessel')
    # vessel.control.activate_next_stage()
    # vessel.control.throttle = 0


def msin3_func():
    pass


def msin3_cond():
    targetAltitude = gl.get_value('targetAltitude')
    velocity = gl.get_value('velocity')
    return is_in_target_height(targetAltitude, velocity)

tm = mytimer()
def msin4_ppr():
    # tm.start_once()
    # pre_launch_altitude = gl.get_value('pre_launch_altitude')

    # print("set targetAltitude: %.1f"%(pre_launch_altitude + 1.0),end = '\n')
    # gl.set_value('targetAltitude', pre_launch_altitude + 1.0)
    gl.set_value('targetAltitude', 181+ 4.0)
    # vessel.control.activate_next_stage()
    vessel = gl.get_value('vessel')
    vessel.control.gear = True
    pass

def msin4_func():
    # set_altitude = 100 - tm.ms()/1700
    # gl.set_value('targetAltitude',set_altitude)
    pass
    # tm.start_once()
    


def msin4_cond():
    vessel = gl.get_value('vessel')
    space_center = gl.get_value("space_center")
    velocity = gl.get_value('velocity')
    altitude = gl.get_value('altitude')
    targetAltitude = gl.get_value('targetAltitude')
    

    if (altitude < targetAltitude and velocity > 0):
        print(velocity, "sssssssssssssssss\n")
        gl.set_value('targetAltitude', 0)
    # gl.set_value('targetAltitude',250 - tm.ms()/800)

    return (vessel.situation == space_center.VesselSituation.landed and velocity > 0)
