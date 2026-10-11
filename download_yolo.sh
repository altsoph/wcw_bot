#!/usr/bin/env sh
set -eu

download_file() {
  python3 - "$1" "$2" <<'PY'
import os
import shutil
import sys
import urllib.request

url, destination = sys.argv[1:]
temporary = destination + '.part'
try:
    request = urllib.request.Request(url, headers={'User-Agent': 'wcw-bot-build/1.0'})
    with urllib.request.urlopen(request, timeout=90) as response, open(temporary, 'wb') as output:
        shutil.copyfileobj(response, output)
    os.replace(temporary, destination)
except Exception:
    if os.path.exists(temporary):
        os.remove(temporary)
    raise
PY
}

case "${1:-yolov3}" in
  none)
    # Browser-only probe images do not need detector assets.
    ;;
  yolov3)
    download_file https://pjreddie.com/media/files/yolov3.weights yolov3.weights
    download_file https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolov3.cfg yolov3.cfg
    download_file https://raw.githubusercontent.com/arunponnusamy/object-detection-opencv/master/yolov3.txt yolov3.txt
    ;;
  yolov4)
    download_file https://github.com/AlexeyAB/darknet/releases/download/yolov4/yolov4.weights yolov4.weights
    download_file https://raw.githubusercontent.com/AlexeyAB/darknet/master/cfg/yolov4.cfg yolov4.cfg
    download_file https://raw.githubusercontent.com/AlexeyAB/darknet/master/data/coco.names yolov4.txt
    ;;
  *)
    echo "Usage: sh download_yolo.sh [none|yolov3|yolov4]" >&2
    exit 2
    ;;
esac
