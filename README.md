[![Release downloads](https://img.shields.io/github/downloads/enesbcs/shellyteacher4domo/total.svg)]() [![Code size](https://img.shields.io/github/languages/code-size/enesbcs/shellyteacher4domo)]() [![Last commit](https://img.shields.io/github/last-commit/enesbcs/shellyteacher4domo)]()

# ShellyTeacher 4 Domoticz beta test version

WARNING: THIS IS A TEST VERSION!

Shelly device teacher for Domoticz MQTT Autodiscovery hardware

You need to understand before installation:
- this is not compatible with the old ShellyMQTT plugin, its based on a different hardware, which will create new devices
- only the Shelly device types listed in the "Implemented devices" will be recognised, but you can change/enhance templates.txt file to add more devices
- its not a plugin, nor a service, it doesn't need to run all the time - only once (Domoticz MQTT Autodiscovery is the Domoticz integrated hardware)

## How it works
When this program started it connects to the MQTT server and awaits for Shelly device announcements.
[Domoticz MQTT Autodiscovery hardware](https://www.domoticz.com/wiki/MQTT#Add_hardware_.22MQTT_Auto_Discovery_Client_Gateway.22) has to be enabled and Shelly devices has to connect to the same [MQTT broker](https://www.domoticz.com/wiki/MQTT#Installing_Mosquitto),
as the Domoticz and this program.

## How to install

For Linux users for any platform capable of running python3:

-Install git (Debian/Ubuntu if user has root right)
```
apt install git
```
-OR install git (Debian/Ubuntu if user has sudo right)
```
sudo apt install git
```
-Download application with git
```
git clone -b testing https://github.com/enesbcs/shellyteacher4domo.git shellyteacher4domo-testing
```
-Run the installation script first, and only once (which will deal python venv)
```
cd shellyteacher4domo-testing
./preinstall.sh
```
-If installation was succesful, ShellyTeacher now can be run from the venv named 'paho' with this command:
```
./run.sh
```

In case you want to save the configurations after rebooting, please make sure that MQTT broker [persistence settings](https://pagefault.blog/2020/02/05/how-to-set-up-persistent-storage-for-mosquitto-mqtt-broker/) configured correctly!

A GUI is also available when TKInter works, this is the default now, Console mode can be requested by specifying -c parameter at the command line!

[![Youtube tutorial](https://img.youtube.com/vi/3PvYhFIsVN4/0.jpg)](https://www.youtube.com/watch?v=3PvYhFIsVN4)

HINT: If you have to add multiple Shelly devices to MQTT, you can use [Shelly Scanner](https://www.usna.it/shellyscanner/index_en.html) app to set MQTT on them.

## How to update the program
First: backup your templates.txt files if you modified it, than:
```
git pull
```

## How to use

1. Edit settings.py file with a plain text editor, and set MQTT server IP address. If discovery prefix is leaved as default 'homeassistant' on the Domoticz MQTT AD hardware, than other settings will fine.
2. Make sure that the Shelly device connects to the same MQTT broker IP address.
3. Start Teacher
```
cd shellyteacher4domo-testing
./run.sh
```
4. Power Shelly device or restart it
5. If Teacher finds the device ID in the mqtt_templates.txt, those will be automatically forwarded for the Discovery topic, and as the default publish method is 'RETAIN', it will survive reboot, and Teacher application is not needed to run, until you wants a new Shelly device to be installed

(In case of Gen2/Gen3 device, the device has to be started before the Teacher, and make sure to enable "Generic status update over MQTT" at MQTT settings page)

A GUI is also available when TKInter works, this is the default now, Console mode can be requested by specifying -c parameter at the command line!

## Implemented devices
Gen1:
- Shelly 1 / 1PM / 1L
- Shelly 2/Shelly 2.5 relay and roller mode
- Shelly Plug / Plug S
- Shelly 4 Pro
- Shelly H&T
- Shelly Motion 1/2
- Shelly Door Window 1/2
- Shelly Button
- Shelly i3
- Shelly Duo
- Shelly Dimmer 1/2
- Shelly Vintage
- Shelly UNI
- Shelly EM
- Shelly 3EM
- Shelly Smoke
- Shelly Flood
- Shelly Gas
- Shelly2LED
- Shelly RGBW2 (*only with 4 channel white mode)
- Shelly TRV (needs Domoticz 2023 beta 15515 or later)

Gen2:
- Shelly Plus 1 / 1PM / 1 Mini / 1PM Mini
- Shelly PM Mini
- Shelly Plus 2PM [(* see position fix)](https://github.com/enesbcs/shellyteacher4domo/wiki/Shelly-2PM-Cover-Position)
- Shelly Plus Plug
- Shelly Plus H&T
- Shelly Plus I4
- Shelly Pro 1 / 1PM
- Shelly Pro 2 / 2PM [(* see position fix)](https://github.com/enesbcs/shellyteacher4domo/wiki/Shelly-2PM-Cover-Position)
- Shelly Pro 3 / 3EM
- Shelly Pro 4PM
- Shelly Pro Dual Cover PM

Gen3:
- Shelly 1 Mini G3 / 1PM Mini G3
- Shelly PM Mini G3
- Shelly HT G3

Tasmota:
- Relays and simple sensors (temperature, humidity, pressure, analog input..) published by the TasmotaDiscovery

## Known problems with devices
- Every Gen1 RGB devices will not work (see https://github.com/enesbcs/shellyteacher4domo/issues/7)
- Tasmota covers not supported
