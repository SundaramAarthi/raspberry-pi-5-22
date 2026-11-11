import sys
from flap_gate import Flap
pin = int(sys.argv[1])
with Flap(pin=pin) as f:
    while True:
        cmd = input(f"pin {pin}, angle 30-150 (q to quit) > ").strip()
        if cmd == "q":
            break
        try:
            a = float(cmd)
        except ValueError:
            continue
        if 30 <= a <= 150:
            f.goto(a)
        else:
            print("use 30 to 150 only")
