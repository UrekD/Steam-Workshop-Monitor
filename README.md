# Steam-Workshop-Monitor
Discord bot for monitoring Steam Workshop items and be notified when they get updated. [Official Discord Server.](https://discord.gg/tSZmkdXnYv)<br><br>

![](https://raw.githubusercontent.com/urekd/urekd/wbstats/overview.svg#gh-dark-mode-only)
![](https://raw.githubusercontent.com/urekd/urekd/wbstats/overview.svg#gh-light-mode-only)

[Invite](https://discord.com/api/oauth2/authorize?client_id=752213037079068832&permissions=8&scope=applications.commands%20bot) the bot to your guild. Upon joining the bot will create a channel and role called workshop, where it will send the update notifications and any announcements about the bot. The role and channel can be freely renamed but not deleted. If they have been deleted you must kick and invite the bot again which will reset everything including your watched items. 
# Commands
Integrated with Discord Slash commands!

![image](https://user-images.githubusercontent.com/38784343/184500803-914e80fb-cb85-404c-99da-ce04cbbb4fa7.png)

# Example

![image](https://user-images.githubusercontent.com/38784343/184500866-1cb62599-5a17-4a5c-83ca-0e26f720acda.png)
![image](https://user-images.githubusercontent.com/38784343/184500884-5df21822-885e-4ab2-87e1-482a8718cacd.png)


# Self Hosting

**Docker Compose**

```docker
version: "3"
services:
  workshopmonitor:
    image: ghcr.io/urekd/steam-workshop-monitor:main
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
```
