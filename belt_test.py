import time
from pydobotplus import Dobot
d = Dobot(port="/dev/ttyACM0")
print("Belt ON")
d.conveyor_belt(0.5, direction=-1, interface=1)
time.sleep(3)
d.conveyor_belt(0, direction=-1, interface=1)
print("Belt OFF")
d.close()
