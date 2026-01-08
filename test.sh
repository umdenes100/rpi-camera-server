#!/bin/bash
set -euo pipefail
unset DISPLAY

OPTS=(
  --width 1920
  --height 1080
  --framerate 30
  --codec h264
  --libav-format h264
  --bitrate 16000000
  --profile high
  --intra 1
  --inline
  --saturation 1.2
  --denoise cdn_hq
  --awb auto
  --exposure normal
  --shutter 500
  --timeout 0
  -o -
)

rpicam-vid "${OPTS[@]}" | \
gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! \
  udpsink host=10.112.9.116 port=5000
