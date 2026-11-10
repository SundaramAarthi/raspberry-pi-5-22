#!/usr/bin/env python3
"""Sorting flap for the tomato sorter: one SG90 on a Raspberry Pi 5.

Bins: Rotten = straight on (rest position), Ripe = right, Unripe = left.
Wiring: servo signal (orange) -> GPIO 18 (physical pin 12), red -> 5 V, brown -> GND.
If the Pi resets or the servo twitches, power the servo from a separate 5 V supply
and join its GND to a Pi GND pin.

Run:   python3 flap_gate.py calibrate    (set the three angles, saved to flap_angles.json: do Rotten first)
       python3 flap_gate.py test         (Rotten straight, then Ripe right, Unripe left, and back)
Use:   from flap_gate import Flap
       with Flap() as flap:
           flap.sort("Ripe")             # moves the flap to the right bin, waits, returns to straight
"""
import json, os, sys, threading, time
import gpiod

PIN = 18                      # GPIO 18, same pin as my earlier servo test
MIN_US, MAX_US = 500, 2400    # pulse width for 0 and 180 degrees (SG90 range, trim if it hits the end stops)
HERE = os.path.dirname(os.path.abspath(__file__))
ANGLE_FILE = os.path.join(HERE, "flap_angles.json")
DEFAULT_ANGLES = {"rotten": 90, "unripe": 60, "ripe": 120}   # starting guesses only: calibrate first
HOLD_S = 1.0                  # time the flap stays over the bin while the tomato slides past
SETTLE_S = 0.4                # time to let the servo reach its angle


# ---------------------------------------------------------------- GPIO (works with libgpiod v1 and v2)
class _Pin:
    def __init__(self, pin):
        self.pin = pin
        self.v2 = hasattr(gpiod, "request_lines")
        path = self._find_chip()
        if self.v2:
            from gpiod.line import Direction, Value
            self.Value = Value
            self.req = gpiod.request_lines(path, consumer="flap", config={
                pin: gpiod.LineSettings(direction=Direction.OUTPUT, output_value=Value.INACTIVE)})
        else:
            self.chip = gpiod.Chip(path)
            self.line = self.chip.get_line(pin)
            self.line.request(consumer="flap", type=gpiod.LINE_REQ_DIR_OUT, default_vals=[0])

    def _find_chip(self):
        # On the Pi 5 the header pins are on the RP1 chip; its gpiochip number changes between OS versions.
        for i in range(32):
            path = f"/dev/gpiochip{i}"
            try:
                if self.v2:
                    label = gpiod.Chip(path).get_info().label
                else:
                    label = gpiod.Chip(path).label()
            except Exception:
                continue
            if "rp1" in label.lower():
                return path
        return "/dev/gpiochip4"

    def write(self, value):
        if self.v2:
            self.req.set_value(self.pin, self.Value.ACTIVE if value else self.Value.INACTIVE)
        else:
            self.line.set_value(1 if value else 0)

    def close(self):
        try:
            (self.req if self.v2 else self.line).release()
        except Exception:
            pass


# ---------------------------------------------------------------- flap
def load_angles():
    if os.path.exists(ANGLE_FILE):
        with open(ANGLE_FILE) as f:
            return {**DEFAULT_ANGLES, **json.load(f)}
    return dict(DEFAULT_ANGLES)

def save_angles(angles):
    with open(ANGLE_FILE, "w") as f:
        json.dump(angles, f, indent=2)


class Flap:
    def __init__(self, pin=PIN):
        self.pin = _Pin(pin)
        self.angles = load_angles()
        self.angle = self.angles["rotten"]          # rest position: straight on, Rotten bin
        self._run = True
        self._lock = threading.Lock()
        self._thread = threading.Thread(target=self._pulse_loop, daemon=True)
        self._thread.start()
        time.sleep(SETTLE_S)

    # 50 Hz pulses made by hand: 20 ms period, 0.5 to 2.4 ms high. Runs in its own thread so the
    # servo keeps holding its position while the rest of the program does other things.
    def _pulse_loop(self):
        while self._run:
            t0 = time.perf_counter()
            with self._lock:
                width = (MIN_US + (MAX_US - MIN_US) * self.angle / 180.0) / 1e6
            self.pin.write(1)
            end = t0 + width
            while time.perf_counter() < end:
                pass
            self.pin.write(0)
            rest = 0.020 - (time.perf_counter() - t0)
            if rest > 0:
                time.sleep(rest)

    def goto(self, angle, wait=SETTLE_S):
        angle = max(0.0, min(180.0, float(angle)))
        with self._lock:
            self.angle = angle
        time.sleep(wait)

    def sort(self, label, hold=HOLD_S):
        """label: 'Ripe' (right bin), 'Unripe' (left bin) or 'Rotten' (straight on, flap stays at rest).
        Any other label (for example an uncertain result) is treated like Rotten and goes straight on."""
        key = str(label).strip().lower()
        if key in ("ripe", "unripe"):
            self.goto(self.angles[key])
            time.sleep(hold)
        self.goto(self.angles["rotten"])       # rest position, straight on

    def close(self):
        self._run = False
        self._thread.join(timeout=1)
        self.pin.write(0)
        self.pin.close()

    def __enter__(self): return self
    def __exit__(self, *a): self.close()


# ---------------------------------------------------------------- command line tools
def calibrate():
    with Flap() as flap:
        print("Calibration. Type a number (0 to 180) to move, +5 or -5 to nudge,")
        print("then 'save rotten' (straight on), 'save ripe' (right) or 'save unripe' (left). 'quit' to finish.")
        print(f"Saved angles now: {flap.angles}")
        while True:
            cmd = input(f"[{flap.angle:.0f} deg] > ").strip().lower()
            if cmd in ("q", "quit", "exit"):
                break
            if cmd.startswith("save "):
                name = cmd.split()[1]
                if name in ("ripe", "rotten", "unripe"):
                    flap.angles[name] = round(flap.angle)
                    save_angles(flap.angles)
                    print(f"saved {name} = {flap.angles[name]}")
                else:
                    print("use: save ripe / save rotten / save unripe")
                continue
            try:
                value = float(cmd)
            except ValueError:
                print("type a number, +5, -5, save ..., or quit")
                continue
            flap.goto(flap.angle + value if cmd[0] in "+-" else value, wait=0.3)
        print("final angles:", flap.angles)

def test():
    with Flap() as flap:
        for label in ("Rotten", "Ripe", "Unripe", "Rotten"):
            print("sorting:", label)
            flap.sort(label)
            time.sleep(0.5)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "test"
    {"calibrate": calibrate, "test": test}.get(mode, test)()
