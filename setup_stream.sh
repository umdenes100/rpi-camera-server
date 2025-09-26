#!/usr/bin/env bash
# setup_stream.sh — one-time setup for Pi 5 + Cam Module 3 streaming
# Installs deps, writes send_stream.sh with YOUR exact pipeline, chmod +x, then self-deletes.

set -euo pipefail

echo "[*] Updating APT & upgrading..."
sudo apt update -y
sudo DEBIAN_FRONTEND=noninteractive apt full-upgrade -y

echo "[*] Installing required packages (rpicam-vid + GStreamer RTP stack)..."
sudo apt install -y \
  rpicam-apps \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-libav

echo "[*] Writing send_stream.sh with your preferred pipeline..."
cat > send_stream.sh <<'EOF'
#!/usr/bin/env bash
# send_stream.sh — stream Cam Module 3 via rpicam-vid → RTP(H.264) to HOST:PORT
# Uses the exact pipeline you provided and prefer.

# You can override HOST/PORT via args or env vars.
HOST="${1:-${HOST:-192.168.1.4}}"
PORT="${2:-${PORT:-5000}}"

# Tweakables (optional; match your defaults)
WIDTH="${WIDTH:-1920}"
HEIGHT="${HEIGHT:-1080}"
FRAMERATE="${FRAMERATE:-50}"
BITRATE="${BITRATE:-16000000}"   # bits per second
INTRA="${INTRA:-50}"             # keyframe interval = fps
MTU="${MTU:-1200}"               # RTP payload bytes (<= path MTU)

echo "[send_stream] → ${WIDTH}x${HEIGHT}@${FRAMERATE} ~$((${BITRATE}/1000000))Mbps → ${HOST}:${PORT}"

# EXACT pipeline you prefer:
# rpicam-vid → stdout → fdsrc (timestamps) → h264parse (normalized, SPS/PPS resend) → rtph264pay (RTP) → udpsink
/usr/bin/rpicam-vid -t 0 --width "${WIDTH}" --height "${HEIGHT}" --framerate "${FRAMERATE}" -n \
  --codec h264 --profile high --level 4.2 --inline --bitrate "${BITRATE}" --intra "${INTRA}" \
  --libav-format h264 -o - \
| gst-launch-1.0 -v \
    fdsrc fd=0 do-timestamp=true blocksize=65536 \
  ! h264parse config-interval=-1 disable-passthrough=true \
  ! rtph264pay pt=96 mtu="${MTU}" \
  ! udpsink host="${HOST}" port="${PORT}" sync=false async=false
EOF

chmod +x send_stream.sh
echo "[*] Created ./send_stream.sh (executable)."

# Self-delete this setup script
me="$(realpath "$0" 2>/dev/null || echo "$0")"
echo "[*] Deleting setup script: $me"
rm -f "$me"

echo "[✔] Setup complete."
echo "Run the stream with:  ./send_stream.sh 192.168.1.4 5000"
echo "Or override via env:  HOST=192.168.1.4 PORT=5000 ./send_stream.sh"
