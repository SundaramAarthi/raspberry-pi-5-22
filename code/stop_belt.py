from pydobotplus import Dobot
d = Dobot(port="/dev/ttyACM0")
d.conveyor_belt(0, direction=-1, interface=1)
d.close()
print("Belt stopped")
