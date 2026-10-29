"""Tomato sorter: camera + Edge Impulse model + flap gate in one program.

The AI Camera watches the belt. When the model sees the same tomato class
twice in a row with at least 80% confidence, the program waits for the
tomato to travel from the camera to the flap, then moves the flap.
It then waits until the belt is empty before sorting the next tomato.

Run: python3 sorter.py   (Ctrl+C to stop)
"""
import time, cv2
from picamera2 import Picamera2
from edge_impulse_linux.image import ImageImpulseRunner
from flap_gate import Flap

MODEL = "/home/aarthi/tomato/model.eim"
CONF = 0.8       # how sure the model must be
TRAVEL_S = 1.5   # seconds from camera to flap (adjust later)

with ImageImpulseRunner(MODEL) as runner, Flap() as flap:
    runner.init()
    cam = Picamera2()
    cam.configure(cam.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"}))
    cam.start()
    time.sleep(2)
    print("Sorter ready. Press Ctrl+C to stop.")
    last = None
    try:
        while True:
            img = cv2.cvtColor(cam.capture_array(), cv2.COLOR_BGR2RGB)
            features, _ = runner.get_features_from_image_auto_studio_settings(img)
            s = runner.classify(features)["result"]["classification"]
            best = max(s, key=s.get)
            if best != "Empty" and s[best] >= CONF and best == last:
                print("Tomato:", best, round(s[best], 2), "-> moving flap")
                time.sleep(TRAVEL_S)
                flap.sort(best)
                print("Done. Waiting for next tomato...")
                while True:
                    img = cv2.cvtColor(cam.capture_array(), cv2.COLOR_BGR2RGB)
                    f2, _ = runner.get_features_from_image_auto_studio_settings(img)
                    s2 = runner.classify(f2)["result"]["classification"]
                    if max(s2, key=s2.get) == "Empty":
                        break
                    time.sleep(0.3)
                last = None
                continue
            last = best
            time.sleep(0.3)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        cam.stop()
