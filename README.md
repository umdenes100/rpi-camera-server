# RPI 5 Camera Server for ENES100
A camera server designed to be run on Raspberry Pi 5 and used with the RPI Camera Module 3. This server is also designed to be integrated within the vision system framework of the ENES100 class.

# Setup Instructions

## Step 0: RPI before boot

Please install the active cooler onto the RPI. There will be two plastic pins that lock in place and you must plug in the fan header. Please look this up if you do not know how.

Additionally you will need a >=27W power supply, a micro hdmi cable, a mouse, a keyboard, the camera, and a valid ethernet connection.

If the camera is USB simply plug it in like you would any device. If it is a camera module, please make sure the RPI is unplugged and attach the camera module to CAM/DISP 0 appropriately. Use the orange cable instead of the white cable. The gold side of the connector should be facing up. Lift the brown covers on the camera and RPI port, insert the connector, and press the covers back down to snap the connectors into place. Please look this up if you do not know how.

Lastly, please ensure there is an SD card inserted onto the back of the RPI 5.

## Step 1: First time boot RPI 5

When plugging power into the RPI 5 for the first time, please press and hold the SHIFT key while it powers on to launch Network install.

Ethernet connection: Connect an Ethernet cable from the RPi to your laptop, using an adapter if necessary. Hit the Windows button + R to open your network connections. Eduroam may not be able to feed WiFi to the RPi, so use a phone hotspot if possible. Select your WiFi connection and your new Ethernet connection simultaneously (using CTRL) and request to Bridge the connection. Once the connection is bridged, the RPi should be receiving WiFi from your laptop. If there is an error, you may need to unplug and replug the power cord for the RPi to reset the boot. Then press shift to rerun the boot. Disconnect and reconnect Ethernet to retry the network connection process.

Follow the majority of the setup instructions that make intuitive sense (i.e. date, time, language, etc.)

The important things to ensure that you setup properly: 

Choose the recommended 64-bit version of Debian/PI OS.
The RPi we are using for 2025 is the Raspberry Pi 5.
Storage: whichever SD card is being used in the RPi.

When prompted to either further config or add extra setup options to the RPI, select edit options or whatever button there is to make these adjustments.
In this menu set the hostname to the format of KS-RPI-X. Please see the WiFi module Registration tracker sheet to see which hostname you should be setting your device to.

Also set the username and password to the device. The username for all of these devices should be keystoneltf. Then password may be unique but make sure to either indicate it in the tracker sheet or ask your boss to edit the sheet for you.

If prompted, enable SSH (otherwise we will do this later.

## Step 2: Updates and Preparation

Open a terminal (ctrl+alt+t)

Refresh the local cache of available packages and their versions from the configured software repositories. Will upgrade packages on the RPI as well.
```console
sudo apt update && sudo apt upgrade
```
We will also at this point install the firewall and allow the port 554 through (this is for the image server to communicate to the VM)
```console
sudo apt install ufw
sudo ufw allow 554/tcp
sudo ufw allow 554/udp
sudo ufw allow 5000/tcp
sudo ufw allow 5000/udp
sudo ufw allow 5001/tcp
sudo ufw allow 5001/udp
```

$$\textcolor{red}{\textnormal{Please follow the next instructions carefully. Failure to do so could mean having to spend a lot of time fixing things.}}$$

Now we must build OpenCV-Python onto the RPI with gstreamer support. This will take some time.

First install system dependencies.
```console
sudo apt update
sudo apt install -y \
    build-essential cmake git pkg-config \
    libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev \
    libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    libjpeg-dev libpng-dev libtiff-dev \
    libxvidcore-dev libx264-dev \
    libatlas-base-dev gfortran
```
These are some things we can use for command line tools and developer reasons.
```console
sudo apt update
sudo apt install \
  gstreamer1.0-tools \
  gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad \
  gstreamer1.0-plugins-ugly \
  gstreamer1.0-libav \
  gstreamer1.0-x \
  gstreamer1.0-gl \
  gstreamer1.0-gtk3 \
  gstreamer1.0-qt5 \
  gstreamer1.0-pulseaudio \
  v4l-utils \
  libv4l-dev \
  libcamera-dev libcamera-apps
```
Clone the OpenCV repos.
```console
cd ~
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
```
Create the build directory and configure CMake to enable Gstreamer support
```console
mkdir -p ~/build/opencv && cd ~/build/opencv

cmake \
  -D CMAKE_BUILD_TYPE=RELEASE \
  -D CMAKE_INSTALL_PREFIX=/usr/local \
  -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
  -D WITH_GSTREAMER=ON \
  -D BUILD_opencv_python3=ON \
  -D PYTHON3_EXECUTABLE=$(which python3) \
  -D PYTHON3_INCLUDE_DIR=$(python3 -c "from sysconfig import get_paths; print(get_paths()['include'])") \
  -D PYTHON3_PACKAGES_PATH=$(python3 -c "from sysconfig import get_paths; print(get_paths()['purelib'])") \
  -D BUILD_EXAMPLES=OFF \
  ~/opencv
```
Now we will Compile and install (This step sometimes can take some time to run ~30min, do not disconnect power while this is running)
```console
make -j$(nproc)
sudo make install
```
Lets confirm to see if all of the above went as planned.
```console
cd ~
mkdir dev
cd dev
python3
```
```python
>>> import cv2
>>> print('GStreamer:', 'YES' if cv2.getBuildInformation().count('GStreamer')>0 else 'NO')
```
You should see YES and in the build information you should see Gstreamer: YES. THat means that everything worked and we are ready to upload the program and run it!

## Step 3: Clone, configure, and run it!

If not already navigate to the dev folder we create in the last step.
```console
cd ~/dev
```
Now we will clone the repo
```console
git clone https://github.com/umdenes100/rpi-camera-server.git
cd rpi-camera-server
```
Lets make double check the config to make sure our server is pointing to the right Virtual Machine Server.
```console
nano send_stream.py
```
Look at the top for GST_HOST = "10.112.9.33"
Please set X.X.X.X to the Internal IP of the VM that you want to send the stream to. Check the WiFi Registration Tracker for this number.

Press ctrl+x then y, then ENTER to save your changes.

Last thing before we run the stream is we are going to setup a tmux session so that the stream can be checked on via an SSH connection.
```console
sudo apt install tmux
tmux
```
I encourage you to look up a little bit about what tmux is, its a very useful tool to know.

Now run the stream!
```console
python3 send_stream.py
```

## Step 4: Extras (WiFi, SSH, etc.)

Enable WiFi (log in if you need/want this, you may need to use a hotspot on your phone for temp WiFi connection, this should generally not be permanent as ethernet is much better)
```console
sudo rfkill unblock all
```


