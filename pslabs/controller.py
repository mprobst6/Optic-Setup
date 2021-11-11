import pygame
from utils import *
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

# Ranges
TRANSLATION_RANGE = 25 # mm
ROTATION_RANGE = 12 # mm

# Center commands
translation_center = TRANSLATION_RANGE/2; rotation_center = ROTATION_RANGE/2

class PS4Controller(object):
    """Class representing the PS4 controller. Pretty straightforward functionality."""

    controller = None
    axis_data = None
    button_data = None
    temp_button_data = None # temporary button data, used to tell whether a particular button was pressed or not
    hat_data = None


    # Specify the move distance
    move_distance = 1
    
    # Safety edges
    buffer = 0.5 # mm need a way to stop the motor when it reaches the buffer, but then move it just inside the buffer so it can start moving the other direction
    MAX_SPEED = 1777830

	# Hat Mapping
    UP = (0,1); DOWN = (0,-1); LEFT = (1,0); RIGHT = (-1,0)
	
    for motor in all_motors:
        motor.create()
        motor.enable()



    def __init__(self):
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
                    if self.temp_button_data[square_button] == True: # emergency stop
                        for motor in self.all_motors:
                            motor.stop_immediate()
                    if self.temp_button_data[share_button] == True: # soft reset, disables all motors and resets them
                        for motor in self.all_motors:
                            motor.reset()
                    if self.temp_button_data[x_button] == True: # center command
                        for motor in self.all_motors:
                            motor.stop_immediate()
                        for motor in self.rotation:
                            motor.move_absolute(rotation_center)
                        for motor in self.translation:
                            motor.move_absolute(translation_center)
                    if self.temp_button_data[right_front_trigger] != self.button_data[right_front_trigger]: # stop z when the trigger is pressed
                        self.kcube_z.stop_immediate()
                    self.button_data[event.button] = self.temp_button_data[event.button] # set button data to the actual buttons

##########################
### BUTTON self.UP COMMANDS ###
##########################
                elif event.type == pygame.JOYBUTTONUP:
                    self.temp_button_data[event.button] = False
                    if self.button_data[right_front_trigger] != self.temp_button_data[right_front_trigger]: # detects releasing the button
                        for motor in self.rotation:
                            motor.stop_immediate()
                    self.button_data[event.button] = self.temp_button_data[event.button]
               
####################
### HAT COMMANDS ###
####################
                elif event.type == pygame.JOYHATMOTION:
                    self.hat_data[event.hat] = event.value
                    for i in range(self.controller.get_numhats()):
                        if self.button_data[right_front_trigger] == False: # no trigger, hats control x and y
                            if self.hat_data[i] == self.RIGHT:
                                self.kcube_x.move_relative(self.move_distance)
                            elif self.hat_data[i] == self.LEFT:
                                self.kcube_x.move_relative(-self.move_distance)
                            elif self.hat_data[i] == self.UP:
	                            self.kcube_y.move_relative(self.move_distance)
                            elif self.hat_data[i] == self.DOWN:
                                self.kcube_y.move_relative(-self.move_distance)
                        elif self.button_data[right_front_trigger] == True: # trigger, hats control z
                            if self.hat_data[i] == self.UP:
                                self.kcube_z.move_relative(self.move_distance)
                            elif self.hat_data[i] == self.DOWN:
                                self.kcube_z.move_relative(-self.move_distance)

#########################
### JOYSTICK COMMANDS ###
#########################
                elif event.type == pygame.JOYAXISMOTION:
# First two if statements set the velocity based on whether the button has been pressed or not
                    if event.axis == horizontal_left_joystick or event.axis == vertical_left_joystick: # controls the left joystick
# negative signs necessary to align the controller directions with the joystick directions
                        left_velocity_du = int(-round(event.value,2)*self.MAX_SPEED)
                        if self.button_data[left_joystick_button] == False:
                            left_velocity_du = 0.2*left_velocity_du # 20% of speed without button push
                    if event.axis == horizontal_right_joystick or event.axis == vertical_right_joystick: # controls the right joystick
                        right_velocity_du = int(-round(event.value,2)*self.MAX_SPEED)
                        if self.button_data[right_joystick_button] == False:
                            right_velocity_du = 0.2*right_velocity_du # 20% of speed without button push
                            
# Controls motion in the x direction
                    self.axis_data[event.axis] = round(event.value,2)
                    if event.axis == horizontal_left_joystick:
                        if left_velocity_du == 0: # calls stop_immediate when the velocity is zero, buggy otherwise
                            self.kcube_x.stop_immediate()
                        else:
                            self.kcube_x.velocity(left_velocity_du)
# Controls motion in the y direction
                    elif event.axis == vertical_left_joystick:
                        if left_velocity_du == 0: # calls stop_immediate when the velocity is zero
                            self.kcube_y.stop_immediate()
                        else:
                            self.kcube_y.velocity(left_velocity_du)
# When the trigger is held, control the yi
                    elif event.axis == horizontal_right_joystick:
                        if self.button_data[right_front_trigger] == True:
                            if right_velocity_du == 0:
                                self.kcube_yi.stop_immediate()
                            else:
                                self.kcube_yi.velocity(right_velocity_du)
# right/left on the left joystick does nothing when the right trigger is not held because only up and down controls the z
                        else:
                            pass
# When the trigger is held, control ya
                    elif event.axis == vertical_right_joystick:
                        if self.button_data[right_front_trigger] == True:
                            if right_velocity_du == 0:
                                self.kcube_ya.stop_immediate()
                            else:
                                self.kcube_ya.velocity(right_velocity_du)
# else control z
                        else: # control z axis when the button is not held
                            if right_velocity_du == 0:
                                self.kcube_z.stop_immediate()
                            else:
                                self.kcube_z.velocity(right_velocity_du)
if __name__ == "__main__":
    ps4 = PS4Controller()
    ps4.listen()
