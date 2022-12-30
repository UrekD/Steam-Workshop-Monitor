#Source https://github.com/UrekD/Steam-Workshop-Monitor
import asyncio
from venv import create
from colorama import Fore, Back, Style
import datetime
import httpx
from nextcord.ext import commands
import os
from nextcord import Embed
from nextcord.ext import commands, menus, tasks
import sqlalchemy as sq
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import nextcord
import time
from dotenv import load_dotenv
from datetime import datetime
import pytz
import threading
import asyncio
import psutil
import redis
import warnings
from cooldowns import *
import aiohttp

#Redis multiple set is deprecated... so we need to do this
warnings.filterwarnings("ignore", category=DeprecationWarning) 

#Timezone for logging
timezone = pytz.timezone("Europe/Berlin")

load_dotenv()

RHOST = os.environ.get("RHOST")
RPASS = os.environ.get("RPASS")
RPORT = int(os.environ.get("RPORT"))
RUSER = os.environ.get("RUSER")
RINDEX = os.environ.get("RINDEX")
token = os.environ.get("TOKEN")
DBHOST = os.environ.get("DBHOST")
DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")
DB = os.environ.get("DB")
cdtime = int(os.getenv("cdtime"))
ccount = int(os.getenv("ccount"))
ctime = int(os.getenv("ctime"))
fdelay = int(os.getenv("fdelay"))
chdebug = int(os.getenv("chdebug"))
ttltime = int(os.getenv("ttltime"))
mincount = int(os.getenv("mincount"))

#Servers for admin commands, should really be in .env.., then parse it to a list
servers = [775414312734425098,988801776612409415]
#Global for logging time of monitor
runtime = None
#Connection for reddis and mysql
rpool = redis.BlockingConnectionPool(username= RUSER, password=RPASS,host=RHOST ,decode_responses=True, port=RPORT, db=int(RINDEX), max_connections=10, health_check_interval = 30)
engine = sq.create_engine(f'mysql+mysqlconnector://{DBUSER}:{DBPASS}@{DBHOST}/{DB}', pool_size=10, max_overflow=5, poolclass=QueuePool, pool_pre_ping=True)
#8 means all commands get restricted to administrators, which they can change in discord manually
slashperms=8

#Logging function
async def Log(x,xx):
    now = datetime.now(tz=timezone)
    print(now.strftime(f"{Fore.RED}[{x}]{Fore.MAGENTA} {xx} {Fore.LIGHTGREEN_EX}%H:%M:%S"))
    if True: #Change to False to disable logging to discord
        await err(now.strftime(f"[{x}] {xx} %H:%M:%S"))
    return None

