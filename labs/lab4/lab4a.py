"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 4A - LIDAR Safety Stop
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np

sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# >> Constants
# The (min, max) degrees to consider when measuring forward and rear distances
FRONT_WINDOW = (-10, 10)
REAR_WINDOW = (170, 190)

MIN_STOP_DISTANCE = 20  # cm
MAX_STOP_DISTANCE = 170  # cm
ALPHA = 0.2  # Amount to use current_speed when updating cur_speed

# Boundaries of the crop window used to only consider objects in front of the car


# Amount to increase stop distance (cm) per speed (cm/s) squared
STOP_DISTANCE_SCALE = 40.0 / 10000

# slow_distance / stop_distance
SLOW_DISTANCE_RATIO = 1.5

# >> Variables

########################################################################################
# Functions
########################################################################################


def start():
    """
    This function is run once every time the start button is pressed
    """
    # Have the car begin at a stop
    rc.drive.stop()

    # Print start message
    print(
        ">> Lab 4A - LIDAR Safety Stop\n"
        "\n"
        "Controls:\n"
        "    Right trigger = accelerate forward\n"
        "    Right bumper = override forward safety stop\n"
        "    Left trigger = accelerate backward\n"
        "    Left bumper = override rear safety stop\n"
        "    Left joystick = turn front wheels\n"
        "    A button = print current speed and angle\n"
        "    B button = print forward and back distances"
    )


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """

    
    # Use the triggers to control the car's speed
    rt = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    lt = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    
    # Calculate the distance in front of and behind the car
    scan = rc.lidar.get_samples()
    _, forward_dist = rc_utils.get_lidar_closest_point(scan, FRONT_WINDOW)
    _, back_dist = rc_utils.get_lidar_closest_point(scan, REAR_WINDOW)
    
    if not rc.controller.is_down(rc.controller.Button.RB):
        if 60 < forward_dist < MAX_STOP_DISTANCE:
            rt = rc_utils.clamp(rt, 0, 0.3)
        elif MIN_STOP_DISTANCE < forward_dist < 60:
            rt = 0
    
        if 60 < back_dist < MAX_STOP_DISTANCE:
            lt = rc_utils.clamp(lt, 0, 0.3)
        elif MIN_STOP_DISTANCE < back_dist < 60:
            lt = 0
    speed = rt - lt
    # Use the left joystick to control the angle of the front wheels
    angle = rc.controller.get_joystick(rc.controller.Joystick.LEFT)[0]

    rc.drive.set_speed_angle(speed, angle)

    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle)

    # Print the distance of the closest object in front of and behind the car
    if rc.controller.is_down(rc.controller.Button.B):
        print("Forward distance:", forward_dist, "Back distance:", back_dist)

    # Display the current LIDAR scan
    rc.display.show_lidar(scan)

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()