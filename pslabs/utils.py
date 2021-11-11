import py_thorlabs_ctrl.kinesis
py_thorlabs_ctrl.kinesis.init(r'C:\Program Files\Thorlabs\Kinesis')
from py_thorlabs_ctrl.kinesis.motor import KCubeDCServo

# put these and the motor groups in the init
kcube_yi = KCubeDCServo(27258547,"rotation")
kcube_ya = KCubeDCServo(27258530,"rotation")
kcube_z  = KCubeDCServo(27258551,"translation")
kcube_y  = KCubeDCServo(27258581,"translation")
kcube_x  = KCubeDCServo(27258584,"translation")
    
# Make lists to operate on sets of motors
all_motors  = [kcube_x,kcube_y,kcube_z,kcube_yi,kcube_ya]
translation = [kcube_x,kcube_y,kcube_z]
rotation    = [kcube_yi,kcube_ya]
left_group  = [kcube_x,kcube_y]
right_group = [kcube_yi,kcube_ya,kcube_z]