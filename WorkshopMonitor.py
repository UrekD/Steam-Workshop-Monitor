#Source https://git.urek.eu
import asyncio
from colorama import Fore, Style
import datetime
import json
import httpx
import aiofiles
import os
import numpy as np
import math
import nextcord
from nextcord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
where = int(os.getenv('where')) 
nrole = int(os.getenv('nrole'))
ctime = int(os.getenv('ctime'))
cdelay = int(os.getenv('cdelay'))
cretry = int(os.getenv('cretry'))
rdelay = int(os.getenv('rdelay'))
fdelay = int(os.getenv('fdelay'))
collectionid = os.getenv('collectionid')
status = os.getenv('status')
cname = os.getenv('cname') 
oup = False

event = asyncio.Event()   

async def Monitor():
    now = datetime.datetime.now()
    print (now.strftime(f"{Fore.MAGENTA}[Monitor] Start {Style.RESET_ALL}%H:%M:%S"))
    i = 0
    with open('data/config.json', "rb") as infile:
        configx = json.load(infile)
        mods = configx["userdata"].get('workshopid')
        global oup
        oup = False
    for mod in mods:
        mod = mod.split('#')
        try:
            await CheckOne(mod,i)
            now = datetime.datetime.now()
            print(now.strftime(f"{Fore.MAGENTA}[CHECKED] {Style.RESET_ALL}%H:%M:%S {mod}"))
        except Exception as exc:
            now = datetime.datetime.now()
            print(now.strftime(f"{Fore.MAGENTA}[RECHECK] {Style.RESET_ALL}%H:%M:%S {mod}, {exc}"))
            await asyncio. sleep(rdelay)
            for x in range(cretry):
                try:
                    await CheckOne(mod,i)
                    now = datetime.datetime.now()
                    print(now.strftime(f"{Fore.MAGENTA}[EXCHECKED] {Style.RESET_ALL}%H:%M:%S {mod}"))
                    break
                except Exception as exc:
                    now = datetime.datetime.now()
                    print(now.strftime(f"{Fore.MAGENTA}[ERROR] {Style.RESET_ALL}%H:%M:%S {mod}, {exc}"))
                    if x is cretry-1:
                        await err(mod[0])
    now = datetime.datetime.now()
    print (now.strftime(f"{Fore.MAGENTA}[Monitor] End {Style.RESET_ALL}%H:%M:%S"))
    if oup is True:
        async with aiofiles.open('data/config.json', mode='w') as jsfile:
            await jsfile.write(json.dumps(config))

async def update(uid):
    channel = bot.get_channel(where)
    await channel.send(f"Mod Updated: https://steamcommunity.com/sharedfiles/filedetails/?id={uid} <@&{nrole}>")

async def err(uid):
    channel = bot.get_channel(where)
    await channel.send(f"ERROR: https://steamcommunity.com/sharedfiles/filedetails/?id={uid} Unable to retreive!")

async def CheckOne(modC,i):
    await asyncio. sleep(cdelay) 
    url = 'https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/'
    myobj = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'itemcount' : 1, 'publishedfileids[0]':modC[0] }
    async with httpx.AsyncClient() as r:
        wdetails = await r.post(url, data = myobj)
    epoch_time = wdetails.json()['response']['publishedfiledetails'][0]['time_updated']
    if int(epoch_time)!=int(modC[1]):
        config["userdata"].get('workshopid')[i] = f"{modC[0]}#{epoch_time}"
        sid = wdetails.json()['response']['publishedfiledetails'][0]['publishedfileid']
        now = datetime.datetime.now()
        global oup
        oup = True
        print(now.strftime(f"{Fore.MAGENTA}[Update] {Style.RESET_ALL}{sid} %H:%M:%S"))
        if int(modC[1])!=000:
            await update(sid)


def CollectionToConfig(id):
    try:
        body = 'publishedfileids[0]' 
        url = 'https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1/'
        myobj = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'collectioncount':1,body: id }
        collection = httpx.post(url, data = myobj)
        modss = collection.json()['response']['collectiondetails'][0]['children']
        ids = []
        for  item in modss:
            temp = item['publishedfileid']
            ids.append(f"{temp}#000")
        config["userdata"]['workshopid'] = ids
        with open('data/config.json', "w") as jsfile:
            json.dump(config, jsfile)
            jsfile.close()
    except Exception as exc:
        print(f"{Fore.RED}[ERROR] {Style.RESET_ALL}Collection was not parsed correctly try again! {exc}")    

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task(event))

    async def on_disconnect(self):
        now = datetime.datetime.now()
        print(now.strftime(f"{Fore.MAGENTA}[DISCONNECTED] {Style.RESET_ALL}%H:%M:%S "))

    async def on_resumed(self):
        now = datetime.datetime.now()
        print(now.strftime(f"{Fore.MAGENTA}[RESUME] {Style.RESET_ALL}%H:%M:%S "))

    async def on_ready(self):
        x = status
        if x is None:
            x = "git.urek.eu | $help"
        await bot.change_presence(activity=nextcord.Game(name=x))
        now = datetime.datetime.now()
        print(now.strftime(f'{Fore.MAGENTA}[INFO] %H:%M:%S {Fore.RED}{bot.user}{Style.RESET_ALL} has connected to nextcord!'))

    async def my_background_task(self,LA):
        await self.wait_until_ready()
        while not self.is_closed():
            try:
                channel = self.get_channel(where) 
                while event.is_set():
                    await channel.send("Command is still running delaying check for 5 seconds..")
                    await asyncio.sleep(5)
                event.set()
                await channel.send("Checking for updates!")
                await Monitor()
                await channel.send("Checking finished sleeping...")
                event.clear()  
                await asyncio.sleep(ctime)
            except:
                event.clear() 
                now = datetime.datetime.now()
                print(now.strftime(f"{Fore.MAGENTA}[STOP] {Style.RESET_ALL}%H:%M:%S An error has accured current monitor cycle skipped!"))
                await asyncio.sleep(fdelay) 

