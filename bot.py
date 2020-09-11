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
# TODO: store information to resume after stopping
# TODO: use above method to remove guilds without courses
# TODO: order assignments by date?
# TODO: add dm notification option using reaction
# TODO: make unlive
# TODO: add options for aliases for courses
# TODO: make documentation

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="I, Robot"))

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send("```" + str(error) + "```")

@bot.command()
@commands.guild_only()
async def track(ctx, *course_ids):
    _add_guild(ctx.message.guild)
    
    c_handler = _get_canvas_handler(ctx.message.guild)
    c_handler.track_course(course_ids, ctx.channel)

    course_names_str = c_handler.get_course_names(ctx.message.channel)

    await ctx.send("Tracking: " + course_names_str)

@bot.command()
@commands.guild_only()
async def untrack(ctx, *course_ids):
    c_handler = _get_canvas_handler(ctx.message.guild)
    c_handler.untrack_course(course_ids, ctx.message.channel)

    course_names_str = c_handler.get_course_names(ctx.message.channel)

    await ctx.send("Tracking: " + course_names_str)

@bot.command()
@commands.guild_only()
async def ass(ctx, *args):
    c_handler = _get_canvas_handler(ctx.message.guild)

    if args and args[0].startswith('-till'):
        till = args[1]
        course_ids = args[2:]
    else:
        till = None
        course_ids = args
    
    for data in c_handler.get_assignments(till, course_ids, ctx.message.channel):
        embed_var=discord.Embed(title=data[0], url=data[1], description=data[2], color=CANVAS_COLOR)
        embed_var.set_thumbnail(url=CANVAS_THUMBNAIL_URL)
        embed_var.add_field(name="Created at", value=data[3], inline=True)
        embed_var.add_field(name="Due at", value=data[4], inline=True)
        await ctx.send(embed=embed_var)

@bot.command()
@commands.guild_only()
async def live(ctx):
    c_handler = _get_canvas_handler(ctx.message.guild)
    c_handler.live_channels.append(ctx.message.channel)

@bot.command()
@commands.guild_only()
async def mode(ctx, mode):
    _add_guild(ctx.message.guild)

    c_handler = _get_canvas_handler(ctx.message.guild)
    c_handler.mode = mode

@bot.command()
async def stream(ctx, arg):
    c_handler = _get_canvas_handler(ctx.message.guild)
    for item in c_handler.get_course_stream_ch(arg, CANVAS_API_URL, CANVAS_API_KEY):
        await ctx.send(item)
        await ctx.send("next item below")

@bot.command()
async def stream_sum(ctx, arg):
    c_handler = _get_canvas_handler(ctx.message.guild)
    await ctx.send(c_handler.get_course_stream_summary_ch(arg, CANVAS_API_URL, CANVAS_API_KEY))

def _remove_empty_strings(ids):
    return [i for i in ids if i != '']

def _add_guild(guild):
    if guild not in d_handler.guilds:
        d_handler.guilds.append(guild)
        d_handler.canvas_handlers.append([guild, CanvasHandler(CANVAS_API_URL, CANVAS_API_KEY, guild)])
    

def _get_canvas_handler(guild):
    for guild_canvas_handler in d_handler.canvas_handlers:
        if guild_canvas_handler[0] == guild:
            return guild_canvas_handler[1]

async def live_tracking():
    # WIP
    while True:
        for ch in d_handler.canvas_handlers:
            if len(ch[1].live_channels) > 0:
                for channel in ch[1].live_channels:
                    await channel.send("Update")
        await asyncio.sleep(10)

bot.loop.create_task(live_tracking())
bot.run(DISCORD_KEY)