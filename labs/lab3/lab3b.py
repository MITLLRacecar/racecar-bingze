"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 3B - Depth Camera Cone Parking
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np
from enum import IntEnum

sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Add any global variables here

MIN_CONTOUR_AREA = 30

# The HSV range for the color orange, stored as (hsv_min, hsv_max)
ORANGE = ((10, 100, 100), (20, 255, 255))

# >> Variables
speed = 0.0  # The current speed of the car
angle = 0.0  # The current angle of the car's wheels
contour_center = None  # The (pixel row, pixel column) of contour
contour_area = 0  # The area of contour

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
    print(">> Lab 3B - Depth Camera Cone Parking")

def update_contour():
    """
    Finds contours in the current color image and uses them to update contour_center
    and contour_area
    """
    global contour_center
    global contour_area

    image = rc.camera.get_color_image()

    if image is None:
        contour_center = None
        contour_area = 0
    else:
        # Find all of the orange contours
        contours = rc_utils.find_contours(image, ORANGE[0], ORANGE[1])

        # Select the largest contour
        contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

        if contour is not None:
            # Calculate contour information
            contour_center = rc_utils.get_contour_center(contour)
            contour_area = rc_utils.get_contour_area(contour)

            # Draw contour onto the image
            rc_utils.draw_contour(image, contour)
            rc_utils.draw_circle(image, contour_center)

        else:
            contour_center = None
            contour_area = 0

        # Display the image to the screen
        rc.display.show_color_image(image)

class State(IntEnum):
    search = 0
    obstacle = 1
    approach = 2
    stop = 3

curState = State.search

def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    # TODO: Park the car 30 cm away from the closest orange cone.
    # Use both color and depth information to handle cones of multiple sizes.
    # You may wish to copy some of your code from lab2b.py
    global speed
    global angle
    global curState
    # Search for contours in the current color image
    update_contour()

    imgX = rc.camera.get_width()

    depth_image = rc.camera.get_depth_image()
    depth_image_adjust = (depth_image - 0.01) % 9999
    depth_image_adjust_blur = cv.GaussianBlur(depth_image_adjust, (11,11), 0)

    contour_x = contour_center[1]
    contour_y = contour_center[0]

    if contour_center is not None:
        angle = rc_utils.remap_range(contour_center[1],0,imgX,-1,1)

    contour_distance = depth_image_adjust_blur[contour_y][contour_x]

    print(contour_distance)
    # TODO: Park the car 30 cm away from the closest orange cone
    if curState == State.search:
        rc.drive.set_speed_angle(0.5, 1)
        
        if contour_center is not None:
            curState = State.approach

    elif curState == State.approach:
       # rc.drive.set_speed_angle(0.5, angle)

        if contour_distance > 50:
            rc.drive.set_speed_angle(0.3,angle)
        elif contour_distance > 32:
           rc.drive.set_speed_angle(0.1,angle)
        elif contour_distance == 32:
            rc.drive.set_speed_angle(-0.1,angle)
        elif contour_distance < 32:
            curState = State.stop
            print("stop")

    elif curState == State.stop:
        rc.drive.set_speed_angle(0,0)

    pass


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
