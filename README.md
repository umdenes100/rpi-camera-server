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

Ethernet connection: Connect an Ethernet cable from the RPI to your laptop, using an adapter if necessary. Hit the Windows button + R to open your network connections. Eduroam may not be able to feed WiFi to the RPi, so use a phone hotspot if possible. Select your WiFi connection and your new Ethernet connection simultaneously (using CTRL) and request to Bridge the connection. Once the connection is bridged, the RPi should be receiving WiFi from your laptop. If there is an error, you may need to unplug and replug the power cord for the RPi to reset the boot. Then press shift to rerun the boot. Disconnect and reconnect Ethernet to retry the network connection process.

Follow the majority of the setup instructions that make intuitive sense (i.e. date, time, language, etc.)

The important things to ensure that you setup properly: 

Choose the recommended 64-bit version of Debian/PI OS.
The RPi we are using for 2025 is the Raspberry Pi 5.
Storage: whichever SD card is being used in the RPi.

When prompted to either further config or add extra setup options to the RPI, select edit options or whatever button there is to make these adjustments.
In this menu set the hostname to the format of KS-RPI-X. Please see the WiFi module Registration tracker sheet to see which hostname you should be setting your device to.

Also set the username and password to the device. The username for all of these devices should be keystoneltf. Then password may be unique but make sure to either indicate it in the tracker sheet or ask your boss to edit the sheet for you.

If prompted, enable SSH.

## Step 2: Updates and Preparation

Open a terminal (ctrl+alt+t)

Refresh the local cache of available packages and their versions from the configured software repositories. Will upgrade packages on the RPI as well.
```console
sudo apt update && sudo apt upgrade
```

# NEEDS UPDATING FOR THE NEW SYSTEM
## Step 3: Clone, configure, and run it!

```console
mkdir dev
cd ~/dev
```
Now we will clone the repo
```console
git clone https://github.com/umdenes100/rpi-camera-server.git
cd rpi-camera-server
```


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

Enable SSH
```console
sudo raspi-config
```
Navigate to interfaces and enable SSH

Set the Hostname
```console
sudo raspi-config
```
Navigate to system options -> hostname and set it to the hostname indicated in the WiFi registration sheet
