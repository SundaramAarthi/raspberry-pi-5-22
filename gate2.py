import time
from flap_gate import Flap

S1 = {"pin": 18, "straight": 135, "across": 100}  # servo 1, back side -> Ripe
S2 = {"pin": 13, "straight": 75, "across": 120}   # servo 2, front side -> Unripe
HOLD_S = 7.0

class TwoFlaps:
    def __init__(self):
        self.f1 = Flap(pin=S1["pin"]); self.f1.goto(S1["straight"])
        self.f2 = Flap(pin=S2["pin"]); self.f2.goto(S2["straight"])

    def sort(self, label, hold=HOLD_S):
        key = str(label).strip().lower()
        if key == "ripe":
            f, s = self.f1, S1
        elif key == "unripe":
            f, s = self.f2, S2
        else:
            return            # Rotten: both flaps stay straight
        end = time.time() + hold
        while time.time() < end:
            f.goto(s["across"])   # keep holding the flap firm
        f.goto(s["straight"])

    def close(self):
        self.f1.close(); self.f2.close()
    def __enter__(self): return self
    def __exit__(self, *a): self.close()

if __name__ == "__main__":
    with TwoFlaps() as g:
        for label in ("Rotten", "Ripe", "Unripe", "Rotten"):
            print("sorting:", label); g.sort(label); time.sleep(0.5)