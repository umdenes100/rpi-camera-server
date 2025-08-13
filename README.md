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

Refresh the local cache of available packages and their versions from the configured software repositories.
```console
sudo apt update
```
<span style="color:red;">Please follow the next instructions carefully. Failure to do so could mean having to spend a lot of time fixing things.</span>

