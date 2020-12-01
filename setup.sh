#!/bin/bash
#
PYTHON="python3"
PIP="pip3"


# create venv
$PYTHON -m venv .venv


# activate venv
source .venv/bin/activate

# install dependencies
$PIP install numpy matplotlib pandas
$PIP install adjustText # (optional)

# leave venv
deactivate


# sudo apt-get install python3-tk # (Debian'ish)
##sudo dnf install python3-tkinter # (Fedora-flavoured)
##sudo pacman -S tk # (Arch)


# setup data sources
wget https://download.geonames.org/export/dump/countryInfo.txt
git clone --depth=1 -b web-data https://github.com/CSSEGISandData/COVID-19.git
git clone --depth=1 https://github.com/coviddata/coviddata.git

