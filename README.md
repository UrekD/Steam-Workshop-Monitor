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
# Commands
**$ping**

![image](https://user-images.githubusercontent.com/38784343/140180871-9647cb59-8bdd-4af5-bccf-f7864e572628.png)

**$list**

Returns a list of mods in a JSON object, format 'MODID#TIME'.
Time format is in Unix epoch time https://www.epochconverter.com/

![image](https://user-images.githubusercontent.com/38784343/140181008-43802124-4154-461f-ad78-50a2a69f9425.png)

**$remove**

Firstly locate the mod via the ID and copy the whole format and remove it via the command.

![image](https://user-images.githubusercontent.com/38784343/140181570-7d4b4d49-3468-4919-9571-febe9ccd0ad8.png)

**$add**

Add the mod with the following format MODID#000 ex. "$add 450814997#000"
If you use 000 it should not trigger a update notification.

![image](https://user-images.githubusercontent.com/38784343/140181637-731a1a32-6538-406e-8fcc-0e5eb925c143.png)

# Example

![image](https://user-images.githubusercontent.com/38784343/140175801-4395f62c-a4bf-4de5-9f50-59e4909336a2.png)
