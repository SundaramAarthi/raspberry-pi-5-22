# Tomato Sorting Machine using Raspberry Pi

Final Year Project (Project 8) – BEng Robotics & Artificial Intelligence, University of Hertfordshire
Student: Aarthi | Supervisor: Wong Kim Siong

## About the project

This project is an AI tomato sorting machine. A Dobot Magician places tomatoes on a conveyor belt. A Raspberry Pi AI Camera above the belt takes a picture, and a machine learning model on the Raspberry Pi 5 classifies each tomato as **Ripe**, **Unripe** or **Rotten**. After the camera, a servo-driven flap guides the tomato into the correct bin.

## How it works

**Dobot → camera → flap → bins**

1. The Dobot Magician places a tomato on the conveyor belt.
2. The belt carries the tomato under the AI Camera.
3. The Raspberry Pi 5 runs the trained model and decides the class (or "Empty" when no tomato is there).
4. The tomato moves on to the flap, and the SG90 servo turns the flap to guide it into the right bin.

| Class  | Flap position              | Servo angle |
|--------|----------------------------|-------------|
| Rotten | Along the edge (straight)  | 110°        |
| Ripe   | Across the belt (far side) | 40°         |
| Unripe | Not final yet (see below)  | 80°         |

With the servo mounted on the side rail, the flap can reliably give two directions (straight and far side). A Y-chute after the belt end, with the flap in the middle, is planned for the third bin.

## Hardware

- Raspberry Pi 5
- Raspberry Pi AI Camera (Sony IMX500)
- Dobot Magician with conveyor belt
- SG90 servo motor with a 3D-printed flap
- 3D-printed servo bracket and camera stand

## Wiring

| Component       | Connection on Raspberry Pi 5               |
|-----------------|--------------------------------------------|
| SG90 signal     | Pin 12 (GPIO 18)                           |
| SG90 power (5V) | Pin 2                                      |
| SG90 ground     | Pin 6                                      |
| AI Camera       | CSI camera port (ribbon cable)             |
| Dobot Magician  | USB                                        |
| Conveyor belt   | Dobot Stepper2 port (controlled via Dobot) |

## Software setup on the Raspberry Pi 5

- AI Camera software: `sudo apt install imx500-all`
- Edge Impulse Linux runner and Python SDK (`edge_impulse_linux`)
- `picamera2` and OpenCV for camera capture

## AI model

- Platform: Edge Impulse
- Model: Transfer learning with MobileNetV2 (96x96), float32
- Classes: Ripe, Unripe, Rotten, Empty
- Data: Public Kaggle "Tomatoes Dataset" (CC0) plus my own photos taken on the real conveyor belt with the AI Camera

### Training progress

| Run   | Changes made                                    | Validation accuracy | Notes                     |
|-------|-------------------------------------------------|---------------------|---------------------------|
| Run 1 | Kaggle dataset only                             | 70.4%               | Unripe 34.8% correct      |
| Run 2 | Added data augmentation and auto-weight classes | 69.8%               | Unripe 38.4% correct      |
| Run 3 | Added 13 of my own belt photos                  | 70.4%               | Unripe 32.8% correct      |
| Run 4 | Added 21 Unripe belt photos                     | 69.7%               | Unripe 39.8% correct      |
| Run 5 | Added 20 Ripe belt photos and a new Empty class (20 photos) | 59.4% | Empty 100% correct |

The validation accuracy is measured mostly on the Kaggle images, and I found some of their labels are confusing (for example, orange tomatoes labelled as Ripe). So I also test the model live on the real belt.

### Live test on the belt (28 Oct 2026)

| On the belt  | Model result   |
|--------------|----------------|
| Nothing      | Empty (100%)   |
| Red tomato   | Ripe (100%)    |
| Green tomato | Unripe (100%)  |

Lessons learned:
- Before adding the Empty class, the model said "Unripe" even for an empty belt, because most of my belt photos were Unripe.
- The live script must resize the camera image the same way as Edge Impulse Studio, otherwise results are wrong.
- The background matters: when the camera saw a keyboard that was not in the training photos, the result was wrong.

## Code files (`code/` folder)

- `flap_gate.py` – controls the flap servo (calibrate and test modes)
- `flap_angles.json` – saved servo angles for each bin
- `capture_photos.sh` – takes 20 training photos with the AI Camera
- `live_test.py` – runs the AI model with the AI Camera and prints the result
- `test_photo.py` – runs the model on saved photos
- `sorter.py` – full sorting program: camera + model + flap together

## Progress

**Done**
- Flap gate designed, 3D printed and mounted after the camera
- AI Camera connected and camera stand made
- Model trained with my own belt photos, including an Empty class
- Model runs live on the Raspberry Pi 5 and classifies Empty, Ripe and Unripe correctly
- First full sorting program (`sorter.py`) detects the tomato and triggers the flap

**Next steps**
- Test the flap timing with `sorter.py` while the belt is moving
- Build a Y-chute for the third bin
- Take Rotten belt photos (dry damaged tomatoes, belt protected with cling film)
- Test with new tomatoes the model has not seen
- Add the Dobot pick-and-place step
