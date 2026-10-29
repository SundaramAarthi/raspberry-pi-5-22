"""Classify saved photos with the model (to check the model without the live camera).

Run: python3 test_photo.py photo1.jpg photo2.jpg ...
"""
import sys, cv2
from edge_impulse_linux.image import ImageImpulseRunner

with ImageImpulseRunner("/home/aarthi/tomato/model.eim") as runner:
    runner.init()
    for path in sys.argv[1:]:
        img = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB)
        try:
            features, _ = runner.get_features_from_image_auto_studio_settings(img)
            mode = "studio"
        except AttributeError:
            features, _ = runner.get_features_from_image(img)
            mode = "crop"
        s = runner.classify(features)["result"]["classification"]
        print(path.split("/")[-1], mode, max(s, key=s.get), {k: round(v, 2) for k, v in s.items()})
