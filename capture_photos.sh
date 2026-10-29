#!/bin/bash
# Takes 20 training photos with the Raspberry Pi AI Camera.
# Usage: ./capture_photos.sh ripe_belt   (photos saved as ripe_belt1.jpg ... ripe_belt20.jpg)
NAME=${1:-photo}
for i in $(seq 1 20); do
  read -p "Hands away! Press Enter for $NAME photo $i"
  rpicam-still -n -o /home/aarthi/tomato/$NAME$i.jpg
done