class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # create the background task and run it in the background
        self.bg_task = self.loop.create_task(self.my_background_task())
        
        # Background tasks as made in example
    async def my_background_task(self):
        await self.wait_until_ready()
        while not self.is_closed():
            # Measuring execution time
            global start_clock
            start_clock = int(time.time())
            start_time = time.time()
            monitorstatus = await NewMonitor()
            global runtime
            runtime = time.time() - start_time
            sleeptime = ctime-runtime # calculate how long to sleep, so it runs at interval
            if monitorstatus:
                await Log('MEND',f"{runtime} seconds | <t:{start_clock}:R>")  
                if sleeptime<60: # check to prevent it from running instatly to not overflow the API
                    sleeptime=60
            else: # if monitorstatus is false, it means it failed to run, so we sleep 
                await Log('MEND FAILURE',f"{runtime} seconds | <t:{start_clock}:R>") 
                sleeptime=fdelay
            await asyncio.sleep(sleeptime) 
             
    @tasks.loop(hours=6)
    async def cleanguilds(self):
        guilds = [guild.id for guild in bot.guilds]
        # Clear ghost guilds in DB
        with engine.connect() as con:
            dbguilds = con.execute("SELECT guildid FROM guilds")
            for row in dbguilds:
                if row[0] not in guilds:
                    asyncio.create_task(Log('Guild Delete',f'Guild {row[0]} not found, deleting'))
                    con.execute("DELETE FROM guilds WHERE guildid = %s", row[0])
            # Leave guilds not in DB
            dbguilds = [x[0] for x in con.execute("SELECT guildid FROM guilds").fetchall()]
            for guild in guilds:
                if guild not in dbguilds:
                    asyncio.create_task(Log('Guild Leave',f'Guild {guild} not found, leaving'))
                    await bot.get_guild(guild).leave()
        # Clear mods without any links
        with engine.connect() as con:
            asyncio.create_task(Log('Mod Clear',f'Clearing mods without any links'))
            con.execute("DELETE FROM mods WHERE mods.ModID IN ( SELECT ModID FROM ( SELECT mods.ModID FROM mods LEFT JOIN link ON mods.ModID=link.ModID WHERE link.ModID IS NULL ) as c )")
            # Get Guilds with less than 5 mods
            print(f"SELECT g.GuildID, count(l.GuildID) AS used FROM guilds g left JOIN link l ON g.GuildID=l.GuildID GROUP BY g.GuildID HAVING used < {mincount}")
            l = con.execute(f"SELECT g.GuildID, count(l.GuildID) AS used FROM guilds g left JOIN link l ON g.GuildID=l.GuildID GROUP BY g.GuildID HAVING used < {mincount}").fetchall()
            dbguilds = [x[0] for x in con.execute(f"SELECT g.GuildID, count(l.GuildID) AS used FROM guilds g left JOIN link l ON g.GuildID=l.GuildID GROUP BY g.GuildID HAVING used < {mincount}").fetchall()]
            for x in dbguilds:
                asyncio.create_task(Log('Guild Leave',f'Guild {x} has less than {mincount}, leaving'))
                asyncio.create_task(NotifyServerOwner(bot.get_guild(x),f'Leaving due to monitoring less than {mincount} mods, this is to make space for others as bot is limited to 100 servers only.'))
                await bot.get_guild(x).leave()
        # Flush Redis
        cc.flushall() 

         
    @tasks.loop(minutes=30)
    async def update_stats(self):
        try:
            async with aiohttp.ClientSession() as session:
                url = "https://top.gg/api/bots/752213037079068832/stats"
                guilds = [guild.id for guild in bot.guilds]
                payload={'server_count': len(guilds)}
                headers = { # Fill below with your credentials and uncomment task
                'Authorization': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6Ijc1MjIxMzAzNzA3OTA2ODgzMiIsImJvdCI6dHJ1ZSwiaWF0IjoxNjY1MjcyNzU0fQ.M93Npo9JBWut3d4Bc_BkymL3PWgTqfDUMPUJWghyYrM'
                }
                async with session.post(url, headers=headers, data=payload) as response:
                    await Log('TopGG Count',f'Count: {len(guilds)}, Response: {response.status}')
        except Exception as e:
            await Log('TopGG Er',e)

    # Runs on startup and sets the status
    async def on_ready(self):
        x = "git.urek.eu | /help" # Change to your own status
        await bot.change_presence(activity=nextcord.Game(name=x))
        guilds = [guild.id for guild in bot.guilds]
        print(f"The {bot.user.name} bot is in {len(guilds)} Guilds.\nThe guilds ids list : {guilds}")
        await Log('START','Bot logged in!')
        #self.update_stats.start() # Uncomment to enable TopGG stats
        #self.cleanguilds.start() # Uncomment to enable cleanup task
         
    async def on_guild_join(self,guild):
        await Log('JOIN',guild)
        try:
            a = await GetGuild(guild.id) # Check if guild is in database
            if a is False: # False means DB error, so we try to notify and leave
                await Log('JOIN FAILURE DB',f"{guild.id}")
                await NotifyServerOwner(guild,"DB Error, try again later!")
                await guild.leave()
            else: # Add guild to database, even it it already exists might not be the best thing...
                rl = await guild.create_role(name='workshop')
                overwrites = {
                    guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
                    rl: nextcord.PermissionOverwrite(read_messages=True),
                    guild.me: nextcord.PermissionOverwrite(read_messages=True)
                }
                ch = await guild.create_text_channel('workshop', overwrites=overwrites)
                #await bot.get_channel(993934158877433926).follow(destination=ch) # Follows a channel, change to your own optional
                with get_connection() as (cursor):
                    cursor.execute(f"delete from guilds where GuildID={guild.id}") # Delete guild if it exists just in case
                    cursor.execute("insert into guilds values (%s,%s,%s,%s,100)", (guild.id, guild.name,ch.id,rl.id, ))
                    # Inserting into Redis as well
                    cc.hmset(guild.id,{'GuildName':guild.name,'ChID':ch.id,'RID':rl.id,'Count':100})
                    cc.expire(guild.id, ttltime)
        except Exception as ex: # If something goes wrong, we try to notify and leave
            print(ex.args)
            await Log('JOIN ERR', ex.args)
            await NotifyServerOwner(guild,"An error occured during initilization, bot may not work properly!")
            await guild.leave()

    # Delete all data about the guild when leaving   
    async def on_guild_remove(self,guild):
        try:
            with get_connection() as (cursor):
                data = cursor.execute(f"SELECT ModID FROM link WHERE GuildID={guild.id}").fetchall() # get all the links for this guild
                for x in data: 
                    cc.delete('%s&%s'%(guild.id,x[0]) ) #delete all the links redis
                cursor.execute(f"delete from guilds where GuildID={guild.id}") #delete from guilds
            await DeleteKey(guild.id) #delete key from redis
            await Log('LEAVE',guild)
        except Exception as ex:
            print(ex.args)
            await Log('LEAVE', ex.args) 

