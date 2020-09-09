import discord
import asyncio
import os
import dateutil.parser.isoparser
from canvas_handler import CanvasHandler
from discord_handler import DiscordHandler
from canvasapi import Canvas
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from discord.ext import commands

bot = commands.Bot(command_prefix='!cd-')

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
# TODO: make documentation
# TODO: add options for aliases for courses
# TODO: add dm notification option using reaction
# TODO: use dicts for channels_courses in canvas_handler
# TODO: add guild in seperate func and not through track

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

@bot.command()
async def track(ctx, *course_ids):
    if ctx.message.guild not in d_handler.guilds:
        d_handler.guilds.append(ctx.message.guild)
        d_handler.canvas_handlers.append(CanvasHandler(CANVAS_API_URL, CANVAS_API_KEY, ctx.message.guild))
    
    c_handler = d_handler.canvas_handlers[d_handler.guilds.index(ctx.message.guild)]
    c_handler.track_course(course_ids, ctx.channel)

    course_names_str = c_handler.get_course_names(ctx.message.channel)

    await ctx.send("Tracking: " + course_names_str)

@bot.command()
async def untrack(ctx, *course_ids):
    c_handler = d_handler.canvas_handlers[d_handler.guilds.index(ctx.message.guild)]
    c_handler.untrack_course(course_ids, ctx.message.channel)

    course_names_str = c_handler.get_course_names(ctx.message.channel)

    await ctx.send("Tracking: " + course_names_str)

@bot.command()
async def ass(ctx, *course_ids):
    c_handler = d_handler.canvas_handlers[d_handler.guilds.index(ctx.message.guild)]

    for data in c_handler.get_assignments(course_ids, ctx.message.channel):
        embed_var=discord.Embed(title=data[0], url=data[1], description=data[2], color=CANVAS_COLOR)
        embed_var.set_thumbnail(url=CANVAS_THUMBNAIL_URL)
        embed_var.add_field(name="Created at", value=data[3], inline=True)
        embed_var.add_field(name="Due at", value=data[4], inline=True)
        await ctx.send(embed=embed_var)

@bot.command()
async def live(ctx):
    c_handler = d_handler.canvas_handlers[d_handler.guilds.index(ctx.message.guild)]
    c_handler.live_channels.append(ctx.message.channel)

@bot.command()
async def mode(ctx, mode):
    c_handler = d_handler.canvas_handlers[d_handler.guilds.index(ctx.message.guild)]
    c_handler.mode = mode

def _remove_empty_strings(ids):
    return [i for i in ids if i != '']
    

async def live_tracking():
    # WIP
    while True:
        for ch in d_handler.canvas_handlers:
            if len(ch.live_channels) > 0:
                for channel in ch.live_channels:
                    await channel.send("Update")
        await asyncio.sleep(10)

bot.loop.create_task(live_tracking())
bot.run(DISCORD_KEY)