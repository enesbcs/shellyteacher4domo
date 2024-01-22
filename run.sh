#!/bin/bash
FILE=/etc/mosquitto/mosquitto.conf
#Checking if the script running on the server itself...
if [ -f "$FILE" ]; then
   SUDO=`command -v sudo`
   echo "Mosquitto conf found. "
   _MOSQ=`$SUDO cat $FILE | grep persistence | grep true`
   if [ -z "$_MOSQ" ]
   then
     echo "persistence DISABLED - RETAIN settings wont survive reboot!"
   else
     echo "persistence ENABLED"
   fi
fi
if [ ! -z `command -v python3` ]
then
 _PYTHON="python3"
elif [ ! -z `command -v python` ]
then
 _PYTHON="python"
else
 _PYTHON=""
fi
#Activating virtualenv and starting ShellyTeacher
if [ ! -z "$_PYTHON" ]
then
 source paho/bin/activate
 $_PYTHON shellyteacher4domo.py
else
 echo "Python not found!"
fi
