import asyncio
import os
import re
from datetime import datetime, timedelta
from typing import List, Optional

import dateutil.parser.isoparser
import discord
from bs4 import BeautifulSoup
from canvasapi import Canvas
from discord.ext import commands
from dotenv import load_dotenv

from canvas_handler import CanvasHandler
from discord_handler import DiscordHandler

bot = commands.Bot(command_prefix='!cd-')

CANVAS_COLOR = 0xe13f2b
CANVAS_THUMBNAIL_URL = "https://lh3.googleusercontent.com/2_M-EEPXb2xTMQSTZpSUefHR3TjgOCsawM3pjVG47jI-BrHoXGhKBpdEHeLElT95060B=s180"

load_dotenv()
CANVAS_API_URL = os.getenv('CANVAS_API_URL')
CANVAS_API_KEY = os.getenv('CANVAS_API_KEY')
DISCORD_KEY = os.getenv('DISCORD_KEY')

d_handler = DiscordHandler()

# TODO: reduce duplication in track_course, untrack_course, get_course_stream by passing func to helper
# TODO: use method to remove guilds without courses, and for invalid track and mode
# TODO: add dm notification option using reaction
# TODO: add options for aliases for courses

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
async def on_command_error(ctx:commands.Context, error:commands.CommandError):
    await ctx.send("```" + str(error) + "```")

@bot.command()
@commands.guild_only()
async def track(ctx:commands.Context, *course_ids:str):
    _add_guild(ctx.message.guild)
    
    c_handler = _get_canvas_handler(ctx.message.guild)
    if not isinstance(c_handler, CanvasHandler):
        return None

    c_handler.track_course(course_ids, ctx.channel)

    embed_var = _get_tracking_courses(c_handler, ctx.message.channel, CANVAS_API_URL)
    await ctx.send(embed=embed_var)

@bot.command()
@commands.guild_only()
async def untrack(ctx:commands.Context, *course_ids:str):
    c_handler = _get_canvas_handler(ctx.message.guild)
    if not isinstance(c_handler, CanvasHandler):
        return None

    c_handler.untrack_course(course_ids, ctx.message.channel)

    embed_var = _get_tracking_courses(c_handler, ctx.message.channel, CANVAS_API_URL)
    await ctx.send(embed=embed_var)

@bot.command()
@commands.guild_only()
async def ass(ctx:commands.Context, *args):
    c_handler = _get_canvas_handler(ctx.message.guild)
    if not isinstance(c_handler, CanvasHandler):
        return None

    if args and args[0].startswith('-till'):
        till = args[1]
        course_ids = args[2:]
    elif args and args[0].startswith('-all'):
        till = None
        course_ids = args[1:]
    else:
        till = "2-week"
        course_ids = args

    
    for data in c_handler.get_assignments(till, course_ids, ctx.message.channel, CANVAS_API_URL):
        embed_var=discord.Embed(title=data[2], url=data[3], description=data[4], color=CANVAS_COLOR)
        embed_var.set_author(name=data[0],url=data[1])
        embed_var.set_thumbnail(url=CANVAS_THUMBNAIL_URL)
        embed_var.add_field(name="Created at", value=data[5], inline=True)
        embed_var.add_field(name="Due at", value=data[6], inline=True)
        await ctx.send(embed=embed_var)

@bot.command()
@commands.guild_only()
async def live(ctx:commands.Context):
    c_handler = _get_canvas_handler(ctx.message.guild)
    if not isinstance(c_handler, CanvasHandler):
        return None
    if ctx.message.channel not in c_handler.live_channels:
        c_handler.live_channels.append(ctx.message.channel)

@bot.command()
@commands.guild_only()
async def unlive(ctx:commands.Context):
    c_handler = _get_canvas_handler(ctx.message.guild)
    if not isinstance(c_handler, CanvasHandler):
        return None
    if ctx.message.channel in c_handler.live_channels:
        c_handler.live_channels.remove(ctx.message.channel)

@bot.command()
@commands.guild_only()
async def info(ctx:commands.Context):
    c_handler = _get_canvas_handler(ctx.message.guild)
    if not isinstance(c_handler, CanvasHandler):
        return None

    await ctx.send(str(c_handler.courses) + "\n" +
                   str(c_handler.guild) + "\n" + 
                   str(c_handler.mode) + "\n" +
                   str(c_handler.channels_courses) + "\n" +
                   str(c_handler.live_channels) + "\n" +
                   str(c_handler.timings) + "\n" +
                   str(c_handler.due_week) + "\n" +
                   str(c_handler.due_day))

@bot.command()
@commands.guild_only()
async def mode(ctx:commands.Context, mode:str):
    _add_guild(ctx.message.guild)

    c_handler = _get_canvas_handler(ctx.message.guild)
    if not isinstance(c_handler, CanvasHandler):
        return None

    if mode in ["guild", "channels"]:
        c_handler.mode = mode
        await ctx.send(mode)
    else:
        await ctx.send("```Invalid mode```")

