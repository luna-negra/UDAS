### Translation [English](README.md) | [Japanese](README.ja.md) | [Korean](README.ko.md)
<hr>

# USB Docking Authentication System (UDAS)

## 1. Introduction
<div>
UDAS - USB Docking Authentication System is a program developed to prevent data leakage or alteration caused by 
automatic connection of suspicious USB storage devices on personal computers such as laptops and desktops that 
do not use USB port blockers. 
</div><br>

<div>
[ Provided Features ]<br>
* USB storage device connection detection<br>
* User confirmation for connected devices<br>
* Blacklist & Whitelist registration for devices<br>
</div>

## 2. Supported OS and Environment
<table>
    <th>
        <td>Version</td>
        <td>Operating System</td>
        <td>Distribution</td>
    </th>
    <tr>
        <td>1</td>
        <td>0.0.0 (Beta)</td>
        <td>Ubuntu 24.04</td>
        <td>Debian Package</td>
    </tr>
</table>

## 3. Installation
### (1) Manual Install
① Downloading Git Reponsitory

```commandline
git clone --branch main https://github.com/luna-negra/UDAS/
```
<br>
② Creating Python Virtual Environment and Debian Package File System

```commandline
cd UDAS;
python -m venv .venv
bash ./create_pkg.sh
```
![img.png](img.png)

* If an error occurs during Debian package creation, please follow the on-screen guide.
<br>

③ Creating Debian Package

```commandline
dpkg-deb --build udas-0.0-0-amd64/
```
<br>
④ Installing UDAS Debian Package

```commandline
sudo dpkg -i udas-0.0.0-amd64.deb
```
* It is recommended to install this package file using sudo with a regular user account.<br>
* During installation, please follow the on-screen guide to perform password change operations and command input operations after installation.<br>

⑤ Verifying Installation
* Run UDAS/udas_gui from the home folder of the account used for installation.

```commandline
~/udas/udas_gui
```

![img_1.png](img_1.png)

* On the GUI screen, navigate to Main > Service and check the Status of Daemons.
![img_2.png](img_2.png)

* If UDAS Detector and UDAS Listener services are running, a message window will appear asking to confirm whitelist registration when a USB storage device is connected to the PC.
![img_3.png](img_3.png)

### 4. Usage
<div>
UDAS settings, USB device management, service activation, log viewing, etc., can be performed through the GUI program. 
The GUI program is divided into the following four sections.<br>

- Main
- Management
- Settings
- Logging<br>

</div>

#### (1) Main
The Main section displays the number of USB storage devices currently registered in Blacklist or Whitelist, 
and the status of UDAS-related service daemons.
![img_4.png](img_4.png)

* UDAS-related service daemons include Detector and Listener. 
  If either of these services is not running, real-time detection of USB storage devices is not possible.
![img_5.png](img_5.png)

#### (2) Management
The Management section provides a list of USB storage devices registered in Blacklist or Whitelist and offers deletion functionality.
![img_6.png](img_6.png)

#### (3) Settings
The Settings section provides UDAS service startup management and other settings management functions.
![img_7.png](img_7.png)

* UDAS Detector Daemon: Used to start/stop the Detecting service. (Requires sudo privileges)
* UDAS Listener Daemon: Used to start/stop the Listener service.
* Block Non Serial Device: Used to enable/disable the function that immediately blocks USB storage devices without a serial number. (Requires sudo privileges)
* Apply Blacklist Policy: Used to enable/disable the function that registers newly detected USB storage devices as Blacklist devices if they are not whitelisted. (Requires sudo privileges)
* Change UDAS Password: Changes the UDAS management password. (Requires sudo privileges)
* UDAS Log level: Changes the log level. (Requires sudo privileges)


#### (4) Logging
Displays UDAS log records. You can filter the results by major log levels.
![img_8.png](img_8.png)
<br>

### 5. Uninstall
```commandline
sudo dpkg -r udas
```
* After uninstallation, please follow the on-screen guide for subsequent steps.