#Source https://github.com/UrekD/Steam-Workshop-Monitor
import asyncio
from colorama import Fore, Style
import datetime
import json
import httpx
import aiofiles
from nextcord.ext import commands

TOKEN = 'token' # bot token
#NUMBERS/INTS don't need to be put in ''
where = 1234 #where to send update notification
nrole = 1234 #role to ping on update
ctime = 900 #check interval in seconds
#collectionid = 1332156191 #collection ID uncoment to fill, after it fills comment it again and restart!
cname = 'workshop' #channel name where you can use commands $list $remove $add
with open('config.json', "rb") as infile:
    config = json.load(infile)
    mods = config["userdata"].get('workshopid')



event = asyncio.Event()   
event.set()

async def Monitor():
    now = datetime.datetime.now()
    print (now.strftime(f"{Fore.MAGENTA}[Monitor] Start {Style.RESET_ALL}%H:%M:%S"))
    i = 0
    mods = config["userdata"].get('workshopid')
    for mod in mods:
        mod = mod.split('#')
        try:
            await CheckOne(mod,i)
        except Exception as exc:
            print(now.strftime(f"{Fore.MAGENTA}[ERROR] {Style.RESET_ALL}%H:%M:%S {mod}, {exc}"))
            await err(mod[0])    
        i = i+1
    print (now.strftime(f"{Fore.MAGENTA}[Monitor] End {Style.RESET_ALL}%H:%M:%S"))
    async with aiofiles.open('config.json', mode='w') as jsfile:
            await jsfile.write(json.dumps(config))

async def update(uid):
    channel = bot.get_channel(where)
    await channel.send(f"Mod Updated: https://steamcommunity.com/sharedfiles/filedetails/?id={uid} <@&{nrole}>")

async def err(uid):
    channel = bot.get_channel(where)
    await channel.send(f"ERROR: https://steamcommunity.com/sharedfiles/filedetails/?id={uid} Unable to retreive!")

async def CheckOne(modC,i):
    asyncio. sleep(1) 
    body = 'itemcount=1&publishedfileids[0]=2638049909'
    url = 'https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/'
    myobj = {'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8', 'itemcount' : 1, 'publishedfileids[0]':modC[0] }
    async with httpx.AsyncClient() as r:
        wdetails = await r.post(url, data = myobj)
    epoch_time = wdetails.json()['response']['publishedfiledetails'][0]['time_updated']
    if int(epoch_time)!=int(modC[1]):
        config["userdata"].get('workshopid')[i] = f"{modC[0]}#{epoch_time}"
        sid = wdetails.json()['response']['publishedfiledetails'][0]['publishedfileid']
        now = datetime.datetime.now()
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
        with open('config.json', "w") as jsfile:
            json.dump(config, jsfile)
            jsfile.close()
    except:
        print("{Fore.RED}[ERROR] {Style.RESET_ALL}Collection was not parsed correctly try again!")    

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
            with open('config.json', "rb") as infile:
                config = json.load(infile)
                mods = config["userdata"].get('workshopid')
            await ctx.send(mods)
       else:
            await ctx.send("Wait untill update check finishes!")


@bot.command()
async def remove(ctx,arg):
    if ctx.channel.name == cname:
        if event.is_set() is False:
            try:
                idsx = config["userdata"]['workshopid']               
                idsx.remove(arg)
                config["userdata"]['workshopid'] = idsx
                async with aiofiles.open('config.json', mode='w') as jsfile:
                    await jsfile.write(json.dumps(config))
                await ctx.send(f"Removed element {arg}")
            except Exception as exc:
                await ctx.send(f"Error has accured {exc}")
        else:
            await ctx.send("Wait untill update check finishes!")        

@bot.event
async def on_ready():
    print(f'{Fore.MAGENTA}[INFO] {Fore.RED}{bot.user}{Style.RESET_ALL} has connected to nextcord!')

@bot.command()
async def add(ctx,arg):
    if ctx.channel.name == cname:
        if event.is_set() is False:
            try:
                idsx = config["userdata"]['workshopid'] 
                idsx.append(arg)
                config["userdata"]['workshopid'] = idsx
                async with aiofiles.open('config.json', mode='w') as jsfile:
                    await jsfile.write(json.dumps(config))
                await ctx.send(f"Added element {arg}")
            except Exception as exc:
                await ctx.send(f"Error has accured {exc}")
        else:
            await ctx.send("Wait untill update check finishes!")

try:
    print("Filling config")
    CollectionToConfig(collectionid)
    print("Finished")
except:
    print("No collection id did not refill")

bot.run(TOKEN)
