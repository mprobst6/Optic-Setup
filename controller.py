#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file presents an interface for interacting with the Playstation 4 Controller
# in Python. Simply plug your PS4 controller into your computer using USB and run this
# script!
#
# NOTE: I assume in this script that the only joystick plugged in is the PS4 controller.
#       if this is not the case, you will need to change the class accordingly.
#
# Copyright © 2015 Clay L. McLeod <clay.l.mcleod@gmail.com>
#
# Distributed under terms of the MIT license.

import pygame
import py_thorlabs_ctrl.kinesis
py_thorlabs_ctrl.kinesis.init(r'C:\Program Files\Thorlabs\Kinesis')
from py_thorlabs_ctrl.kinesis.motor import KCubeDCServo

# Button Mapping
x_button = 0
circle_button = 1
square_button = 2
triangle_button = 3
left_front_trigger = 4
right_front_trigger = 5
share_button = 6
options_button = 7
left_joystick_button = 8
right_joystick_button = 9

# Joystick Mapping
horizontal_left_joystick = 0
vertical_left_joystick = 1
horizontal_right_joystick = 2
vertical_right_joystick = 3

# Hat Mapping
right = (0,1); left = (0,-1); up = (1,1); down = (1,-1)

# Center commands
translation_center = 12.5; rotation_center = 6

# Jump Distance
# jump_by =  # change in um
# distance = jump_by*   # some number of device units per mm

# Maximum Move Speed
max_speed = 1777830 # get_max_velocity_du # 1777830, du stands for device units

kcube_yi = KCubeDCServo(27258547)   
kcube_ya = KCubeDCServo(27258530)
kcube_z = KCubeDCServo(27258551)
kcube_y = KCubeDCServo(27258581)
kcube_x = KCubeDCServo(27258584)

# Make lists to operate on sets of motors
all_motors = [kcube_x,kcube_y,kcube_z,kcube_yi,kcube_ya]
translation = [kcube_x,kcube_y,kcube_z]
rotation = [kcube_yi,kcube_ya]
left_group = [kcube_x,kcube_y]
right_group = [kcube_yi,kcube_ya,kcube_z]


kcube_x.create(); kcube_y.create(); kcube_z.create(); kcube_yi.create(); kcube_ya.create()
kcube_x.enable(); kcube_y.enable(); kcube_z.enable(); kcube_yi.enable(); kcube_ya.enable()
print('Ready for input')

class PS4Controller(object):
    """Class representing the PS4 controller. Pretty straightforward functionality."""

    controller = None
    axis_data = None
    button_data = None
    hat_data = None

    def init(self):
        """Initialize the joystick components"""

        pygame.init()
        pygame.joystick.init()
        self.controller = pygame.joystick.Joystick(0)
        self.controller.init()

    def listen(self):
        """Listen for events to happen"""

        if not self.axis_data:
            self.axis_data = {}

        if not self.button_data:
            self.button_data = {}
            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False

        if not self.hat_data:
            self.hat_data = {}
            for i in range(self.controller.get_numhats()):
                self.hat_data[i] = (0, 0)

        while True:
            for event in pygame.event.get():


                if event.type == pygame.JOYBUTTONDOWN:
                    self.button_data[event.button] = True    
                    if self.button_data[options_button] == True:
                        for motor in all_motors:
                            motor.stop_immediate()
                    elif self.button_data[share_button] == True:
                        for motor in all_motors:
                            motor.stop()
                        for motor in rotation:
                            motor.move_absolute(rotation_center)
                        for motor in translation:
                            motor.move_absolute(translation_center)


                elif event.type == pygame.JOYBUTTONUP:
                    self.button_data[event.button] = False
                    # print('event.button:',event.button)
                    


                elif event.type == pygame.JOYHATMOTION:
                    self.hat_data[event.hat] = event.value
                    print(self.hat_data)
                    print('event.hat:',event.hat)
                    for i in range(self.controller.get_numhats()):
                        if self.button_data[right_front_trigger] == False:
                            if self.hat_data[i] == right:
                                kcube_x.move_absolute(distance)
                            elif self.hat_data[i] == left:
                                kcube_x.move_absolute(-distance)
                            elif self.hat_data[i] == up:
	                            kcube_y.move_absolute(distance)
                            elif self.hat_data[i] == down:
                                kcube_y.move_absolute(-distance)
                        elif self.button_data[right_front_trigger] == True:
                            if self.hat_data[i] == right:
                                print('hello')
                            elif self.hat_data[i] == left:
                                print('hello')
                            elif self.hat_data[i] == up:
                                print('hello')
                            elif self.hat_data[i] == down:
                                print('hello')


                elif event.type == pygame.JOYAXISMOTION:
# First two if statements set the velocity based on whether the button has been pressed or not
                    if event.axis == horizontal_left_joystick or event.axis == vertical_left_joystick: # controls the left joystick
# negative signs necessary to align the controller directions with the joystick directions
                        left_velocity_du = int(-round(event.value,2)*max_speed)
                        if self.button_data[left_joystick_button] == False:
                            left_velocity_du = 0.2*left_velocity_du # 20% of speed without button push
                    if event.axis == horizontal_right_joystick or event.axis == vertical_right_joystick: # controls the right joystick
                        right_velocity_du = int(-round(event.value,2)*max_speed)
                        if self.button_data[right_joystick_button] == False:
                            right_velocity_du = 0.2*right_velocity_du # 20% of speed without button push
                            
# Controls motion in the x direction
                    self.axis_data[event.axis] = round(event.value,2)
                    if event.axis == horizontal_left_joystick:
                        if left_velocity_du == 0: # calls stop when the velocity is zero, buggy otherwise
                            kcube_x.stop()
                        else:
                            kcube_x.velocity(left_velocity_du)
                            # print("x velocity: {}".format(left_velocity_du))
# Controls motion in the y direction
                    elif event.axis == vertical_left_joystick:
                        if left_velocity_du == 0: # calls stop when the velocity is zero
                            kcube_y.stop()
                        else:
                            kcube_y.velocity(left_velocity_du)
                            # print("y velocity {}".format(left_velocity_du))
# When the trigger is held, control the yi
                    elif event.axis == horizontal_right_joystick:
                        if self.button_data[right_front_trigger] == True:
                            if right_velocity_du == 0:
                                kcube_yi.stop()
                            else:
                                kcube_yi.velocity(right_velocity_du)
                                print("yi velocity: {}".format(right_velocity_du))
# right/left on the left joystick does nothing when the right trigger is not held because only up and down controls the z
                        else:
                            print("left right does nothing right now")
# When the trigger is held, control ya
                    elif event.axis == vertical_right_joystick:
                        if self.button_data[right_front_trigger] == True:
                            if right_velocity_du == 0:
                                kcube_ya.stop()
                            else:
                                kcube_ya.velocity(right_velocity_du)
                                print("ya velocity: {}".format(right_velocity_du))
# else control z
                        else: # control z axis when the button is not held
                            if right_velocity_du == 0:
                                kcube_z.stop()
                            else:
                                kcube_z.velocity(right_velocity_du)
                                print("z velocity: {}".format(right_velocity_du))
if __name__ == "__main__":
    ps4 = PS4Controller()
    ps4.init()
    ps4.listen()
