# bot.py
from ast import alias
from email import message
import os
import random
from bs4 import MarkupResemblesLocatorWarning
import discord
from dotenv import load_dotenv
import pyperclip
import json
import d20
import argparse

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='@')

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(dest="command", help="Commands")

parser_start = subparsers.add_parser("start", aliases=["s"], help="Start an encounter")
parser_start.add_argument("channelName", type=str, help="Channel name to display encounter to players")

parser_join = subparsers.add_parser("join", aliases=["j"], help="Join a PC to an encounter")
parser_join.add_argument("name", type=str, help="Name")
parser_join.add_argument("initiative", type=int, help="Initiative")



encounter = {
    "members": [],
    "round": 0,
    "currentTurn": None,
    "running": False,
    "channel": None
}


def initialize(channelName):
    encounter["members"] = []
    encounter["round"] = 0
    encounter["currentTurn"] = None
    encounter["running"] = True
    encounter["channel"] =  discord.utils.get(bot.get_all_channels(), name  = channelName)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name="e")
async def dispatchCommand(ctx, *a):
    try:
        args = parser.parse_args(a)
    except:
        await ctx.send(parser_start.format_help())
        return

    match args.command:
        case "start" | "s":
            await start(ctx, args)
        case "join" | "j":
            await join(ctx, args)
        case _:
            await ctx.send(parser.format_help())

async def start(ctx, args):
    if encounter["running"]:
        await ctx.send('Combat alreay running.  Use "end" to stop.')
        return

    initialize(args.channelName)
    await ctx.send(f'Combat ready')
    await encounter["channel"].send(f"Please join using command:\n `@e j [name] [initative]`")

async def join(ctx, args):
    if encounter["running"] == False:
        await ctx.send('Combat is not running.  Please wait for the DM')
        return

    encounter["members"].append({
        "name": args.name,
        "initiative": args.initiative
    })
    await ctx.send(f"{args.name} added to encounter with initative {args.initiative}")


@bot.command(name ='a')
async def add(ctx, qty: int, name: str, hp: int, ac: int, init: str):
    round = round + 1
    if init == None:
        init = '+0'

    for x in range(1, qty + 1):
        if qty > 1:
            adjName = f'{name}{x}'
        else:
            adjName = name

        encounter.members.append({
            "init": init,
            "name": adjName,
            "hp": hp,
            "ac": ac
        })
            
    await ctx.message.author.send(f'Add complete {encounter}')
    await ctx.send(f'Add complete {encounter}')


bot.run(TOKEN)