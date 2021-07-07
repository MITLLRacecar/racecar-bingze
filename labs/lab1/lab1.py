"""
Copyright MIT and Harvey Mudd College
MIT License
Summer 2020

Lab 1 - Driving in Shapes
"""

########################################################################################
# Imports
########################################################################################

import sys

sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################

rc = racecar_core.create_racecar()

# Put any global variables here
counter = 0
isDriving = False
type = 0
########################################################################################
# Functions
########################################################################################


def start():
    """
    This function is run once every time the start button is pressed
    """
    # Begin at a full stop
    global counter
    global isDriving
    global type

    counter = 0
    isDriving = False
    type = 0

    rc.drive.stop()

    # Print start message
    # TODO (main challenge): add a line explaining what the Y button does
    print(
        ">> Lab 1 - Driving in Shapes\n"
        "\n"
        "Controls:\n"
        "    Right trigger = accelerate forward\n"
        "    Left trigger = accelerate backward\n"
        "    Left joystick = turn front wheels\n"
        "    A button = drive in a circle\n"
        "    B button = drive in a square\n"
        "    X button = drive in a figure eight\n"
    )


def update():
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    global counter
    global isDriving
    global type

    # TODO (warmup): Implement acceleration and steering
    rTrigger = rc.controller.get_trigger(rc.controller.Trigger.RIGHT)
    lTrigger = rc.controller.get_trigger(rc.controller.Trigger.LEFT)
    (lJoyX, lJoyY) = rc.controller.get_joystick(rc.controller.Joystick.LEFT)
    rc.drive.set_speed_angle((rTrigger - lTrigger), lJoyX)

    if rc.controller.was_pressed(rc.controller.Button.A):
        print("Driving in a circle...")
        # TODO (main challenge): Drive in a circle
        counter = 0
        type = 1
        isDriving = True
    


    # TODO (main challenge): Drive in a square when the B button is pressed
    if rc.controller.was_pressed(rc.controller.Button.B):
        print("Driving in a square...")
        counter = 0
        type = 2
        isDriving = True

    # TODO (main challenge): Drive in a figure eight when the X button is pressed
    if rc.controller.was_pressed(rc.controller.Button.X):
        print("Driving in a figure eight...")
        counter = 0
        type = 3
        isDriving = True
    # TODO (main challenge): Drive in a shape of your choice when the Y button
    # is pressed
    if rc.controller.was_pressed(rc.controller.Button.Y):
        print("Driving in a triangle...")
        counter = 0
        type = 4
        isDriving = True

    if isDriving:
        if type == 1:
            counter += rc.get_delta_time()

            if counter < 5:
                rc.drive.set_speed_angle(1,1)
            else:
                rc.drive.set_speed_angle(0,1)
                rc.drive.stop()
                isDriving = False

        if type == 2:
            counter += rc.get_delta_time()
            if counter < 1:
                rc.drive.set_speed_angle(1,0)
            elif counter < 3:
                rc.drive.set_speed_angle(0.66,1)
            elif counter < 5:
                rc.drive.set_speed_angle(1,0)
            elif counter < 7:
                rc.drive.set_speed_angle(0.15,1)
            elif counter < 9:
                rc.drive.set_speed_angle(1,0)
            elif counter < 11:
                rc.drive.set_speed_angle(0.44,1)
            elif counter < 13:
                rc.drive.set_speed_angle(1,0)
            else:
                rc.drive.stop()
                isDriving = False

        if type == 3:
            counter += rc.get_delta_time()
            if counter < 5:
                rc.drive.set_speed_angle(1,1)
            elif counter < 10:
                rc.drive .set_speed_angle(1,-1)
            else:
                rc.drive.stop()
                isDriving = False

        if type == 4:
            counter += rc.get_delta_time()
            if counter < 1:
                rc.drive.set_speed_angle(1,0)
            elif counter < 3:
                rc.drive.set_speed_angle(1,1)
            elif counter < 5:
                rc.drive.set_speed_angle(1,0)
            elif counter < 8:
                rc.drive.set_speed_angle(0.7,1)
            elif counter < 10:
                rc.drive.set_speed_angle(1,0)

########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update)
    rc.go()
