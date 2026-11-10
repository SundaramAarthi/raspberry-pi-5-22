import time
from flap_gate import Flap
from pydobotplus import Dobot

f2 = Flap(pin=13)
f2.goto(75)          # front flap to the edge
f = Flap(pin=18)
f.goto(145)          # back flap to the edge
d = Dobot(port="/dev/ttyACM0")
d.conveyor_belt(0.5, direction=-1, interface=1)
try:
    input("Belt on. Press Enter when the tomato is at the back flap...")
    f.goto(45)
    time.sleep(1.5)
    f.goto(145)
    time.sleep(0.5)
finally:
    d.conveyor_belt(0, direction=-1, interface=1)
    d.close()
    f.close()
    f2.close()
    print("Belt stopped")