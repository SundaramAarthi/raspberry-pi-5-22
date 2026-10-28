# Tomato Sorting Machine using Raspberry Pi

Final Year Project (Project 8) – BEng Robotics & Artificial Intelligence, University of Hertfordshire
Student: Aarthi | Supervisor: Wong Kim Siong

## About the project

This project is an AI tomato sorting machine. A Dobot Magician places tomatoes on a conveyor belt. A Raspberry Pi AI Camera above the belt takes a picture, and a machine learning model on the Raspberry Pi 5 classifies each tomato as **Ripe**, **Unripe** or **Rotten**. At the end of the belt, a servo-driven flap pushes the tomato into the correct bin.

## How it works

1. The Dobot Magician picks up a tomato and places it on the conveyor belt.
2. The conveyor carries the tomato under the AI Camera.
3. The Raspberry Pi 5 runs the trained model and decides the class.
4. The SG90 servo turns the flap to send the tomato to the right bin:

| Class  | Bin           | Servo angle |
|--------|---------------|-------------|
| Rotten | Straight on   | 110°        |
| Unripe | Left          | 140°        |
| Ripe   | Right         | 80°         |

## Hardware

- Raspberry Pi 5
- Raspberry Pi AI Camera (Sony IMX500)
- Dobot Magician with conveyor belt
- SG90 servo motor with a 3D-printed flap
- 3D-printed servo bracket and camera stand

## Wiring

| Component       | Connection on Raspberry Pi 5            |
|-----------------|-----------------------------------------|
| SG90 signal     | Pin 12 (GPIO 18)                         |
| SG90 power (5V) | Pin 2                                    |
| SG90 ground     | Pin 6                                    |
| AI Camera       | CSI camera port (ribbon cable)           |
| Dobot Magician  | USB                                      |
| Conveyor belt   | Dobot Stepper2 port (controlled via Dobot) |

The wiring diagram is in the `images/` folder.

## AI model

- Platform: Edge Impulse
- Model: Transfer learning with MobileNetV2 (96x96)
- Classes: Ripe, Unripe, Rotten
- Data: Public Kaggle "Tomatoes Dataset" (CC0) plus my own photos taken on the real conveyor belt

### Training progress

| Training run | Changes made                                   | Validation accuracy | Unripe correct |
|--------------|------------------------------------------------|---------------------|----------------|
| Run 1        | Kaggle dataset only                            | 70.4%               | 34.8%          |
| Run 2        | Added data augmentation and auto-weight classes | 69.8%               | 38.4%          |
| Run 3        | Added 13 of my own belt photos                 | 70.4%               | 32.8%          |
| Run 4        | Added 21 more Unripe belt photos               | 69.7%               | 39.8%          |

I found that some images in the public dataset have confusing labels (for example, orange tomatoes labelled as Ripe), which lowers accuracy. To fix this, I am adding more of my own photos taken on the actual conveyor belt with the same background and lighting.

## Folder structure

```
code/      Python scripts for the servo, flap gate and live classification
cad/       3D design files (flap, servo bracket, camera stand)
images/    Setup photos, wiring diagram and sample training photos
results/   Edge Impulse training results and confusion matrices
```

## Code files

- `servo_test.py` – first test of the servo on the Raspberry Pi 5
- `flap_gate.py` – moves the flap to the three bin positions
- `flap_angles.json` – saved servo angles for each bin
- `live_test.py` – runs the AI model with the AI Camera and prints the result

## Progress

**Done**
- Flap gate designed, 3D printed, and calibrated on the Raspberry Pi 5
- AI Camera connected and camera stand made
- Model trained in Edge Impulse and running on the Raspberry Pi 5
- Python script written for live classification

**In progress**
- Fixing camera detection after a system update
- Taking more belt photos of Ripe and Rotten tomatoes to retrain the model

**Next steps**
- Combine camera, model and flap gate into one program
- Test the Dobot gripper with tomatoes
- Make the three bins and test the full sorting system
