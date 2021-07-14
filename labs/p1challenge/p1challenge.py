"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Phase 1 Challenge - Cone Slaloming
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np
from enum import IntEnum
from nptyping import NDArray
from typing import Any, Tuple, List, Optional

sys.path.insert(0, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Add any global variables here

MIN_CONTOUR_AREA = 30

# HSV values for color identification.
BLUE = ((100,150,150), (120,255,255),"BLUE") 
RED = ((170,50,50),(10,255,255),"RED")

# Car values.
speed = 0.0
angle = 0.0

# Camera values.
contour_center = None
contour_area = 0

cur_color = None

# Color distances.
red_distance = 0.0
blue_distance = 0.0

# Color contour centers.
red_center = None
blue_center = None

# Color contour areas.
red_contour_area = 0.0
blue_contour_area = 0.0
########################################################################################
# Functions
########################################################################################

class State(IntEnum):
    redReg = 0
    blueReg = 1
    psdBlue = 2
    psdRed = 3
    reverse = 4
    search = 5
    stop = 6

cur_state = State.search

def start():
    """
    This function is run once every time the start button is pressed
    """
    # Global variables.
    global speed
    global angle
    global cur_color

    # Variables.
    speed = 0.0
    angle = 0.0
    cur_color = None

    # Have the car begin at a stop
    rc.drive.set_speed_angle(speed,angle)

    # Print start message
    print(">> Phase 1 Challenge: Cone Slaloming")

# def update_contour():
#     """
#     Finds contours in the current color image and uses them to update contour_center
#     and contour_area
#     """
#     global contour_center
#     global contour_area
#     global cur_color

#     image = rc.camera.get_color_image()


#     if image is None:
#         contour_center = None
#         contour_area = 0
#     else:
#         color = (RED,BLUE)

#         for x in color:
#             contours = rc_utils.find_contours(image, x[0], x[1])
#             cur_color = x[2]
#             if len(contours) != 0:
#                 break

#         # Select the largest contour
#         contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)

#         if contour is not None:
#             # Calculate contour information
#             contour_center = rc_utils.get_contour_center(contour)
#             contour_area = rc_utils.get_contour_area(contour)

#             # Draw contour onto the image
#             rc_utils.draw_contour(image, contour)
#             rc_utils.draw_circle(image, contour_center)

#         else:
#             contour_center = None
#             contour_area = 0

#         # Display the image to the screen
#         rc.display.show_color_image(image)

def get_mask(
    image: NDArray[(Any, Any, 3), np.uint8],
    hsv_lower: Tuple[int, int, int],
    hsv_upper: Tuple[int, int, int]
) -> NDArray[Any, Any]:
    """
    Returns a mask containing all of the areas of image which were between hsv_lower and hsv_upper.
    Args:
        image: The image (stored in BGR) from which to create a mask.
        hsv_lower: The lower bound of HSV values to include in the mask.
        hsv_upper: The upper bound of HSV values to include in the mask.
    """
    # Convert hsv_lower and hsv_upper to numpy arrays so they can be used by OpenCV
    hsv_lower = np.array(hsv_lower)
    hsv_upper = np.array(hsv_upper)

    # TODO: Use the cv.cvtColor function to switch our BGR colors to HSV colors
    image = cv.cvtColor(image, cv.COLOR_BGR2HSV)

    # TODO: Use the cv.inRange function to highlight areas in the correct range
    mask = cv.inRange(image, hsv_lower, hsv_upper)

    return mask

def getCones():
    
    global cur_color
    global red_distance
    global blue_distance
    global red_center
    global blue_center
    global red_contour_area
    global blue_contour_area
    
    color_img = rc.camera.get_color_image()
    depth_img = rc.camera.get_depth_image()

    depth_image_adjust = (depth_img - 0.01) % 9999
    depth_image_adjust_blur = cv.GaussianBlur(depth_image_adjust, (11,11), 0)

    red_contours = rc_utils.find_contours(color_img, RED[0], RED[1])
    red_contour = rc_utils.get_largest_contour(red_contours, 30)
    
    blue_contours = rc_utils.find_contours(color_img, BLUE[0], BLUE[1])
    blue_contour = rc_utils.get_largest_contour(blue_contours, 30)  

    red_distance = 0
    blue_distance = 0

    red_contour_area = 0 
    blue_contour_area = 0
    
    mask_red = get_mask(color_img, RED[0], RED[1])
    masked_depth_image_red = cv.bitwise_and(depth_image_adjust_blur, depth_image_adjust_blur, mask=mask_red)

    mask_blue = get_mask(color_img, BLUE[0], BLUE[1])
    masked_depth_image_blue = cv.bitwise_and(depth_image_adjust_blur, depth_image_adjust_blur, mask=mask_blue)


    if red_contour is not None:
        red_contour_area = rc_utils.get_contour_area(red_contour)
        red_center = rc_utils.get_contour_center(red_contour)
        red_center_y = rc_utils.clamp(red_center[1],0,479)
        red_center_x = rc_utils.clamp(red_center[0],0,639)
        #red_distance = rc_utils.get_closest_pixel(masked_depth_image_red)
        red_distance = depth_image_adjust_blur[red_center_y][red_center_x]
        #rc_utils.draw_circle(color_img, red_center, rc_utils.ColorBGR.yellow.value)
        rc.display.show_depth_image(color_img, points=[red_center])
        print("access red")

    if blue_contour is not None:
        blue_contour_area = rc_utils.get_contour_area(blue_contour)
        blue_center = rc_utils.get_contour_center(blue_contour)
        blue_center_y = rc_utils.clamp(blue_center[1],0,479)
        blue_center_x = rc_utils.clamp(blue_center[0],0,639)
        # blue_distance = rc_utils.get_closest_pixel(masked_depth_image_blue)
        blue_distance = depth_image_adjust_blur[blue_center_y][blue_center_x]
        # rc_utils.draw_circle(color_img, blue_center, rc_utils.ColorBGR.yellow.value)
        rc.display.show_depth_image(color_img, points=[blue_center])
        print("access blue")

    """  
    if (red_contour_area is not None) and (red_contour_area > blue_contour_area) :
        
        rc_utils.draw_contour(color_img, red_contour)
        rc_utils.draw_circle(color_img, red_center)       
    if (blue_contour_area is not None) and (blue_contour_area > red_contour_area):
        
        rc_utils.draw_contour(color_img, blue_contour)
        rc_utils.draw_circle(color_img, blue_contour) 
    """
    print("Distance red:" + str(red_distance))
    print("Distance blue:" + str(blue_distance))
    
def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    getCones()
   # update_contour

    color_img = rc.camera.get_color_image()
    depth_img = rc.camera.get_depth_image()
    
    # Global variables.
    global speed
    global angle
    global cur_state    
    global red_distance
    global blue_distance
    global cur_color
    global red_contour_area
    global blue_contour_area

    # Variables.
    speed = 0.0
    angle = 0.0

    color_img_x = rc.camera.get_width()
    color_img_y = rc.camera.get_height()

    if red_contour_area > blue_contour_area:
        cur_color = 'RED'
    else: 
        cur_color = 'BLUE'    
        
    if blue_distance == 0 and red_distance == 0:
        if cur_color == "BLUE":
            cur_state = State.psdBlue
        elif cur_color == "RED":
            cur_state = State.psdRed

    elif blue_distance != 0:
        cur_state = State.blueReg

    elif red_distance !=0:
        cur_state = State.redReg

    if  cur_state == State.psdRed:
        angle = -1               
    elif cur_state == State.psdBlue:
        angle = 1
    
    if cur_state == State.blueReg:
        point = rc_utils.remap_range(blue_distance, 40, 130, color_img_x, color_img_x *3 //4, True)
        speed = 1
        angle = rc_utils.remap_range(blue_center[1], point, color_img_x //2 , 0 ,-1 ,True)
        
    elif cur_state == State.redReg:
        point = rc_utils.remap_range(red_distance, 40, 130, 0, color_img_x // 4, True)
        speed = 1
        angle = rc_utils.remap_range(red_center[1], point, color_img_x //2 , 0 ,1 ,True)

    print(color_img_x)
    print(color_img_y)
        
    

    rc.drive.set_speed_angle(speed,angle)
########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, None)
    rc.go()
