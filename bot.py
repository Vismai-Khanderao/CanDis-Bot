import discord
import asyncio
import os
import dateutil.parser.isoparser
from canvas_handler import CanvasHandler
from discord_handler import DiscordHandler
from canvasapi import Canvas
from bs4 import BeautifulSoup
from dotenv import load_dotenv

client = discord.Client()

CANVAS_COLOR = 0xe13f2b
CANVAS_THUMBNAIL_URL = "https://lh3.googleusercontent.com/2_M-EEPXb2xTMQSTZpSUefHR3TjgOCsawM3pjVG47jI-BrHoXGhKBpdEHeLElT95060B=s180"

load_dotenv()
CANVAS_API_URL = os.getenv('CANVAS_API_URL')
CANVAS_API_KEY = os.getenv('CANVAS_API_KEY')
DISCORD_KEY = os.getenv('DISCORD_KEY')

d_handler = DiscordHandler()

# TODO: make live assignment reminder/new announcement feature
# TODO: make send assignments due in n time from now
# TODO: make unlive
# TODO: change timezone from gmt to pst
# TODO: change client to bot
# TODO: make documentation
# TODO: add options for aliases for courses
# TODO: add dm notification option using reaction
# TODO: use dicts for channels_courses in canvas_handler

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('!cd track'):
        if message.guild not in d_handler.guilds:
            d_handler.guilds.append(message.guild)
            d_handler.canvas_handlers.append(CanvasHandler(CANVAS_API_URL, CANVAS_API_KEY, message.guild))
        
        c_handler = d_handler.canvas_handlers[d_handler.guilds.index(message.guild)]
        c_handler.track_course(message.content.split(" ")[2:], message.channel)

        course_names_str = c_handler.get_course_names(message.channel)

        await message.channel.send("Tracking: " + course_names_str)
    
    if message.content.startswith('!cd untrack'):
        c_handler = d_handler.canvas_handlers[d_handler.guilds.index(message.guild)]
        c_handler.untrack_course(message.content.split(" ")[2:], message.channel)

        course_names_str = c_handler.get_course_names(message.channel)

        await message.channel.send("Tracking: " + course_names_str)

    if message.content.startswith('!cd ass'):
        if len(message.content.split(" ")[2:]) == 0:
            course_ids = None
        else:
            course_ids = message.content.split(" ")[2:]

        c_handler = d_handler.canvas_handlers[d_handler.guilds.index(message.guild)]

        for data in c_handler.get_assignments(course_ids, message.channel):
            embed_var=discord.Embed(title=data[0], url=data[1], description=data[2], color=CANVAS_COLOR)
            embed_var.set_thumbnail(url=CANVAS_THUMBNAIL_URL)
            embed_var.add_field(name="Created at", value=data[3], inline=True)
            embed_var.add_field(name="Due at", value=data[4], inline=True)
            await message.channel.send(embed=embed_var)
    
    if message.content.startswith('!cd live'):
        c_handler = d_handler.canvas_handlers[d_handler.guilds.index(message.guild)]
        c_handler.live_channels.append(message.channel)
    
    if message.content.startswith('!cd mode'):
        c_handler = d_handler.canvas_handlers[d_handler.guilds.index(message.guild)]
        c_handler.mode = message.content.split(" ")[2]

    # for testing only
    if message.content.startswith('!cd info'):
        assigned_guilds = []
        for ch in d_handler.canvas_handlers:
            assigned_guilds.append(ch.guild.name)
        
        d_handler_guilds = []
        for guild in d_handler.guilds:
            d_handler_guilds.append(guild.name)

        await message.channel.send(", ".join(assigned_guilds) + "\n" + ", ".join(d_handler_guilds))

async def live_tracking():
    # WIP
    while True:
        for ch in d_handler.canvas_handlers:
            if len(ch.live_channels) > 0:
                for channel in ch.live_channels:
                    await channel.send("Update")
        await asyncio.sleep(10)

client.loop.create_task(live_tracking())
client.run(DISCORD_KEY)