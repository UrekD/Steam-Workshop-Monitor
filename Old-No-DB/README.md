# Steam-Workshop-Monitor<br />![GitHub all releases](https://img.shields.io/github/downloads/UrekD/Steam-Workshop-Monitor/total?style=for-the-badge) ![GitHub repo size](https://img.shields.io/github/repo-size/UrekD/Steam-Workshop-Monitor?style=for-the-badge) ![GitHub last commit](https://img.shields.io/github/last-commit/UrekD/Steam-Workshop-Monitor?style=for-the-badge) ![GitHub stars commit](https://img.shields.io/github/stars/UrekD/Steam-Workshop-Monitor?style=for-the-badge)

Discord bot to monitor collection of mods on the Steam Workshop and notify on update to selected Discord channel via Nextcordbot API.
# Requirements

- Python 3.10 or later
- Python pip -> requirements.txt
- Discord bot token
# Setup
**Linux**
```py
git clone https://github.com/UrekD/Steam-Workshop-Monitor/
cd Steam-Workshop-Monitor/
pip3 install -r requirements.txt
#Edit info in .env
python3 WorkshopMonitor.py
#Wait till config fills then ctrl+c
#Comment out l5 in .env
python3 WorkshopMonitor.py
```
**Windows**
```py
Downloadn the repo and extract to an empty folder
Open a CLI ex. CMD,PS,GitBash in the directory
pip3 install -r requirements.txt
#Edit info in .env
python3 WorkshopMonitor.py
#Wait till config fills then ctrl+c
#Comment out l5 in .env
python3 WorkshopMonitor.py
```
**Docker Compose**

If collectionid var is present it overwrites the config, so run it then comment it out!
After mounting the volume you can also edit it manually with a text editor on the machine.
```docker
version: "3"
services:
  workshopmonitor:
    image: look at from https://github.com/UrekD/Steam-Workshop-Monitor/pkgs/container/steam-workshop-monitor/34820545?tag=main
    environment:
      - TOKEN=fmSUjZKW.To)v<eDw_8VZG<Pik#yN #bot token
      - where=935678087209856 #channel ID to send notification
      - nrole=9124604480608221 #role id to ping on notify
      - ctime=900 #time between checks in seconds
      - collectionid=1332156191 #workshop collection id found in url
      - cdelay=1 #delay between each mods checked in seconds
      - rdelay=5 #delay on recheck in seconds
      - cretry=3 #how many times to retry the recheck mod
      - fdelay=300 #how many seconds to wait until monitor runs again after failure ex. on internet failure
    volumes:
      - botdataa:/data
      
volumes:
  botdataa:
```
volumes:
  botdataa:

# Commands
Integrated with Discord Slash commands!

![image](https://user-images.githubusercontent.com/38784343/172271297-94e52c55-05b8-4860-ad5d-cdd5c7506d00.png)


# Example

![image](https://user-images.githubusercontent.com/38784343/140175801-4395f62c-a4bf-4de5-9f50-59e4909336a2.png)
