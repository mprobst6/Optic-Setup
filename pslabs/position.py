import numpy as np
import py_thorlabs_ctrl.kinesis
py_thorlabs_ctrl.kinesis.init(r'C:\Program Files\Thorlabs\Kinesis') 
from py_thorlabs_ctrl.kinesis.motor import KCubeDCServo
import time

kcube_x = KCubeDCServo(27258584)
kcube_x.create(); kcube_x.enable()
kcube_x.home()
time.sleep(10)
print("starting move now")
for j in range(20):
    print("moving for the {}th time".format(j))
    kcube_x.move_relative(1)
    for i in range(10):
        kcube_x.get_position()
        print("Device moving: {}".format(kcube_x.get_status()))
        time.sleep(0.5)


### The motors overshoot the desired position then return to it
### The status turns to "IsMoving = False" before it really has stopped
### However, the positon appears to be exact, at least within several decimal places