# Functions for trying to notify server owner
async def NotifyServerOwner(guild,message):
    try:
        x = guild.system_channel
        if x is not None: 
            await x.send(message) # send the message to the system channel
        else: 
            x = guild.text_channels[0] # if no system channel, send to the first channel
            await x.send(message) # send the message to the first channel
            await x.send("Please set a system channel!") # send the message to the first channel
    except Exception as ex:
        print(ex.args) # print the error
        await Log('NotifyServerOwner', ex.args) 

# Function to check all mods
async def CheckAll(mods):
    try:
        url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
        myobj = {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "itemcount": len(mods),
        }
        # Build the payload with all the mods
        for x in range(len(mods)):
            myobj[f"publishedfileids[{x}]"] = mods[x][0]
        async with httpx.AsyncClient() as r:
            wdetails = await r.post(url, data=myobj)
        return (wdetails.json())
    except Exception as x:
        print(f'Error in CheckAll {x.args}')
        return False

# Servers as a healthcheck for Steam API
async def APICheck():
    try:
        async with httpx.AsyncClient() as r:
            wdetails = await r.get('https://api.steampowered.com/ISteamWebAPIUtil/GetServerInfo/v1/')
        if wdetails.status_code == 200:
            return True
        else:
            return False
    except:
        return False
        
async def Notify(ModData,ModID):
    try: # Try to update redis 1st and seperately
        cc.hset(ModID,'ModUpdated', ModData['time_updated'])
        cc.expire(ModID, ttltime)
    except Exception as ex:
        await Log('Update Redis', ex.args)
    with get_connection() as (cursor): # Update the database then notify
        cursor.execute(f"UPDATE mods SET ModUpdated={ModData['time_updated']} WHERE  ModID={ModID};") 
        # Get channels to notify about the update
        for e in cursor.execute(f"SELECT G.ChID,G.RID FROM link L JOIN guilds G ON G.GuildID=L.GuildID WHERE L.ModID={ModID}").fetchall():
            await Log('NOTIFY',f'{e[0]}')
            channel = bot.get_channel(e[0])
            try: # This try should probbly be earlier but seems to work fine
                await channel.send(
                    f"Mod Updated: <t:{ModData['time_updated']}:R> https://steamcommunity.com/sharedfiles/filedetails/?id={ModID} <@&{e[1]}>"
                )  
            except Exception as ex:
                await Log('FAIL NOTIFY',f'{e[0]}')

