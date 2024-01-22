#!/bin/bash
echo "ShellyTeacher dependency solver"
echo "-------------------------------"
DISPLAY=`printenv DISPLAY`
if [ -z `command -v command` ]
then
   echo "Command not found!"
   exit
fi
_SUDO=`command -v sudo`
_SYSTEM=""
_ROOT=""
if [ "$(id -u)" -eq 0 ]; then
  _ROOT="y"
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
echo "If you are not root, the system may now ask root password several times. (You may consider to use sudo)"
if [ "$_SYSTEM" = "apt-get" ]
then
  if [ ! -z "$_SUDO" ]
  then
   _SYSTEM="sudo $_SYSTEM"
  fi
  if [ -z "$_SUDO" ] && [ -z "$_ROOT" ]; then
   su - root -c "$_SYSTEM update ; $_SYSTEM install -y python3 python3-pip python3-venv"
   if [ ! -z "$DISPLAY" ]
   then
    su - root -c "$_SYSTEM install -y python3-tk"
   fi
  else
   $_SYSTEM update
   $_SYSTEM install -y python3 python3-pip python3-venv
   if [ ! -z "$DISPLAY" ]
   then
    $_SYSTEM install -y python3-tk
   fi
  fi
fi
if [ "$_SYSTEM" = "pacman" ]
then
  if [ ! -z "$_SUDO" ]
  then
   _SYSTEM="sudo $_SYSTEM"
  fi
  if [ -z "$_SUDO" ] && [ -z "$_ROOT" ]; then
   su - root -c "echo -ne '\n' | $_SYSTEM -S python python-pip"
   if [ ! -z "$DISPLAY" ]
   then
    su - root -c "echo -ne '\n' | $_SYSTEM -S tk"
   fi
  else
   echo -ne '\n' | $_SYSTEM -S python python-pip
   if [ ! -z "$DISPLAY" ]
   then
    echo -ne '\n' | $_SYSTEM -S tk
   fi
  fi
fi
if [ "$_SYSTEM" = "apk" ]
then
  _SED="sed"
  if [ ! -z "$_SUDO" ]
  then
   _SYSTEM="sudo $_SYSTEM"
   _SED="sudo sed"
  fi
  if [ -z "$_SUDO" ] && [ -z "$_ROOT" ]; then
   su - root -c "$_SED -i '/community/s/^#//' /etc/apk/repositories"
   su - root -c "$_SYSTEM update ; $_SYSTEM add python3 py3-pip"
   if [ ! -z "$DISPLAY" ]
   then
    su - root -c "$_SYSTEM add python3-tkinter"
   fi
  else
   $_SED -i '/community/s/^#//' /etc/apk/repositories
   $_SYSTEM update
   $_SYSTEM add python3 py3-pip
   if [ ! -z "$DISPLAY" ]
   then
    $_SYSTEM add python3-tkinter
   fi
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
