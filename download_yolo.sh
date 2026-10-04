#!/usr/bin/env sh
set -eu

case "${1:-yolov3}" in
  yolov3)
    wget -q https://pjreddie.com/media/files/yolov3.weights -O yolov3.weights
    wget -q https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg -O yolov3.cfg
    wget -q https://raw.githubusercontent.com/arunponnusamy/object-detection-opencv/master/yolov3.txt -O yolov3.txt
    ;;
  yolov4)
    wget -q https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4.weights -O yolov4.weights
    wget -q https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg -O yolov4.cfg
    wget -q https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names -O yolov4.txt
    ;;
  *)
    echo "Usage: sh download_yolo.sh [yolov3|yolov4]" >&2
    exit 2
    ;;
esac