# Main fucntion for the background task to Monitor mods
async def NewMonitor():
    await Log('Monitor','Start')
    try:
        if await APICheck(): # Check if Steam API is up
            with get_connection() as (cursor): # Get all the mods to check
                x = cursor.execute("SELECT ModID,ModUpdated FROM mods").fetchall()
                data = await CheckAll(x)
                if data is False: # If the API is down, we just return
                    await Log('Monitor','API Error')
                    return False
                for item in data['response']['publishedfiledetails']:
                    if item is None or item['result']==9: # Check that data is valid, not private or deleted
                        continue
                    # Check if the mod has been updated, by comparing the time_updated
                    if int(item['time_updated']) != int(x[data['response']['publishedfiledetails'].index(item)][1]):
                        # s is the time updated in Unix time
                        s = int(x[data['response']['publishedfiledetails'].index(item)][0])
                        # Run notify non blocking as to not slow down the loop
                        asyncio.create_task(Log('UPDATED',f'{s} updated!') )
                        asyncio.create_task(Notify(item,s)) 
                return True
        else: # If the API is down, we just return
            await Log('Monitor','API Down')
            return False
    except Exception as x:
        await Log('EXCEPTION Monitor', x.args)
        return False

intents = nextcord.Intents(messages=False, guilds=True)
bot = Bot(intents=intents)

# Handeling for MySQL connection
@contextmanager
def get_connection():
    con = engine.connect()
    try:
        yield con
    finally:
        con.close()

# Check a single mod, used in /add 
async def CheckOne(id):
    try:
        url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"
        myobj = {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "itemcount": 1,
            "publishedfileids[0]": [id],
        }
        async with httpx.AsyncClient() as r:
            wdetails = await r.post(url, data=myobj)
        return (wdetails.json()["response"]["publishedfiledetails"][0])
    except Exception as x:
        await Log('EXCEPTION CheckOne',x.args)
        return None

# Class for displaying list of mods of /list
class MyEmbedDescriptionPageSource(menus.ListPageSource):
    def __init__(self, data):
        super().__init__(data, per_page=25)

    async def format_page(self, menu, entries):
        embed = Embed(title="Mods", description="\n".join(entries))
        embed.set_footer(text=f"Page {menu.current_page + 1}/{self.get_max_pages()}")
        return embed

# For handeling rate limits of slash commands
@bot.event
async def on_application_command_error(inter: nextcord.Interaction, error):
    error = getattr(error, "original", error)

    if isinstance(error, CallableOnCooldown):
        await inter.send(
            f"You are being rate-limited! Retry in `{error.retry_after}` seconds."
        )

    else:
        await Log('EXCEPTION CMD',error.args)

