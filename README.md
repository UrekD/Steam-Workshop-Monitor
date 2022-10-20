# Steam-Workshop-Monitor
Discord bot to notify you when your server mods get updated on the Steam workshop. 

# How it works

Upon joining it creates a channel and a role where it will send notifications, once a mod get's updated which you added using the /add command. This is achived by quering the public Steam API and comparing the update times with those stored in the database.

# Commands

Integrated with Discord Slash commands!

![image](https://user-images.githubusercontent.com/38784343/184500803-914e80fb-cb85-404c-99da-ce04cbbb4fa7.png)

# Example

![image](https://user-images.githubusercontent.com/38784343/184500866-1cb62599-5a17-4a5c-83ca-0e26f720acda.png)
![image](https://user-images.githubusercontent.com/38784343/184500884-5df21822-885e-4ab2-87e1-482a8718cacd.png)


# Deployment

## Requirements

- Redis DB (Redis lab offers free hosting)
- MySQL DB (Import DB from db.sql)
- Discord bot (Needs scope applications.commands and bot-administrator)
- Docker host

**Docker Compose**<br>
Some things such as status, cleanup, top.gg task are hardcoded so require enabling in code and building your own image!

```docker
version: "3.1"
services:
  workshopmain:
    image: ghcr.io/urekd/steam-workshop-monitor:main	
    container_name: workshopmonitor
    environment:
      - RHOST=cloud.redislabs.com #Redis host
      - RPASS=testpassword #Redis pass
      - RPORT=50421 #Redis port
      - RUSER=default #Redis user
      - RINDEX=0 #Redis db index
      - TZ=Europe/Berlin #Your timezone
      - TOKEN=NzUyMjEzMDM3MDc5MDY4ODMy.X1UW-w.tcVSMWKbIU9smbSJa7EDAteqALU #Bot token
      - DBHOST=192.168.0.2 #MySQL host
      - DBUSER=workshopbot #MySQL User
      - DBPASS=pass123
      - DB=workshop
      - ccount=6 #Command times per CDTIME
      - cdtime=30 #Seconds of cooldown
      - ttltime=3600 #Redis key time to live
      - ctime=300 #Check interval in seconds
      - fdelay=120 #Run delay on monitor fail (ex. API is down)
      - chdebug=1234 (Channel where to send logs/debug to)
      - mincount=1 #Minimum count for mods Used in cleanup
    restart: unless-stopped
```
# Personal note

As of release of 1.0 I have stopped development of the bot as my verification was rejected: "I want to confirm that we're denying your verification request due to some concerns regarding your bot’s operation...". I have left comments in the code to help if anyone wishes to continue with it's development, I sadly didn't get to refactor nor implement all the things I had planned. The bot is fully functioning, the only bug I found was that ever since I moved it out of Oracle's cloud Redis likes to trow a 'connection reset by peer' every few hours. I also included a Drone pipeline I used with Gitea to automate deployment using Portainer, which makes it super simple to redeploy while developing.

The hosted instance of the bot will still be avaliable until further notice, but no guarantee of it's operation is given! [Invite](https://discord.com/api/oauth2/authorize?client_id=752213037079068832&permissions=8&scope=applications.commands%20bot) the bot to your guild. [Official Discord Server.](https://discord.gg/tSZmkdXnYv) If you want to monitor 25 or less items you can use [Steam Watch Bot](https://steam.watch/).

![](https://raw.githubusercontent.com/urekd/urekd/wbstats/overview.svg#gh-dark-mode-only)
![](https://raw.githubusercontent.com/urekd/urekd/wbstats/overview.svg#gh-light-mode-only)
