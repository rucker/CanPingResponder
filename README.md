# CanPingResponder

This kata evaluates your ability to stand up a BeagleBone Black computer board so that it can be used in a product development effort that uses CAN bus as the device communication environment.

As a member of an embedded product team, you need to set up a very simple "ping" responder on a CAN bus so that you can assess simple CAN bus connectivity. The ping responder accepts a CAN message with ID = 100 (decimal) and an 8-byte data payload whose last byte is an integer value, and responds with a reply message with ID = 101 (decimal) and an 8-byte data field whose last byte is the received message integer value plus 1. Because it is a byte value, if the received value is 0xFF, the response value should be 0x00. The response must also preserve any other existing data that was received. The CAN bus will nominally be configured to operate at 500 kHz.

Your solution will need to use a BeagleBone Black (BBB) microcontroller/computer board, running Debian Linux 9 ("Stretch"), using the SocketCAN library. The language must be Python3. Your test framework will be Py-Test. Because a stock BeagleBone Black will not be readily configured to your needs, you will need to configure it according to the instructions that follow.

## Items Needed

1. **BeagleBone Black board**
1. **microSD Card**, at least 4GB
   - You will also need a way to write to the microSD card; a full-size SD card adapter is often used for this
1. **_USB Type A_-to-_Mini USB_ cable**
   - This will both power the BeagleBone board and provide a data connection with your computer