bot = Bot(command_prefix='$')
bot.remove_command('help')

@bot.command()
async def ping(ctx):
    if ctx.channel.name == cname:
        await ctx.reply('Pong!')

@bot.command()
async def help(ctx):
    if ctx.channel.name == cname:
        embed=nextcord.Embed(title="Steam-Workshop-Monitor Help", url="https://github.com/UrekD/Steam-Workshop-Monitor", color=0xff0000)
        embed.set_author(name="Steam-Workshop-Monitor Help", url="https://github.com/UrekD/Steam-Workshop-Monitor", icon_url="https://icons.iconarchive.com/icons/icons8/windows-8/512/Logos-Steam-icon.png")
        embed.set_thumbnail(url="https://icons.iconarchive.com/icons/icons8/windows-8/512/Logos-Steam-icon.png")
        embed.add_field(name="$ping", value="Pong!", inline=False)
        embed.add_field(name="$list", value="Lists all mods from current config.", inline=False)
        embed.add_field(name="$remove mod#time", value="Removes specified mod from current configuration ex. $remove 1439779114#1531480087 ", inline=False)
        embed.add_field(name="$add modid#000", value="Adds a mod to config in format modid#000, ex. $add 1439779114#000 ", inline=False)
        embed.add_field(name="$clear", value="Removes all mods from the config.", inline=False)
        embed.add_field(name="$refill workshopid", value="Overwrites the config with the mods in workshop collection. ex, $refill 1332156191", inline=False)
        await ctx.send(embed=embed)

@bot.command()
async def list(ctx):
    if ctx.channel.name == cname:
       if event.is_set() is False:
            event.set()
            with open('data/config.json', "rb") as infile:
                config = json.load(infile)
                mods = config["userdata"].get('workshopid')
                c=math.ceil(len(mods)/80)
            for mod in np.array_split(mods, c):
                await ctx.send(mod)
            event.clear()
       else:
            await ctx.send("Wait until update check finishes!")

@bot.command()
async def remove(ctx,arg):
    if ctx.channel.name == cname:
        if event.is_set() is False:
            try:
                event.set()
                idsx = config["userdata"]['workshopid']               
                idsx.remove(arg)
                config["userdata"]['workshopid'] = idsx
                async with aiofiles.open('data/config.json', mode='w') as jsfile:
                    await jsfile.write(json.dumps(config))
                await ctx.send(f"Removed element {arg}")
            except Exception as exc:
                await ctx.send(f"Error has accured {exc}")
            event.clear()
        else:
            await ctx.send("Wait until update check finishes!")        

@bot.command()
@commands.check_any(commands.is_owner())
async def say(ctx,arg):
    channel = bot.get_channel(where)
    await channel.send(f"{arg}")

@bot.command()
async def clear(ctx):
    if ctx.channel.name == cname:
        if event.is_set() is False:
            try:
                event.set()
                d = [] 
                config["userdata"]['workshopid'] = d
                async with aiofiles.open('data/config.json', mode='w') as jsfile:
                    await jsfile.write(json.dumps(config))
                await ctx.send("Cleared the config")
            except Exception as exc:
                await ctx.send(f"Error has accured {exc}")
            event.clear()
        else:
            await ctx.send("Wait until update check finishes!")

@bot.command()
async def add(ctx,arg):
    if ctx.channel.name == cname:
        if event.is_set() is False:
            try:
                event.set()
                idsx = config["userdata"]['workshopid'] 
                idsx.append(arg)
                config["userdata"]['workshopid'] = idsx
                async with aiofiles.open('data/config.json', mode='w') as jsfile:
                    await jsfile.write(json.dumps(config))
                await ctx.send(f"Added element {arg}")
            except Exception as exc:
                await ctx.send(f"Error has accured {exc}")
            event.clear()
        else:
            await ctx.send("Wait until update check finishes!")

@bot.command()
async def refill(ctx,arg):
    if ctx.channel.name == cname:
        if event.is_set() is False:
            try:
                event.set()
                CollectionToConfig(int(arg))
                await ctx.send("Cleared and filled config with collection!")
            except Exception as exc:
                await ctx.send(f"Error has accured {exc}")
            event.clear()
        else:
            await ctx.send("Wait until update check finishes!")

with open('data/config.json', "rb") as infile:
    config = json.load(infile)
    mods = config["userdata"].get('workshopid')

if collectionid is not None:
    try:
        print(f"{Fore.MAGENTA}[Fill] Filling config")
        CollectionToConfig(int(collectionid))
        print(f"{Fore.MAGENTA}[Fill] Finished")
    except:
        print(f"{Fore.MAGENTA}[Fill] Error filling collection")

bot.run(TOKEN,reconnect=True)
