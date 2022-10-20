from math import fabs
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
from sqlalchemy.pool import QueuePool
import sqlalchemy as sq
from dotenv import load_dotenv
from contextlib import contextmanager
import re

load_dotenv()

today = datetime.date.today()
x=(today.strftime("%d/%m/%Y")) 

#It would be smart to alto init location as .env var but task scheculer is a pain and dosen't like relative paths

DBHOST = os.environ.get("DBHOST")
DBUSER = os.environ.get("DBUSER")
DBPASS = os.environ.get("DBPASS")
DB = os.environ.get("DB")
from sqlalchemy.pool import QueuePool
import sqlalchemy as sq
engine = sq.create_engine(f'mysql+mysqlconnector://{DBUSER}:{DBPASS}@{DBHOST}/{DB}', pool_size=10, max_overflow=5, poolclass=QueuePool, pool_pre_ping=True)

@contextmanager
def get_connection():
    con = engine.connect()
    try:
        yield con
    finally:
        con.close()

with get_connection() as (cursor):
    g,m,l = cursor.execute(f"SELECT COUNT(*) FROM guilds UNION SELECT COUNT(*) FROM mods UNION SELECT COUNT(*) FROM link").fetchall()

def test(): #Generates PNG not great
    image = Image.new('RGB', (240, 120), color = (20,19,33))
    fontsize = 14  # starting font size
    font = ImageFont.truetype("verdana.ttf", fontsize)
    text1 = f"Workshop Monitor {x}\nServers/Guilds count: {g[0]} \nUnique items monitored: {m[0]} \nTotal monitored: {l[0]} \nAverage total check time: 3s"
    draw = ImageDraw.Draw(image) 
    spacing = 5
    
    draw.text((6, 8), text1, fill =(200,61,114), font = font, 
            spacing = spacing, align ="left")

    image.save('D:\\GitHub\\UrekD\\stats.png')

def git_push():
    from git import Repo
    PATH_OF_GIT_REPO = r'D:\\System\\Documents\\MEGAsync\\GitHub\\UrekD\\.git'  # make sure .git folder is properly configured
    COMMIT_MESSAGE = 'Updating stats'
    repo = Repo(PATH_OF_GIT_REPO)
    if repo.active_branch.name != 'wbstats':
        print("Not on wbstats branch, aborting")
        return
    gen()
    repo.git.add(update=True)
    repo.git.add(r'overview.svg')
    repo.index.commit(COMMIT_MESSAGE)
    origin = repo.remote(name='origin')
    origin.push()   

def gen():
    """
    Generate an SVG badge with summary statistics
    :param s: Represents user's GitHub statistics
    """
    
    with open("D:\\GitHub\\WorkshopMonitor\\stats\\templates\\overview.svg", "r") as f:
        output = f.read()

    output = re.sub("{{ name }}", x, output)
    output = re.sub("{{ stars }}", f"{g[0]}", output)
    output = re.sub("{{ forks }}", f"{m[0]}", output)
    output = re.sub("{{ contributions }}", f"{l[0]}", output)
    output = re.sub("{{ lines_changed }}", "2s", output)

    with open("D:\\GitHub\\UrekD\\overview.svg", "w") as f:
        f.write(output)

if __name__ == '__main__':
    print('Starting...')
    git_push()
    print('Done!')