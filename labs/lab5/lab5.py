"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 5 - AR Markers
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
RIGHT_FRONT_WINDOW = (40, 50)
LEFT_FRONT_WINDOW = (310, 320)
FRONT_WINDOW = (-10, 10)

MIN_CONTOUR_AREA = 30

# A crop window for the floor directly in front of the car
CROP_FLOOR = ((360, 0), (rc.camera.get_height(), rc.camera.get_width()))

# Colors, stored as a pair (hsv_min, hsv_max)
BLUE = ((88,245,199), (108,255,255))  # The HSV range for the color blue
# TODO (challenge 1): add HSV ranges for other colors
GREEN = ((35,43,46),(77,255,255))
RED = ((0,245,212),(10,255,255))

# >> Variables
speed = 0.0  # The current speed of the car
angle = 0.0  # The current angle of the car's wheels
contour_center = None  # The (pixel row, pixel column) of contour
contour_area = 0  # The area of contour
########################################################################################
# Functions
########################################################################################
class State(IntEnum):
    wallFollow = 0
    lineFollow = 1
    arMarkerLeft = 2
    arMarkerRight = 3

curState = State.wallFollow

def start():
    """
    This function is run once every time the start button is pressed
    """
    # Have the car begin at a stop
    rc.drive.stop()

    # Print start message
    print(">> Lab 5 - AR Markers")

def wallFollow():
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

def updateContour():
    global contour_center
    global contour_area

    image = rc.camera.get_color_image()

    if image is None:
        contour_center = None
        contour_area = 0
    else:
        # TODO (challenge 1): Search for multiple tape colors with a priority order
        # (currently we only search for blue)

        # Crop the image to the floor directly in front of the car
        image = rc_utils.crop(image, CROP_FLOOR[0], CROP_FLOOR[1])

        # Find all of the blue contours

        color = (BLUE,GREEN,RED)

        for x in color:
            contours = rc_utils.find_contours(image, x[0], x[1])
            if len(contours) != 0:
                break

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

def lineFollow():
    global speed
    global angle

    # Search for contours in the current color image
    updateContour()

    # Choose an angle based on contour_center

    imgX = rc.camera.get_width()
    
    if contour_center is not None:
        angle = rc_utils.remap_range(contour_center[1],0,imgX,-1,1)

    # Use the triggers to control the car's speed
    forwardSpeed = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    backSpeed = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    speed = forwardSpeed - backSpeed

    rc.drive.set_speed_angle(1, angle)

    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle)

    # Print the center and area of the largest contour when B is held down
    if rc.controller.is_down(rc.controller.Button.B):
        if contour_center is None:
            print("No contour found")
        else:
            print("Center:", contour_center, "Area:", contour_area)

def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    color_image = rc.camera.get_color_image()
    markers = rc_utils.get_ar_markers(color_image)

    # TODO: Turn left if we see a marker with ID 0 and right for ID 1
    # if markers is not None:
    #     first_marker = markers[0]
    #     if first_marker.get_id() == 0:
    #         first_marker = markers[1]
    #     elif first_marker.get_id() == 1:
    #         first_marker = markers[1]
    #     elif first_marker.get_id() == 199:
    #         first_marker = markers[1]
    #     elif first_marker.get_id() == 2:
    #         first_marker = markers[1]

    if curState == State.wallFollow:
        wallFollow()
    elif curState == State.lineFollow:
        lineFollow()
    # TODO: If we see a marker with ID 199, turn left if the marker faces left and right
    # if the marker faces right

    # TODO: If we see a marker with ID 2, follow the color line which matches the color
    # border surrounding the marker (either blue or red). If neither color is found but
    # we see a green line, follow that instead.


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