@bot.command()
@commands.guild_only()
async def stream(ctx:commands.Context, *args):
    c_handler = _get_canvas_handler(ctx.message.guild)
    if not isinstance(c_handler, CanvasHandler):
        return None
    
    if args and args[0].startswith('-till'):
        till = args[1]
        course_ids = args[2:]
    elif args and args[0].startswith('-all'):
        till = None
        course_ids = args[1:]
    else:
        till = "2-week"
        course_ids = args

    for data in c_handler.get_course_stream_ch(till, course_ids, ctx.message.channel, CANVAS_API_URL, CANVAS_API_KEY):
        embed_var=discord.Embed(title=data[2], url=data[3], description=data[4], color=CANVAS_COLOR)
        embed_var.set_author(name=data[0],url=data[1])
        embed_var.set_thumbnail(url=CANVAS_THUMBNAIL_URL)
        embed_var.add_field(name="Created at", value=data[5], inline=True)
        await ctx.send(embed=embed_var)

def _add_guild(guild:discord.Guild):
    if guild not in [ch.guild for ch in d_handler.canvas_handlers]:
        d_handler.canvas_handlers.append(CanvasHandler(CANVAS_API_URL, CANVAS_API_KEY, guild))

def _get_canvas_handler(guild:discord.Guild) -> Optional[CanvasHandler]:
    for ch in d_handler.canvas_handlers:
        if ch.guild == guild:
            return ch
    return None

def _get_tracking_courses(c_handler:CanvasHandler, channel:discord.TextChannel, CANVAS_API_URL) -> discord.Embed:
    course_names = c_handler.get_course_names(channel, CANVAS_API_URL)
    embed_var=discord.Embed(title="Tracking Courses:", color=CANVAS_COLOR)
    embed_var.set_thumbnail(url=CANVAS_THUMBNAIL_URL)
    for c_name in course_names:
        embed_var.add_field(name=c_name[0], value="[Course Page]({})".format(c_name[1]))
    return embed_var

async def live_tracking():
    # WIP
    while True:
        for ch in d_handler.canvas_handlers:
            if len(ch.live_channels) > 0:
                notify_role = None
                for role in ch.guild.roles:
                    if role.name == "notify":
                        notify_role = role
                        break
                if ch.mode == "guild":
                    for c in ch.courses:
                        till = ch.timings[str(c.id)]
                        till = re.sub(r"\s", "-", till)
                        data_list = ch.get_course_stream_ch(till, (str(c.id),), None, CANVAS_API_URL, CANVAS_API_KEY)
                        if notify_role and data_list:
                            for channel in ch.live_channels:
                                await channel.send(notify_role.mention)
                        for data in data_list:
                            embed_var=discord.Embed(title=data[2], url=data[3], description=data[4], color=CANVAS_COLOR)
                            embed_var.set_author(name=data[0],url=data[1])
                            embed_var.set_thumbnail(url=CANVAS_THUMBNAIL_URL)
                            embed_var.add_field(name="Created at", value=data[5], inline=True)
                            for channel in ch.live_channels:
                                await channel.send(embed=embed_var)
                        if data_list:
                            # latest announcement first
                            ch.timings[str(c.id)] = data_list[0][5]
        await asyncio.sleep(3600)

async def assignment_reminder():
    while True:
        for ch in d_handler.canvas_handlers:
            if len(ch.live_channels) > 0:
                notify_role = None
                for role in ch.guild.roles:
                    if role.name == "notify":
                        notify_role = role
                        break
                if ch.mode == "guild":
                    for c in ch.courses:
                        data_list = ch.get_assignments("1-week", (str(c.id),), None, CANVAS_API_URL)
                        recorded_ass_ids = ch.due_week[str(c.id)]
                        ass_ids = await _assignment_sender(ch, data_list, recorded_ass_ids, notify_role)
                        ch.due_week[str(c.id)] = ass_ids

                        data_list = ch.get_assignments("1-day", (str(c.id),), None, CANVAS_API_URL)
                        recorded_ass_ids = ch.due_day[str(c.id)]
                        ass_ids = await _assignment_sender(ch, data_list, recorded_ass_ids, notify_role)
                        ch.due_day[str(c.id)] = ass_ids
        await asyncio.sleep(3600)

async def _assignment_sender(ch:CanvasHandler, data_list:List[str], recorded_ass_ids:List[str], notify_role:Optional[discord.Role]) -> List[str]:
    ass_ids = [data[-1] for data in data_list]
    not_recorded = [data_list[ass_ids.index(i)] for i in ass_ids if i not in recorded_ass_ids]
    if notify_role and not_recorded:
        for channel in ch.live_channels:
            await channel.send(notify_role.mention)
    for data in not_recorded:
        embed_var=discord.Embed(title=data[2], url=data[3], description=data[4], color=CANVAS_COLOR)
        embed_var.set_author(name=data[0],url=data[1])
        embed_var.set_thumbnail(url=CANVAS_THUMBNAIL_URL)
        embed_var.add_field(name="Created at", value=data[5], inline=True)
        embed_var.add_field(name="Due at", value=data[6], inline=True)
        for channel in ch.live_channels:
            await channel.send(embed=embed_var)
    return ass_ids


bot.loop.create_task(live_tracking())
bot.loop.create_task(assignment_reminder())
bot.run(DISCORD_KEY)
