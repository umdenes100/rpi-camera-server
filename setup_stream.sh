#!/bin/bash                                                                                                                                                                                                                                     set -e                                                                                                                                                                                                                                          echo "Updating system and installing required packages..."                                                              sudo apt update                                                                                                         sudo apt full-upgrade -y                                                                                                                                                                                                                        # Install libcamera apps and dependencies                                                                               sudo apt install -y libcamera-apps gstreamer1.0-tools gstreamer1.0-plugins-base \                                           gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \                                          gstreamer1.0-libav ffmpeg ufw                                                                                                                                                                                                               # Enable camera interface if not already enabled
if ! grep -q "^camera_auto_detect=1" /boot/config.txt 2>/dev/null; then
    echo "Enabling camera interfaces..."
    sudo raspi-config nonint do_camera 0
fi

# Ask user for receiver IP and port
read -rp "Enter the receiver IP address: " RECEIVER_IP
read -rp "Enter the UDP port number to send the stream to: " RECEIVER_PORT

# Validate IP and port (basic)
if ! [[ "$RECEIVER_IP" =~ ^([0-9]{1,3}\.){3}[0-9]{1,3}$ ]]; then
    echo "Invalid IP address format. Exiting."
    exit 1
fi
if ! [[ "$RECEIVER_PORT" =~ ^[0-9]+$ ]] || [ "$RECEIVER_PORT" -lt 1 ] || [ "$RECEIVER_PORT" -gt 65535 ]; then
    echo "Invalid port number. Exiting."
    exit 1
fi

# Create send_stream.sh script
cat << EOF > send_stream.sh
#!/bin/bash
# Script to send 1080p@50fps H264 stream to $RECEIVER_IP:$RECEIVER_PORT

# Disable preview by clearing DISPLAY variable
DISPLAY=

rpicam-vid --width 1920 --height 1080 --framerate 50 --codec h264 --libav-format=h264 --timeout 0 -o - | \\                                                                   gst-launch-1.0 fdsrc ! h264parse ! rtph264pay config-interval=1 pt=96 ! udpsink host=$RECEIVER_IP port=$RECEIVER_PORT
EOF

chmod +x send_stream.sh

echo "Configuring UFW firewall to allow UDP traffic to $RECEIVER_IP:$RECEIVER_PORT..."

# Enable UFW if disabled
sudo ufw status | grep -q inactive && sudo ufw --force enable

# Allow outgoing UDP packets to specified IP/port                                      sudo ufw allow out to $RECEIVER_IP port $RECEIVER_PORT proto udp

echo "Setup complete. You can start streaming by running ./send_stream.sh"

echo "Deleting setup script to keep only send_stream.sh"                               rm -- "\$0"
