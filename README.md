# Tomato Sorting Machine using Raspberry Pi

Final Year Project (Project 8) – BEng Robotics & Artificial Intelligence, University of Hertfordshire
Student: Sundaram Aarthi | Supervisor: Wong Kim Siong

## About the project

This project is an AI tomato sorting machine. Tomatoes travel along a conveyor belt under a Raspberry Pi AI Camera. A machine learning model running on the Raspberry Pi 5 classifies each tomato as **Ripe**, **Unripe** or **Rotten** (or **Empty** when there is no tomato). Two servo-driven flaps after the camera then guide each tomato off the belt into the correct bin.

▶️ Demo video: [`videos/ripe_sort_demo_two_flaps.mp4`](videos/ripe_sort_demo_two_flaps.mp4)

## How it works

**Dobot → camera → front flap → back flap → bins**

1. A tomato is placed on the conveyor belt (the Dobot Magician will do this step).
2. The belt carries the tomato under the AI Camera.
3. The Raspberry Pi 5 runs the model. When it sees the same class twice in a row with at least 80% confidence, it starts the sort.
4. After the tomato has travelled to the flaps (7.5 s), the correct flap swings across the belt and holds for 7 s, so the tomato slides along it and drops off the side.
5. The program waits until the belt is empty again, then sorts the next tomato.

| Class  | Flap that moves        | Where the tomato goes   |
|--------|------------------------|-------------------------|
| Ripe   | Back flap (servo 1)    | Off the front side      |
| Unripe | Front flap (servo 2)   | Off the back side       |
| Rotten | No flap moves          | Straight off the end    |

## Hardware

- Raspberry Pi 5
- Raspberry Pi AI Camera (Sony IMX500) on a 3D-printed stand
- Dobot Magician V2 with conveyor belt (belt motor on the Dobot's Stepper 2 port)
- 2 × SG90 servo motors with 3D-printed flaps (160 mm long, 4 mm thick) and rail brackets

## Wiring

| Wire            | Servo 1 – back flap (Ripe) | Servo 2 – front flap (Unripe) |
|-----------------|----------------------------|-------------------------------|
| Orange (signal) | Pin 12 (GPIO 18)           | Pin 33 (GPIO 13)              |
| Red (5 V)       | Pin 2                      | Pin 4                         |
| Brown (GND)     | Pin 6                      | Pin 9                         |

- AI Camera: CSI camera port (ribbon cable)
- Dobot Magician: USB to the Raspberry Pi (`/dev/ttyACM0`)

The full wiring diagram is in [`diagrams/`](diagrams).

## Settings

| Setting                     | Value                          |
|-----------------------------|--------------------------------|
| Servo 1 (back) angles       | edge 135°, across 100°         |
| Servo 2 (front) angles      | edge 75°, across 120°          |
| Belt speed and direction    | 0.5, direction −1              |
| Confidence needed           | 0.8                            |
| Camera-to-flap delay        | 7.5 s                          |
| Flap hold time              | 7 s                            |

## AI model

- Platform: Edge Impulse
- Model: Transfer learning with MobileNetV2 (96x96), float32, running on the Pi with the Edge Impulse Linux SDK
- Classes: Empty, Ripe, Rotten, Unripe
- Data: Public Kaggle "Tomatoes Dataset" (CC0) plus my own photos taken on the real conveyor belt with the AI Camera

### Training progress

| Run   | Changes made                                                | Validation accuracy |
|-------|-------------------------------------------------------------|---------------------|
| Run 1 | Kaggle dataset only                                         | 70.4%               |
| Run 2 | Added data augmentation and auto-weight classes             | 69.8%               |
| Run 3 | Added 13 of my own belt photos                              | 70.4%               |
| Run 4 | Added 21 Unripe belt photos                                 | 69.7%               |
| Run 5 | Added 20 Ripe belt photos and a new Empty class             | 59.4%               |
| Run 6 | Added 20 Empty + 20 Ripe photos from the final camera view  | 68.7%               |

The validation accuracy is measured mostly on the Kaggle images, which have some confusing labels. So I also test the model live on the real belt.

### Live test results

| On the belt  | Model result         |
|--------------|----------------------|
| Nothing      | Empty (0.93 – 1.00)  |
| Red tomato   | Ripe (0.80 – 0.99)   |
| Green tomato | Unripe (1.00)        |

## Folder structure

```
code/      Python scripts for the camera, model, flaps and belt
cad/       3D design files (flap, servo bracket)
images/    Tomato photos and wiring photos
diagrams/  System block and wiring diagram
results/   Edge Impulse confusion matrices and Gantt chart
videos/    Demo videos of the sorter
```

## Code files (`code/`)

| File               | What it does                                                  |
|--------------------|---------------------------------------------------------------|
| `sorter.py`        | Main program: camera + model + belt + two flaps              |
| `gate2.py`         | Controls both flaps (angles and hold time)                    |
| `flap_gate.py`     | Low-level servo control on the Pi 5 (GPIO pulses)             |
| `live_test.py`     | Shows what the model sees, once per second                    |
| `test_photo.py`    | Runs the model on saved photos                                |
| `move.py`          | Moves one servo by hand to find angles                        |
| `belt_test.py`     | Runs the conveyor belt for a few seconds                      |
| `stop_belt.py`     | Stops the conveyor belt                                       |
| `kick_test.py`     | Tests one flap with the belt running                          |
| `capture_photos.sh`| Takes 20 training photos with the AI Camera                   |

## Problems I solved

- **Camera not detected** after a system update → installed the IMX500 software (`imx500-all`).
- **Model said "Unripe" on an empty belt** → added an Empty class and took photos from the final camera position.
- **Background confused the model** (keyboard, cables) → fixed the camera so it mostly sees the belt.
- **Only two bins with one flap** → added a second servo and flap on the other side of the belt.
- **Big tomatoes pushed the flap aside** → printed longer, thicker flaps and made the code keep holding the flap.
- **Flap went back too early** → increased the hold time to 7 s.

## Progress

**Done**
- AI model running live on the Raspberry Pi 5
- Conveyor belt controlled from the Pi
- Two-flap sorting gate working; automatic Ripe sorting tested on the real belt

**Next steps**
- Test Unripe sorting with green tomatoes
- Take Rotten belt photos and retrain
- Add the Dobot pick-and-place step (suction cup or gripper)
- Run repeated tests and record the success rate
