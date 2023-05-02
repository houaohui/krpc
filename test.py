# import math
# import time
# import krpc
# conn = krpc.connect(name='Pitch/Heading/Roll')
# vessel = conn.space_center.active_vessel
# vessel.auto_pilot.reference_frame = vessel.surface_velocity_reference_frame
# vessel.auto_pilot.target_roll = -90
# # vessel.auto_pilot.target_pitch = 90
# # vessel.auto_pilot.target_heading = 0
# vessel.auto_pilot.engage()

# while True:
#     vessel.control.pitch = -1
#     pass

import time
from math import sin, cos, pi
import krpc

conn = krpc.connect(name='Landing Site')
vessel = conn.space_center.active_vessel
body = vessel.orbit.body
create_relative = conn.space_center.ReferenceFrame.create_relative

# Define the landing site as the top of the VAB
landing_latitude = -(0+(5.0/60)+(48.38/60/60))
landing_longitude = -(74+(37.0/60)+(12.2/60/60))
landing_altitude = 111

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
landing_reference_frame = \
    create_relative(
        create_relative(
            create_relative(
                body.reference_frame,
                landing_position,
                q_long),
            (0, 0, 0),
            q_lat),
        (landing_altitude, 0, 0))

# Draw axes
conn.drawing.add_line((0, 0, 0), (1, 0, 0), landing_reference_frame)
conn.drawing.add_line((0, 0, 0), (0, 1, 0), landing_reference_frame)
conn.drawing.add_line((0, 0, 0), (0, 0, 1), landing_reference_frame)

while True:
    time.sleep(1)