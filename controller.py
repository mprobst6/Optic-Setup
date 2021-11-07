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
import time

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
up = (0,1); down = (0,-1); left = (1,0); right = (-1,0)

# Ranges
translation_range = 25 # mm
rotation_range = 12 # mm

# Safety edges
buffer = 0.5 # mm need a way to stop the motor when it reaches the buffer, but then move it just inside the buffer so it can start moving the other direction

# Center commands
translation_center = translation_range/2; rotation_center = rotation_range/2

# Jump Distance
distance = 1  # hopefully this is in mm

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

for motor in all_motors:
    motor.create()
    motor.enable()

print('Ready for input')

class PS4Controller(object):
    """Class representing the PS4 controller. Pretty straightforward functionality."""

    controller = None
    axis_data = None
    button_data = None
    temp_button_data = None # temporary button data, used to tell whether a particular button was pressed or not
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
            self.temp_button_data = {}
            for i in range(self.controller.get_numbuttons()):
                self.button_data[i] = False
                self.temp_button_data[i] = False

        if not self.hat_data:
            self.hat_data = {}
            for i in range(self.controller.get_numhats()):
                self.hat_data[i] = (0, 0)

        while True:
            for event in pygame.event.get():

############################
### BUTTON DOWN COMMANDS ###
############################
                if event.type == pygame.JOYBUTTONDOWN:
                    self.temp_button_data[event.button] = True
                    if self.temp_button_data[options_button] == True: # emergency stop
                        for motor in all_motors:
                            motor.stop_immediate()
                    if self.temp_button_data[share_button] == True: # center command
                        for motor in all_motors:
                            motor.stop_immediate()
                        for motor in rotation:
                            motor.move_absolute(rotation_center)
                        for motor in translation:
                            motor.move_absolute(translation_center)
                    if self.temp_button_data[right_front_trigger] != self.button_data[right_front_trigger]: # stop z when the trigger is pressed
                        kcube_z.stop_immediate()
                    self.button_data[event.button] = self.temp_button_data[event.button] # set button data to the actual buttons

##########################
### BUTTON UP COMMANDS ###
##########################
                elif event.type == pygame.JOYBUTTONUP:
                    self.temp_button_data[event.button] = False
                    if self.button_data[right_front_trigger] != self.temp_button_data[right_front_trigger]: # detects releasing the button
                        for motor in rotation:
                            motor.stop_immediate()
                    self.button_data[event.button] = self.temp_button_data[event.button]
               
####################
### HAT COMMANDS ###
####################
                elif event.type == pygame.JOYHATMOTION:
                    self.hat_data[event.hat] = event.value
                    for i in range(self.controller.get_numhats()):
                        if self.button_data[right_front_trigger] == False: # no trigger, hats control x and y
                            if self.hat_data[i] == right:
                                kcube_x.move_relative(distance)
                            elif self.hat_data[i] == left:
                                kcube_x.move_relative(-distance)
                            elif self.hat_data[i] == up:
	                            kcube_y.move_relative(distance)
                            elif self.hat_data[i] == down:
                                kcube_y.move_relative(-distance)
                        elif self.button_data[right_front_trigger] == True: # trigger, hats control z
                            if self.hat_data[i] == up:
                                kcube_z.move_relative(distance)
                            elif self.hat_data[i] == down:
                                kcube_z.move_relative(-distance)

#########################
### JOYSTICK COMMANDS ###
#########################
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
                        if left_velocity_du == 0: # calls stop_immediate when the velocity is zero, buggy otherwise
                            kcube_x.stop_immediate()
                        else:
                            kcube_x.velocity(left_velocity_du)
# Controls motion in the y direction
                    elif event.axis == vertical_left_joystick:
                        if left_velocity_du == 0: # calls stop_immediate when the velocity is zero
                            kcube_y.stop_immediate()
                        else:
                            kcube_y.velocity(left_velocity_du)
# When the trigger is held, control the yi
                    elif event.axis == horizontal_right_joystick:
                        if self.button_data[right_front_trigger] == True:
                            if right_velocity_du == 0:
                                kcube_yi.stop_immediate()
                            else:
                                kcube_yi.velocity(right_velocity_du)
# right/left on the left joystick does nothing when the right trigger is not held because only up and down controls the z
                        else:
                            pass
# When the trigger is held, control ya
                    elif event.axis == vertical_right_joystick:
                        if self.button_data[right_front_trigger] == True:
                            if right_velocity_du == 0:
                                kcube_ya.stop_immediate()
                            else:
                                kcube_ya.velocity(right_velocity_du)
# else control z
                        else: # control z axis when the button is not held
                            if right_velocity_du == 0:
                                kcube_z.stop_immediate()
                            else:
                                kcube_z.velocity(right_velocity_du)
if __name__ == "__main__":
    ps4 = PS4Controller()
    ps4.init()
    ps4.listen()
