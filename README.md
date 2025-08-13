# RPI 5 Camera Server for ENES100
A camera server designed to be run on Raspberry Pi 5 and used with the RPI Camera Module 3. This server is also designed to be integrated within the vision system framework of the ENES100 class.

# Setup Instructions

## Step 0: RPI before boot

Please install the active cooler onto the RPI. There will be two plastic pins that lock in place and you must plug in the fan header. Please look this up if you do not know how.

Additionally you will need a >=27W power supply, a micro hdmi cable, a mouse, a keyboard, and a valid ethernet connection.

## Step 1: First time boot RPI 5

Follow the majority of the setup instructions that make intuitive sense (i.e. date, time, language, etc.)

The important things to ensure that you setup properly: 

Choose the recommended 64-bit version of Debian/PI OS.

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
$$\textcolor{red}{\textnormal{Please follow the next instructions carefully. Failure to do so could mean having to spend a lot of time fixing things.}}$$

Now we must build OpenCV-Python onto the RPI with gstreamer support. This will take some time.

First install system dependencies.
```console
sudo apt-get update
sudo apt-get install -y \
    build-essential cmake git pkg-config \
    libgtk-3-dev libavcodec-dev libavformat-dev libswscale-dev \
    libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    libjpeg-dev libpng-dev libtiff-dev \
    libxvidcore-dev libx264-dev \
    libatlas-base-dev gfortran
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
  -D CMAKE_INSTALL_PREFIX=$VIRTUAL_ENV \
  -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib/modules \
  -D WITH_GSTREAMER=ON \
  -D BUILD_opencv_python3=ON \
  -D PYTHON3_EXECUTABLE=$VIRTUAL_ENV/bin/python3 \
  -D PYTHON3_INCLUDE_DIR=$(python3 -c "from sysconfig import get_paths; print(get_paths()['include'])") \
  -D PYTHON3_PACKAGES_PATH=$VIRTUAL_ENV/lib/python3.10/site-packages \
  -D BUILD_EXAMPLES=OFF \
  ~/opencv
```