For more information, see the BeagleBoard main site (http://beagleboard.org/) and the dedicated BeagleBone Black page (http://beagleboard.org/black).

## Procedures

### Preliminary Board Setup

The BeagleBone Black ships with a full version of Debian which occupies most of the 4GB of onboard flash. In our development group, we re-flash our boards with the IoT version of Debian which does not contain the GUI and associated apps. Doing this frees up nearly half of the onboard flash. The direct link to the Debian image used for this kata is:

https://debian.beagleboard.org/images/bone-debian-9.5-iot-armhf-2018-10-07-4gb.img.xz

The SHA256 digest of the image is `52363c654b7a1187656b08c5686af7564c956d6c60c7df5bf4af098f7df395e0` and you can verify this locally by running `openssl sha -sha256 <file>`.

(You may view available images at http://beagleboard.org/latest-images, however for the sake of consistency and avoiding unforseen compatability issues, we recommended you simply download from the link given above.)

To create the flash image on the microSD card, we recommend using Etcher (https://etcher.io/).

Once you've generated the flashable microSD card -- WITH THE BEAGLEBONE BLACK POWERED OFF -- insert the microSD card and then plug in the BeagleBone Black to your computer which will power it up. The BBB will power up and run from the microSD image. You will need to enable it to autoflash your BBB (described in the following steps):

1. Open a Terminal on Macintosh and connect to the BBB:  
   `ssh debian@192.168.6.2`  
using `temppwd` as the default password. (You may find that your BBB obtained an IP address of `192.168.7.2`. This is fine; simply connect via whichever address it was assigned.)
1. Edit the /boot/uEnv.txt, and uncomment the line:  
   `cmdline=init=/opt/scripts/tools/eMMC/init-eMMC-flasher-v3.sh`
1. Reboot the BBB and let it flash the eMMC:  
   `sudo shutdown -r now` or `sudo reboot`  
   The BBB will recognize the flash card and begin flashing its eMMC, and the status LEDs will begin flashing in a ping-pong pattern.  
   **_NOTE:_** You'll need to wait 45-60 seconds before seeing the "ping pong" pattern. Once that pattern appears, you'll need to wait another 5-6 minutes for the flashing process to finish.
1. When the board finishes flashing, it will power down, and its LEDs will all be off. Disconnect the BBB from power/USB and **eject the microSD card**.  
   **_NOTE:_** If you do not eject the microSD card then the BBB will re-flash its firmware the next time it boots.
1. **After removing the microSD card**, power up the BBB again, connect via SSH, and then verify that the board firmware is correct by typing  
   `cat /etc/os-release`  
   You should get the following output:  
   ```
   PRETTY_NAME="Debian GNU/Linux 9 (stretch)"
   NAME="Debian GNU/Linux"
   VERSION_ID="9"
   VERSION="9 (stretch)"
   ID=debian
   HOME_URL="https://www.debian.org/"
   SUPPORT_URL="https://www.debian.org/support"
   BUG_REPORT_URL="https://bugs.debian.org/"
   ```

### Install general updates

1. Ensure your BBB has network connectivity and then update the software base:  
   `sudo apt-get update`  
   `sudo apt-get upgrade`  
   **_NOTE:_** During the `upgrade` process you will be prompted twice about the Robotics Cape:
   1. When asked to "Enable the Robotics Cape device tree?", select `<No>`
   1. When asked "Which [librobotcontrol] program to run on boot?", select `none`
1. As a sanity point, verify that you have nearly 40% of the eMMC still available for use:  
   `df -h`  
   You should get something similar to the following:  
   ```
   Filesystem      Size  Used Avail Use% Mounted on
   udev            215M     0  215M   0% /dev
   tmpfs            49M  5.3M   44M  11% /run
   /dev/mmcblk1p1  3.5G  2.0G  1.4G  60% /
   tmpfs           242M     0  242M   0% /dev/shm
   tmpfs           5.0M  4.0K  5.0M   1% /run/lock
   tmpfs           242M     0  242M   0% /sys/fs/cgroup
   tmpfs            49M     0   49M   0% /run/user/1000
   ```
1. Save a copy of the current U-Boot environment configuration - _uEnv.txt_- in case it needs to be restored:  
   `sudo cp /boot/uEnv.txt /boot/uEnv.txt.beaglebone`

### Set Up and Activate CAN Capability

1. Verify that `/lib/firmware` directory contains `BB-CAN1-00A0.dtbo`:  
   `ls /lib/firmware | grep BB-CAN`
1. If you have not already done so, save the current U-Boot environment, uEnv.txt, configuration in case it needs to be restored (if you are prompted to overwrite _uEnv.txt.beaglebone_ then you should decline):  
   `sudo cp -i /boot/uEnv.txt /boot/uEnv.txt.beaglebone`
1. Create a new uEnv.txt file specific to the CAN cape DTBO:  
   ```
   cat << EOF | sudo tee /boot/uEnv.txt
   # uEnv.txt for WaveShare RS485 CAN Cape

   uname_r=4.14.71-ti-r80
   enable_uboot_overlays=1
   dtb_overlay=/lib/firmware/BB-CAN1-00A0.dtbo
   cmdline=coherent_pool=1M net.ifnames=0 quiet
   EOF
   ```
   **Note: You will need to replace the Linux kernel version in the `uname_r=4.14.71-ti-r80` line with your specific Linux version if it is different than what has been written here.**
1. Add the `start-can` and `stop-can` scripts:  
   ```
   cat << EOF | sudo tee /usr/local/bin/start-can
   #!/bin/sh
   sudo ip link set can0 up type can bitrate 500000
   EOF
   sudo chmod +x /usr/local/bin/start-can
   cat << EOF | sudo tee /usr/local/bin/stop-can
   #!/bin/sh
   sudo ip link set can0 down
   EOF
   sudo chmod +x /usr/local/bin/stop-can
   ```
1. In `/etc/network/interfaces`, configure `can0` to start up at boot:  
   ```
   cat << EOF | sudo tee -a /etc/network/interfaces
   
   # CAN Bus
   auto can0
   iface can0 can static
       bitrate 500000
   EOF
   ```
1. Reboot  
   ```
   sudo reboot
   ```
1. Verify that only `can0` is listed as the available CAN device:  
   ```
   ip link
   ```  
   and it is designated as UP.
   
### Set Up and Activate VCAN Capability

Create a `setup-and-start-vcan` bash script to create the virtual CAN link, `vcan0`:  
```
cat << EOF | sudo tee /usr/local/bin/setup-and-start-vcan
#!/bin/sh
sudo modprobe vcan
sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0
EOF
sudo chmod +x /usr/local/bin/setup-and-start-vcan
```

**Note: You will need to use the `setup-and-start-vcan` script to enable the `vcan0` link every time you power up your BBB.**

### Python 3 Development Setup

The BBB Debian 9 installation comes with Python 3 and PIP3. Use PIP3 to install Py-Test and the Python CAN library:  
`sudo pip3 install pytest`  
`sudo pip3 install python-can==1.5.2` (**You must install version 1.5.2!**)

### File Sharing setup

The "File Sharing setup" section is technically not needed to complete the kata. However, your life will be much easier if you enable file sharing on your BeagleBone Black so that you can have the flexibility to develop on your own machine while executing directly from the BBB. Below are instructions for two file sharing methods: NFS and SMB.

#### NFS

**On the BeagleBone Black running Debian:**
1. Make sure you have an up-to-date package index:  
   `sudo apt-get update`
1. Install the kernel version of the NFS server:  
   `sudo apt-get install nfs-kernel-server`
1. Add a `debian` share entry to `/etc/exports` as shown below (note the “insecure” for OSX):  
   ```
   cat << EOF | sudo tee -a /etc/exports
   
   /home/debian *(rw,no_subtree_check,insecure,all_squash,anonuid=1000,anongid=1000)
   EOF
   ```  
   Note: The default `debian` account has uid=1000 and gid=1000.
1. Update the NFS export table:  
   `sudo exportfs -ra`
1. Restart `nfs-kernel-server`:  
   `sudo service nfs-kernel-server restart`
1. Enable NFS server to start at boot:  
   `sudo systemctl enable nfs-kernel-server`

**On macOS machine:**  
This example mounts the `debian` home folder from the `beaglebone` device (unless you've changed it, your BBB will have an mDNS name of `beaglebone.local`).
1. Create a mount point:  
   `mkdir -p ~/Shares/beaglebone/debian`
1. To mount your BeagleBone Black exported share point, use  
   `sudo mount -o resvport -t nfs beaglebone.local:/home/debian ~/Shares/beaglebone/debian`
1. To unmount, use  
   `sudo umount ~/Shares/beaglebone/debian`

**On Debian machine:**  
This example mounts the `debian` home folder from the `beaglebone` device (unless you've changed it, your BBB will have an mDNS name of `beaglebone.local`).
1. Make sure you have an up-to-date package index:  
   `sudo apt-get update`
1. Install `nfs-common` if you have not already installed `nfs-kernel-server`:  
   `sudo apt-get install nfs-common`
1. Create a mount point:  
   `mkdir -p ~/Shares/beaglebone/debian`
1. To mount your BeagleBone Black exported share point, use  
   `sudo mount -t nfs beaglebone.local:/home/debian ~/Shares/beaglebone/debian`
1. To unmount, use  
   `sudo umount ~/Shares/beaglebone/debian`

#### SMB

1. Make sure you have an up-to-date package index:  
   `sudo apt-get update`
1. Install Samba:  
   `sudo apt-get install samba`
1. In `/etc/samba/smb.conf`, change the following lines in the `[home` section:
   ```
   ...
   [homes]
     ...
     read only = no
     ...
     create mask = 0775
     ...
     directory mask = 0775
     ...
   ```
1. Add the `debian` user to the SMB user list:  
   `sudo smbpasswd -a debian`  
   It is suggested that you use the corresponding Linux account password.
1. Restart the samba service  
   `sudo service smbd restart`

### Set up the Project

The Loop team will provide you with a zipped file containing the required files for the kata.

The structure of the project is as follows:

`ping_responder_controller.py` (in the Controllers directory) - This is the ping responder controller library for you to test drive. A template version has been created for you.

`ping_responder_controller_tests.py` (in the Tests directory) - This is the test runner for test driving the controller. A template version has been created for you.

`can_adapter.py` (in the Tools directory) - This is a CAN adapter library that simplifies the use of the SocketCAN library in Python. **_You should be able to use this file as is and not need to modify it._**

`can_ping_responder.py` is the program that will run the `ping_responder_controller.py` as a stand-alone app. You should not need to modify it. It will be used when integration testing your solution with an existing system.

From the working directory, run `python3 -m Tests.ping_responder_controller_tests` to run the tests. By default, the tests use the `vcan0` link.

**Note: For your development activities, you will be using the virtual CAN link, `vcan0`. You will need to run the `setup-and-start-vcan` script to enable the `vcan0` link every time you power up your BBB.**
