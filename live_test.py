"""Live test: classifies what the AI Camera sees once per second and prints it.

Run: python3 live_test.py   (Ctrl+C to stop)
"""
import time
import cv2
from picamera2 import Picamera2
from edge_impulse_linux.image import ImageImpulseRunner

MODEL = "/home/aarthi/tomato/model.eim"

with ImageImpulseRunner(MODEL) as runner:
    runner.init()
    cam = Picamera2()
    cam.configure(cam.create_preview_configuration(main={"size": (640, 480), "format": "RGB888"}))
    cam.start()
    time.sleep(2)
    print("Camera ready. Press Ctrl+C to stop.")
    try:
        while True:
            frame = cam.capture_array()
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # same image resize/crop as Edge Impulse Studio used in training
            features, cropped = runner.get_features_from_image_auto_studio_settings(img)
            res = runner.classify(features)
            scores = res["result"]["classification"]
            best = max(scores, key=scores.get)
            print(best, {k: round(v, 2) for k, v in scores.items()})
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopped.")
    finally:
        cam.stop()
