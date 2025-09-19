#!/bin/bash
# send_cam_stream.sh
# Stream Raspberry Pi Camera Module 3 (Pi 5) over UDP/RTP (H.264) to 192.168.1.4:5000

HOST="192.168.1.4"
PORT="5000"
WIDTH=1920
HEIGHT=1080
FRAMERATE=50
BITRATE=16000000  # 16 Mbps

/usr/bin/rpicam-vid -t 0 \
  --width $WIDTH --height $HEIGHT --framerate $FRAMERATE -n \
  --codec h264 --profile high --level 4.2 --inline \
  --bitrate $BITRATE --intra $FRAMERATE \
  --libav-format h264 -o - \
| gst-launch-1.0 -v \
    fdsrc fd=0 do-timestamp=true blocksize=65536 \
  ! h264parse config-interval=-1 disable-passthrough=true \
  ! rtph264pay pt=96 mtu=1200 \
  ! udpsink host=$HOST port=$PORT sync=false async=false
