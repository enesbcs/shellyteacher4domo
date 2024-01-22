#!/bin/bash
echo "ShellyTeacher dependency solver"
DISPLAY=`printenv DISPLAY`
SUDO=`command -v sudo`
_SYSTEM=""
if [ "$(id -u)" -eq 0 ]; then
  echo "Virtualenv only installs packages to the actual user!"
  exit
fi
if [ -z `command -v command` ]
then
   echo "Command not found!"
   exit
fi
if [ ! -z `command -v apt-get` ]
then
   _SYSTEM="apt-get"
elif [ ! -z `command -v pacman` ]
then
   _SYSTEM="pacman"
elif [ ! -z `command -v apk` ]
then
   _SYSTEM="apk"
else
   echo "Not supported system!"
   exit
fi

if [ "$_SYSTEM" = "apt-get" ]
then
  if [ ! -z `command -v sudo` ]
  then
   _SYSTEM="sudo $_SYSTEM"
  fi
  $_SYSTEM update
  $_SYSTEM install -y python3 python3-pip python3-venv
  if [ ! -z "$DISPLAY" ]
  then
   $_SYSTEM install -y python3-tk
  fi
fi
if [ "$_SYSTEM" = "pacman" ]
then
  if [ ! -z `command -v sudo` ]
  then
   _SYSTEM="sudo $_SYSTEM"
  fi
  echo -ne '\n' | $_SYSTEM -S python python-pip
  if [ ! -z "$DISPLAY" ]
  then
   echo -ne '\n' | $_SYSTEM -S tk
  fi
fi
if [ "$_SYSTEM" = "apk" ]
then
  _SED="sed"
  if [ ! -z `command -v sudo` ]
  then
   _SYSTEM="sudo $_SYSTEM"
   _SED="sudo sed"
  fi
  _SED= -i '/community/s/^#//' /etc/apk/repositories
  $_SYSTEM update
  $_SYSTEM add python3 py3-pip
  if [ ! -z "$DISPLAY" ]
  then
   $_SYSTEM add python3-tkinter
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
if [ ! -z `command -v pip3` ]
then
 _PIP="pip3"
elif [ ! -z `command -v pip` ]
then
 _PIP="pip"
else
 _PIP=""
 echo "Pip not found, something went really badly!"
 exit
fi
if [ ! -z "$_PYTHON" ]
then
 $_PYTHON -m venv paho
 source paho/bin/activate
 $_PIP install paho-mqtt
else
 echo "Python3 not found, something went really badly!"
 exit
fi
echo "Installation ended for current user, try to run shellyteacher with venv using: ./run.sh"
