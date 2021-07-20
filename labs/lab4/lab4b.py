"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 4B - LIDAR Wall Following
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

# Add any global variables here
FRONT_WINDOW = (-10, 10)
RIGHT_FRONT_WINDOW = (40, 50)
LEFT_FRONT_WINDOW = (310, 320)
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
    print(">> Lab 4B - LIDAR Wall Following")


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    speed = 1
    angle = 0

    # TODO: Follow the wall to the right of the car without hitting anything.

    scan = rc.lidar.get_samples()
    
    _, rf_dist = rc_utils.get_lidar_closest_point(scan, RIGHT_FRONT_WINDOW)
    _, lf_dist = rc_utils.get_lidar_closest_point(scan, LEFT_FRONT_WINDOW)
    _, front_dist = rc_utils.get_lidar_closest_point(scan, FRONT_WINDOW)
    if front_dist < 100:
        speed = rc_utils.remap_range(front_dist, 0, 100, .5, .8)

    if rf_dist > lf_dist:
        dif_dist_r = rc_utils.clamp(rf_dist - lf_dist, 0, 50)
        angle = rc_utils.remap_range(dif_dist_r, 0, 50, 0, 1)
    elif lf_dist > rf_dist:
        dif_dist_l = rc_utils.clamp(lf_dist - rf_dist, 0, 50)
        angle = rc_utils.remap_range(dif_dist_l, 0, 50, 0, -1)

    if rf_dist > 200 and lf_dist > 200 and front_dist > 200:
        angle = 0

    rc.drive.set_speed_angle(speed, angle)
    pass

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
