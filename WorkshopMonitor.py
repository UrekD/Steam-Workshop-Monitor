#Source https://github.com/UrekD/Steam-Workshop-Monitor
import asyncio
from colorama import Fore, Style
import datetime
import json
import httpx
import aiofiles
import os
import numpy as np
import math
from nextcord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TOKEN')
where = int(os.getenv('where')) 
nrole = int(os.getenv('nrole'))
ctime = int(os.getenv('ctime'))
cdelay = int(os.getenv('cdelay'))
collectionid = os.getenv('collectionid')
cname = os.getenv('cname') 
oup = False

event = asyncio.Event()   
event.set()

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
            await asyncio. sleep(5) 
            try:
                await CheckOne(mod,i)
                now = datetime.datetime.now()
                print(now.strftime(f"{Fore.MAGENTA}[CHECKED] {Style.RESET_ALL}%H:%M:%S {mod}"))
            except Exception as exc:
                now = datetime.datetime.now()
                print(now.strftime(f"{Fore.MAGENTA}[ERROR] {Style.RESET_ALL}%H:%M:%S {mod}, {exc}"))
                await err(mod[0])
        i = i+1
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


    async def my_background_task(self,LA):
        await self.wait_until_ready()
        channel = self.get_channel(where) 
        while not self.is_closed():
            event.set()
            await channel.send("Checking for updates!")
            await Monitor()
            await channel.send("Checking finished sleeping...")
            event.clear()
            await asyncio.sleep(ctime) 

bot = Bot(command_prefix='$')

@bot.command()
async def ping(ctx):
    await ctx.reply('Pong!')

@bot.command()
async def list(ctx):
    if ctx.channel.name == cname:
       if event.is_set() is False:
            with open('data/config.json', "rb") as infile:
                config = json.load(infile)
                mods = config["userdata"].get('workshopid')
                c=math.ceil(len(mods)/80)
            for mod in np.array_split(mods, c):
                await ctx.send(mod)
            
       else:
            await ctx.send("Wait until update check finishes!")

@bot.command()
async def remove(ctx,arg):
    if ctx.channel.name == cname:
        if event.is_set() is False:
            try:
                idsx = config["userdata"]['workshopid']               
                idsx.remove(arg)
                config["userdata"]['workshopid'] = idsx
                async with aiofiles.open('data/config.json', mode='w') as jsfile:
                    await jsfile.write(json.dumps(config))
                await ctx.send(f"Removed element {arg}")
            except Exception as exc:
                await ctx.send(f"Error has accured {exc}")
        else:
            await ctx.send("Wait until update check finishes!")        

@bot.event
async def on_ready():
    print(f'{Fore.MAGENTA}[INFO] {Fore.RED}{bot.user}{Style.RESET_ALL} has connected to nextcord!')

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
                d = [] 
                config["userdata"]['workshopid'] = d
                async with aiofiles.open('data/config.json', mode='w') as jsfile:
                    await jsfile.write(json.dumps(config))
                await ctx.send(f"Cleared the config")
            except Exception as exc:
                await ctx.send(f"Error has accured {exc}")
        else:
            await ctx.send("Wait until update check finishes!")

@bot.command()
async def add(ctx,arg):
    if ctx.channel.name == cname:
        if event.is_set() is False:
            try:
                idsx = config["userdata"]['workshopid'] 
                idsx.append(arg)
                config["userdata"]['workshopid'] = idsx
                async with aiofiles.open('data/config.json', mode='w') as jsfile:
                    await jsfile.write(json.dumps(config))
                await ctx.send(f"Added element {arg}")
            except Exception as exc:
                await ctx.send(f"Error has accured {exc}")
        else:
            await ctx.send("Wait until update check finishes!")

with open('data/config.json', "rb") as infile:
    config = json.load(infile)
    mods = config["userdata"].get('workshopid')

if collectionid != None:
    try:
        print(f"{Fore.MAGENTA}[Fill] Filling config")
        CollectionToConfig(int(collectionid))
        print(f"{Fore.MAGENTA}[Fill] Finished")
    except:
        print(f"{Fore.MAGENTA}[Fill] Error filling collection")



bot.run(TOKEN)
