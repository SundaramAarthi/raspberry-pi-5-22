import time, cv2
from picamera2 import Picamera2
from edge_impulse_linux.image import ImageImpulseRunner
from gate2 import TwoFlaps as Flap
from pydobotplus import Dobot

MODEL = "/home/aarthi/tomato/model.eim"
CONF = 0.8       # how sure the model must be
TRAVEL_S = 7.5   # seconds from camera to flap (adjust later)

with ImageImpulseRunner(MODEL) as runner, Flap() as flap:
    runner.init()
    cam = Picamera2()
    cam.configure(cam.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"}))
    cam.start()
    time.sleep(2)
    belt = Dobot(port="/dev/ttyACM0")
    belt.conveyor_belt(0.5, direction=-1, interface=1)
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
        belt.conveyor_belt(0, direction=-1, interface=1)
        belt.close()