@bot.slash_command(name="whelp", description="help", default_member_permissions=slashperms)
@cooldown(ccount, cdtime, bucket=SlashBucket.guild)
@cooldown(2, cdtime, bucket=CooldownBucket.kwargs)
async def help(interaction: nextcord.Interaction):
    embed = nextcord.Embed(
        title="Steam-Workshop-Monitor Help",
        url="https://discord.gg/tSZmkdXnYv", # Change this to your discord server
        color=0xFF0000,
    )
    embed.set_author(
        name="Steam-Workshop-Monitor Help",
        url="https://discord.gg/tSZmkdXnYv", # Change this to your discord server
        icon_url="https://icons.iconarchive.com/icons/icons8/windows-8/512/Logos-Steam-icon.png",
    )
    embed.set_thumbnail(
        url="https://icons.iconarchive.com/icons/icons8/windows-8/512/Logos-Steam-icon.png"
    )
    embed.add_field(name="/add", value="Add Workshop item by ID", inline=False)
    embed.add_field(name="/remove", value="Add Workshop item by ID", inline=False)
    embed.add_field(name="/list", value="List all items monitored by this guild", inline=False)
    embed.add_field(name="/time", value="Get time of last check loop", inline=False)
    embed.add_field(name="/info", value="Get remaining mod quota for this guild", inline=False)
    embed.add_field(name="/help", value="Get this help", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.slash_command(name="winfo", description="Get remaining mod quota for this guild", default_member_permissions=slashperms)
@cooldown(ccount, cdtime, bucket=SlashBucket.guild)
@cooldown(2, cdtime, bucket=CooldownBucket.kwargs)
async def xinfo(interaction: nextcord.Interaction):
    await interaction.response.defer()
    try:
        guilddata = await GetGuild(interaction.guild_id)
        if guilddata is False:
            await interaction.followup.send("DB seems down :(")
        elif guilddata is not None:
            await interaction.followup.send(f"Available Mods to monitor: {guilddata['Count']}\n Role: <@&{guilddata['RID']}>\n Channel: <#{guilddata['ChID']}>")
        else:
            await interaction.followup.send("Guild is not in DB! Kick and invite again!")
    except Exception as x:
        await interaction.followup.send(f"Error has accured :(")
        await Log('EXCEPTION xinfo',x.args)
        return

@bot.slash_command(name="wtime", description="Get time of last check loop", default_member_permissions=slashperms)
@cooldown(ccount, cdtime, bucket=SlashBucket.guild)
@cooldown(2, cdtime, bucket=CooldownBucket.kwargs)
async def ttime(interaction: nextcord.Interaction):
    if runtime is None:
        await interaction.response.send_message("Monitor has not run yet!")
    else:
        await interaction.response.send_message(f"{round(runtime,2)} seconds | <t:{start_clock}:R>")
    
# Force fill all data from MySQL to Redis
@bot.slash_command(name="wafill", description="MYSQL TO REDIS", default_member_permissions=slashperms, guild_ids = servers)
async def rfill(interaction: nextcord.Interaction):
    await interaction.response.defer()
    await FillRedis()
    await interaction.followup.send("Done!", ephemeral=True)

# Admin command for increasing mod quota
@bot.slash_command(name="wacount", description="Increase guild quota", default_member_permissions=slashperms, guild_ids = servers)
async def acount(interaction: nextcord.Interaction, srvr: str, arg: str):
    await interaction.response.defer()
    try:
        with get_connection() as (cursor):
            cursor.execute(f"UPDATE guilds SET Count={int(arg)} WHERE  GuildID={int(srvr)}")
        await DeleteKey(srvr) #delete key from redis
    except Exception as x:
        await interaction.followup.send("Error has accured :(")
        await Log('EXCEPTION acount',x.args)
        return
    await interaction.followup.send("Done!")

# Admin command for setting channel ID for guild manually
@bot.slash_command(name="wach", description="Set Channel", default_member_permissions=slashperms, guild_ids = servers)
async def ach(interaction: nextcord.Interaction, srvr: str, arg: str):
    await interaction.response.defer()
    try:
        with get_connection() as (cursor):
            cursor.execute(f"UPDATE guilds SET ChID={int(arg)} WHERE  GuildID={int(srvr)}")
        await DeleteKey(srvr) #delete key from redis
    except Exception as x:
        await interaction.followup.send("Error has accured :(")
        await Log('EXCEPTION ach',x.args)
        return
    await interaction.followup.send("Done!")

# Admin command for setting role ID for guild manually
@bot.slash_command(name="warole", description="Set Role", default_member_permissions=slashperms, guild_ids = servers)
async def arole(interaction: nextcord.Interaction, srvr: str, arg: str):
    await interaction.response.defer()
    try:
        with get_connection() as (cursor):
            cursor.execute(f"UPDATE guilds SET RID={int(arg)} WHERE  GuildID={int(srvr)}")
        await DeleteKey(srvr) #delete key from redis
    except Exception as x:
        await interaction.followup.send("Error has accured :(")
        await Log('EXCEPTION arole',x.args)
        return
    await interaction.followup.send("Done!")

# Admin command for getting quota for guild by ID
@bot.slash_command(name="wainfo", description="Get remaining mod quota for this guild", default_member_permissions=slashperms, guild_ids = servers)
async def ainfo(interaction: nextcord.Interaction, arg: str):
    await interaction.response.defer()
    try:
        guilddata = await GetGuild(int(arg))
        if guilddata is False:
            await interaction.followup.send("DB seems down :(")
        elif guilddata is not None:
            await interaction.followup.send(f"Available Mods to monitor: {guilddata['Count']}\n Role: <@&{guilddata['RID']}>\n Channel: <#{guilddata['ChID']}>")
        else:
            await interaction.followup.send("Guild is not in DB! Kick and invite again!")
    except Exception as x:
        await interaction.followup.send(f"Error has accured :(")
        await Log('EXCEPTION xinfo',x.args)
        return

# Debug cmd to get hosts usage CPU and RAM
@bot.slash_command(name="wthreadds", description="Monitor time and when it last ran", default_member_permissions=slashperms, guild_ids = servers)
@cooldown(ccount, cdtime, bucket=SlashBucket.guild)
@cooldown(2, cdtime, bucket=CooldownBucket.kwargs)
async def threadds(interaction: nextcord.Interaction):
    await interaction.response.defer()
    th = []
    for thread in threading.enumerate(): 
        th.append(thread.name)
    await interaction.followup.send((th,'RAM memory % used:', psutil.virtual_memory()[2],' The CPU usage is: ', psutil.cpu_percent(4)))

@bot.slash_command(name="wlist", description="Lists all mods monitored by this Guild!", default_member_permissions=slashperms)#, guild_ids = servers)
@cooldown(ccount, cdtime, bucket=SlashBucket.guild)
@cooldown(2, cdtime, bucket=CooldownBucket.kwargs)
async def listx(interaction: nextcord.Interaction):
        await interaction.response.defer()
        try:
            with get_connection() as (cursor):
                data = cursor.execute(f"SELECT m.ModID,m.ModName FROM mods m JOIN link l ON l.ModID=m.ModID WHERE l.GuildID= {interaction.guild.id}").fetchall()
            leng=len(data) # Get number of mods
            t = 30
            if leng > 75: # If more than 75 mods, increase timeout for embed
                t = t * (leng / 50)
            data = [("#%s [%s](https://steamcommunity.com/workshop/filedetails/?id=%s) | %s" % (num,data[num][1],data[num][0],data[num][0])) for num in range(0, leng)]
            pages = menus.ButtonMenuPages(
                source=MyEmbedDescriptionPageSource(data),
                clear_buttons_after=True,
                timeout=t, # Timeout for embed, idk if needed but just in case
            )
            await pages.start(interaction=interaction)
        except Exception as ex:
            print(ex.args)
            await interaction.followup.send("Error")

@bot.slash_command(
    name="wadd",
    description="Add a Steam Workshop Item by it's ID!", default_member_permissions=slashperms)
@cooldown(ccount, cdtime, bucket=SlashBucket.guild)
@cooldown(2, cdtime, bucket=CooldownBucket.kwargs)
async def add(interaction: nextcord.Interaction, arg: int):
    await interaction.response.defer() # Defer response to avoid timeout
    await Log('Add',f'{interaction.guild.id} {arg}')
    x = await CheckOne(arg) # Get item data from Steam API
    if x['result']!=9 and x!=None: # Check that it does not returs 9 (item not found) and not None
        try:
            with get_connection() as (cursor):
                count = await GetGuildCount(interaction.guild.id) # Get quota remaining for this guild
                if count is None: 
                    await interaction.followup.send("Guild is not in DB! Kick and invite again!")
                    return
                if int(count)<1:
                    await interaction.followup.send("Mod limit reached, remove some mods!")
                    return
                a = await GetModUpdated(arg) # Try to get mod from DB to see if it in DB already
                if a == None: # If not in DB, add it
                    cursor.execute("insert into mods values (%s,%s,%s)", (arg,x['title'],x['time_updated'], ))
                    cc.hmset(arg, {'ModName':x['title'],'ModUpdated': x['time_updated']})
                    cc.expire(arg, ttltime)
                a = await GetLinkUpdated('%s&%s'%(interaction.guild.id,arg)) # Check that this guild isn't already monitoring this mod
                if a == None: # If not, add it
                    cursor.execute(f"insert into link values ({interaction.guild.id},{arg})") # Add mod to guild
                    cursor.execute(f"UPDATE guilds SET Count=COUNT-1 WHERE  GuildID={interaction.guild.id}") # Should really use a trigger or a procedure...
                    cc.hincrby(interaction.guild.id,'Count', -1) # Update redis
                    tn = '%s&%s'%(interaction.guild.id,arg)
                    cc.hset(tn,'n', '0')
                    cc.expire(tn, ttltime)
                    await interaction.followup.send(f"{arg} added!")
                else:
                    await interaction.followup.send(f"{arg} already added!")
        except Exception as x:
            print(x.args)
            await interaction.followup.send("Database not responding!")
    else:
        await interaction.followup.send(f"{arg} doesn't exist!")

@bot.slash_command(
    name="wremove",
    description="Remove a Steam Workshop Item by it's ID!", default_member_permissions=slashperms#,guild_ids = servers
)
@cooldown(ccount, cdtime, bucket=SlashBucket.guild)
@cooldown(2, cdtime, bucket=CooldownBucket.kwargs)
async def remove(interaction: nextcord.Interaction, arg: int):
    await interaction.response.defer() # Defer response to avoid timeout
    await Log('Remove',f'{arg} {interaction.guild.id}')
    try:
        with get_connection() as (cursor):
            a = await GetLinkUpdated('%s&%s'%(interaction.guild.id,arg)) # Check that this guild is monitoring this mod
            if a != None: # If it is, remove it
                try:
                    cursor.execute(f"delete from link where ModID={arg} and GuildID={interaction.guild.id}") # Remove mod from guild
                    await GetGuildCount(interaction.guild.id) # Get guild count 
                    cursor.execute(f"UPDATE guilds SET Count=COUNT+1 WHERE  GuildID={interaction.guild.id}") # Should really use a trigger or a procedure...
                    cc.hincrby(interaction.guild.id,'Count', 1) # Update redis
                    await DeleteKey('%s&%s'%(interaction.guild.id,arg)) # Delete redis key for this mod
                    await interaction.followup.send(f"{arg} removed!")
                except Exception as x:
                    print(x.args)
                    await interaction.followup.send(f"Error removing {arg}") 
            else:
                await interaction.followup.send(f"Not monitoring {arg}!")                 
    except Exception as x:
        print(x.args)
        await interaction.followup.send("Database not responding!")

# Method for parsing a whole steam collection
# Never implemented, but basics of getting the data from the API should be fully working
async def CollectionToConfig(arg):
    try:
        body = "publishedfileids[0]"
        url = (
            "https://api.steampowered.com/ISteamRemoteStorage/GetCollectionDetails/v1/"
        )
        myobj = {
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
            "collectioncount": 1,
            body: arg,
        }
        collection = httpx.post(url, data=myobj)
        ids=[]
        modss = collection.json()["response"]["collectiondetails"][0]["children"]
        for item in modss:
            temp = item["publishedfileid"]
            x = await CheckOne(temp)
            with get_connection() as (cursor):
                #a = cursor.execute(f"select * from mods where ModID={temp}").fetchone()
                a = await GetModUpdated(arg)
                if a == None:
                    cursor.execute(f"insert into mods values ({temp},'{x['title']}',{x['time_updated']})")
                try:
                    cursor.execute(f"insert into link values (775414312734425098,{temp})")
                except Exception as exc:
                    await Log("ERROR",f"Collection was not parsed correctly try again! {exc}")
    except Exception as exc:
        await Log("ERROR",f"Collection was not parsed correctly try again! {exc}")

# Used for sending a message to the debug channel on Discord
# Used in method Log
async def err(x):
    try:
        a = bot.get_channel(chdebug)
        await a.send(x)
    except:
        print(x)
        print("Error sending to channel!")

cc = redis.Redis(connection_pool=rpool, retry_on_timeout=True)


# Get Guild count from Redis if not in Redis, get it from DB and add it to Redis
async def GetGuildCount(arg):
    try:
        a = cc.hget(arg,'Count')
        if a == None:
                a = await GetGuild(arg)
                if a is False:
                    return a
                if a != None:
                    return a[3]
                else:
                    return None
        else:
            return a
    except Exception as exc:
        await Log("ERROR",f"Error getting count {exc}")
        return False

# Get Mod update time from Redis if not in Redis, get it from DB and add it to Redis
async def GetModUpdated(xkey):
    try:
        value = cc.hget(xkey,"ModUpdated")
        if value is None:
            with get_connection() as (cursor):
                value = cursor.execute(f"select ModUpdated from mods where ModID={xkey}").fetchone()
                if value is not None:
                    cc.hset(xkey,'ModUpdated', value[0])
                    cc.expire(xkey, ttltime)
                    return value
                else:
                    return None
        else:
            return value
    except Exception as exc:
        await err(f"Error getting value from redis! {exc}")
        return None

# Get Guild from Redis if not in Redis, get it from DB and add it to Redis
async def GetGuild(arg):
    try:
        a = cc.hgetall(arg)
        if a == {}:
            with get_connection() as (cursor):
                a = cursor.execute(f"select GuildName,ChID,RID,Count from guilds where GuildID={arg}").fetchone()
                if a != None:
                    cc.hmset(arg,a)
                    cc.expire(arg, ttltime)
                    return a
                else:
                    return None
        else:
            return a
    except Exception as exc:
        await Log("ERROR",f"Error getting guild {exc}")
        return False

#Get all guilds from db and add to redis
async def GuildsToRedis():
    try:
        with get_connection() as (cursor):
            a = cursor.execute("select * from guilds").fetchall()
            for item in a:
                cc.hmset(item[0], {'GuildName':item[1],'ChID': item[2],'RID': item[3],'Count': item[4]})
                cc.expire(item[0], ttltime)
    except Exception as exc:
        await err(f"Error getting guilds from db! {exc}")
        return None

#Get all mods from db and add to redis 
async def ModsToRedis():
    try:
        with get_connection() as (cursor):
            a = cursor.execute("select * from mods").fetchall()
            for item in a:
                cc.hmset(item[0], {'ModName':item[1],'ModUpdated': item[2]})
                cc.expire(item[0], ttltime)
    except Exception as exc:
        await err(f"Error getting mods from db! {exc}")
        return None

#Get all links from db and add to redis
async def LinksToRedis():
    try:
        with get_connection() as (cursor):
            a = cursor.execute("select * from link").fetchall()
            for item in a:
                item = '%s&%s'%(item[0],item[1])
                cc.hset(item,'n',0)
                cc.expire(item, ttltime)
    except Exception as exc:
        await err(f"Error getting links from db! {exc}")
        return None

# Get Mod update time from Redis if not in Redis, get it from DB and add it to Redis
async def GetLinkUpdated(xkey):
    try:
        value = cc.hget(xkey,"n")
        if value is None:
            with get_connection() as (cursor):
                split = xkey.split('&') # Split the key to get the guild id and mod id
                value = cursor.execute(f"select * from link where GuildID={split[0]} and ModID={split[1]}").fetchone()
                if value is not None:
                    cc.hset(xkey,'n', 0)
                    cc.expire(xkey, ttltime)
                    return value
                else:
                    return None
        else:
            return value
    except Exception as exc:
        await err(f"Error getting value from redis! {exc}")
        return None

#Delete key from redis
async def DeleteKey(arg):
    try:
        cc.delete(arg)
    except Exception as exc:
        await err(f"Error deleting key from redis! {exc}")
        return None

async def FillRedis():
    #cc.flushall()
    await GuildsToRedis()
    await ModsToRedis()
    await LinksToRedis()
    await Log("INFO","Redis filled!")

# Checking SQL connection encryption
def CheckEncryption():
    with get_connection() as (cursor):
        a = cursor.execute("SHOW SESSION STATUS LIKE \'Ssl_cipher\';")
    print(a.fetchone())

#CheckEncryption()
cc.flushall() # Flush redis to prevent any old or debug data
bot.run(token)