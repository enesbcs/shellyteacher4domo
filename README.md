# ShellyTeacher 4 Domoticz
Shelly device teacher for Domoticz MQTT Autodiscovery hardware

**This is a beta test version, make sure to not use on production server. You have been warned!**

## How it works
When this program started it connects to the MQTT server and waits Shelly device announcements.
Domoticz MQTT Autodiscovery hardware has to be enabled and Shelly devices has to connect to the same MQTT broker,
as the Domoticz and this program.

## How to install

```
sudo apt install python3-pip git
pip3 install paho-mqtt
git clone https://github.com/enesbcs/shellyteacher4domo.git
```

## How to update to program
First: save your templates.txt files if you modified it, than:
```
git pull
```

## How to use

1. Edit settings.py file with a plain text editor, and set MQTT server IP address. If discovery prefix is leaved as default 'homeassistant' on the Domoticz MQTT AD hardware, than other settings will fine.
2. Make sure that the Shelly device connects to the same MQTT broker IP address.
3. Start Teacher
> python3 shellyteacher4domo.py
4. Power Shelly device or restart it
5. If Teacher finds the device ID in the mqtt_templates.txt, those will be automatically forwarded for the Discovery topic, and as the default publish method is 'RETAIN', it will survive reboot, and Teacher application is not needed to run, until you wants a new Shelly device to be installed

(In case of Gen2 device, the device has to be started before the Teacher, and make sure to enable "Generic status update over MQTT" at MQTT settings page)

## Tested and working devices
Gen1:
- Shelly 1
- Shelly 1 PM
- Shelly 1L
- Shelly 2/Shelly 2.5 relay and roller mode
- Shelly Plug and Plug S
- Shelly 4 Pro
- Shelly H&T
- Shelly Motion
- Shelly Door Window 1/2
- Shelly Button
- Shelly i3
- Shelly Duo
- Shelly Dimmer 1/2

Gen2:
- Shelly Plus 1

## Tested and partially working devices
- Shelly RGB Bulb (RGB is faulty in Domoticz AD...)
- Energy reporting will not be good, until Domoticz AD supports basic math in templates
