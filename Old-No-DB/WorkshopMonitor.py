#Source https://git.urek.eu
import asyncio
from colorama import Fore, Style
import datetime
import json
import httpx
import aiofiles
import os
import nextcord
from nextcord.ext import commands, menus
from nextcord import Interaction, SlashOption, ChannelType
import nextcord
from dotenv import load_dotenv
from nextcord import Embed

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
oup = False

event = asyncio.Event()   
intents = nextcord.Intents(messages=False, guilds=True)

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
        i=i+1
    now = datetime.datetime.now()
    print (now.strftime(f"{Fore.MAGENTA}[Monitor] End {Style.RESET_ALL}%H:%M:%S"))
    if oup is True:
        async with aiofiles.open('data/config.json', mode='w') as jsfile:
            await jsfile.write(json.dumps(config, indent=4, sort_keys=True))

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
            jsfile.write(json.dumps(config, indent=4, sort_keys=True))
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
            x = "git.urek.eu | /help"
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
            except Exception() as x:
                event.clear() 
                now = datetime.datetime.now()
                print(x)
                print(now.strftime(f"{Fore.MAGENTA}[STOP] {Style.RESET_ALL}%H:%M:%S An error has accured current monitor cycle skipped!"))
                await asyncio.sleep(fdelay) 

bot = Bot(intents=intents)
bot.remove_command('help')

@bot.slash_command(name="help", description="help")
async def help(interaction: nextcord.Interaction):
    embed=nextcord.Embed(title="Steam-Workshop-Monitor Help", url="https://github.com/UrekD/Steam-Workshop-Monitor", color=0xff0000)
    embed.set_author(name="Steam-Workshop-Monitor Help", url="https://github.com/UrekD/Steam-Workshop-Monitor", icon_url="https://icons.iconarchive.com/icons/icons8/windows-8/512/Logos-Steam-icon.png")
    embed.set_thumbnail(url="https://icons.iconarchive.com/icons/icons8/windows-8/512/Logos-Steam-icon.png")
    embed.add_field(name="/ping", value="Pong!", inline=False)
    embed.add_field(name="/list", value="Lists all mods from current config.", inline=False)
    embed.add_field(name="/remove mod#time", value="Removes specified mod from current configuration ex. /remove 1439779114#1531480087 ", inline=False)
    embed.add_field(name="/add modid#000", value="Adds a mod to config in format modid#000, ex. /add 1439779114#000 ", inline=False)
    embed.add_field(name="/clear", value="Removes all mods from the config.", inline=False)
    embed.add_field(name="/fcheck", value="Force a check cycle indepentent of the interval.Force a check cycle indepentent of the interval", inline=False)
    embed.add_field(name="/refill workshopid", value="Overwrites the config with the mods in workshop collection. ex, /refill 1332156191", inline=False)
    await interaction.response.send_message(embed=embed)
    
class MyEmbedDescriptionPageSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=25)

    async def format_page(self, menu, entries):
        embed = Embed(title="Mods", description="\n".join(entries))
        embed.set_footer(text=f'Page {menu.current_page + 1}/{self.get_max_pages()}')
        return embed
        
@bot.slash_command(name="list", description="Lists all mods from current config.")
async def list(interaction: nextcord.Interaction):
   if event.is_set() is False:
        try:
            event.set()
            with open('data/config.json', "rb") as infile:
                config = json.load(infile)
                data = config["userdata"].get('workshopid')
            leng = len(data)
            t = 30
            if leng > 75:
                t = t * (leng/50)
            data = [f'{data[num]} #{num}' for num in range(0,leng)]
            pages = menus.ButtonMenuPages(
                        source=MyEmbedDescriptionPageSource(data),
                        clear_buttons_after=True,
                        timeout=t
                    )
            await pages.start(interaction=interaction)
            event.clear()
        except:
            event.clear()
            await interaction.response.send_message("Error is config empty?")
   else:
        await interaction.response.send_message("Wait until update check finishes!")


@bot.slash_command(name="remove", description="Removes specified mod from current configuration ex. /remove 1439779114#1531480087")
async def remove(interaction: nextcord.Interaction, arg: str):
    if event.is_set() is False:
        try:
            event.set()
            idsx = config["userdata"]['workshopid']               
            idsx.remove(arg)
            config["userdata"]['workshopid'] = idsx
            async with aiofiles.open('data/config.json', mode='w') as jsfile:
                await jsfile.write(json.dumps(config, indent=4, sort_keys=True))
            await interaction.response.send_message(f"Removed element {arg}")
        except Exception as exc:
            await interaction.response.send_message(f"Error has accured {exc}")
        event.clear()
    else:
        await interaction.response.send_message("Wait until update check finishes!")     

@bot.slash_command(name="fcheck", description="Force a check cycle indepentent of the interval.Force a check cycle indepentent of the interval.")
async def fcheck(interaction: nextcord.Interaction):
    if event.is_set() is False:
        try:
            event.set()
            await interaction.response.send_message("Checking...")
            channel = bot.get_channel(where) 
            await channel.send("Checking for updates!")
            await Monitor()
            await channel.send("Checking finished sleeping...")
            event.clear()  
        except Exception as exc:
            await interaction.response.send_message(f"Error has accured {exc}")
        event.clear()
    else:
        await interaction.response.send_message("Wait until update check finishes!")

@bot.slash_command(name="clear", description="Removes all mods from the config.")
async def clear(interaction: nextcord.Interaction):
    if event.is_set() is False:
        try:
            event.set()
            d = [] 
            config["userdata"]['workshopid'] = d
            async with aiofiles.open('data/config.json', mode='w') as jsfile:
                await jsfile.write(json.dumps(config, indent=4, sort_keys=True))
            await interaction.response.send_message("Cleared the config")
        except Exception as exc:
            await interaction.response.send_message(f"Error has accured {exc}")
        event.clear()
    else:
        await interaction.response.send_message("Wait until update check finishes!")

@bot.slash_command(name="add", description="Adds a mod to config in format modid#000, ex. /add 1439779114#000")
async def add(interaction: nextcord.Interaction, arg: str):
    if event.is_set() is False:
        try:
            event.set()
            idsx = config["userdata"]['workshopid'] 
            idsx.append(arg)
            config["userdata"]['workshopid'] = idsx
            async with aiofiles.open('data/config.json', mode='w') as jsfile:
                await jsfile.write(json.dumps(config, indent=4, sort_keys=True))
            await interaction.response.send_message(f"Added element {arg}")
        except Exception as exc:
            await interaction.response.send_message(f"Error has accured {exc}")
        event.clear()
    else:
        await interaction.response.send_message("Wait until update check finishes!")

@bot.slash_command(name="refill", description="Overwrites the config with the mods in workshop collection. ex, /refill 1332156191")
async def refill(interaction: nextcord.Interaction, arg: int):
    if event.is_set() is False:
        try:
            event.set()
            CollectionToConfig(int(arg))
            await interaction.response.send_message("Cleared and filled config with collection!")
            channel = bot.get_channel(where) 
            await channel.send("Checking for updates!")
            await Monitor()
            await channel.send("Checking finished sleeping...")
            event.clear()  
        except Exception as exc:
            await interaction.response.send_message(f"Error has accured {exc}")
        event.clear()
    else:
        await interaction.response.send_message("Wait until update check finishes!")

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
