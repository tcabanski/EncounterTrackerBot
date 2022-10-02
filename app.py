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

parser_display = subparsers.add_parser("print", aliases=["p"], help="Print an encounter")

encounter = {
    "members": [],
    "round": -1,
    "turn": -1,
    "running": False,
    "channel": None
}

def initialize(ctx, channelName):
    encounter["members"] = []
    encounter["round"] = -1
    encounter["turn"] = -1
    encounter["running"] = True
    encounter["channel"] =  discord.utils.get(bot.get_all_channels(), name  = channelName)
    encounter["owner"] = ctx.author

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
        case "print" | "p":
            await printCommand(ctx, args)
        case _:
            await ctx.send(parser.format_help())

async def start(ctx, args):
    if encounter["running"]:
        await ctx.send('Combat alreay running.  Use "end" to stop.')
        return

    initialize(ctx, args.channelName)
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

    encounter["members"].sort(reverse=True, key=lambda e: e["initiative"])

    await ctx.send(f"{args.name} added to encounter with initative {args.initiative}")

async def printCommand(ctx, args):
    if encounter["running"] == False:
        await ctx.send('Combat is not running.  Please wait for the DM')
        return

    if ctx.author.id != encounter["owner"].id:
        await ctx.send('Only the DM can use this command')
        return

    text = "========================="
    if encounter["round"] < 0:
       text = text + f"\nEncounter round: NONE" 
    else:
        text = text + f"\nEncounter round: {encounter['round']}"
    
    members = encounter["members"]
    turn = encounter["turn"]
    
    if len(members) == 0:
        text = text + "\nNo creatures or PCs in encounter"
    else:
        for x in range(0, len(encounter["members"])):
            member = members[x - 1]
            if x == turn:
                text = text + f"\n**{x}: {member['name']}**"
            else:
                text = text + f"\n{x}: {member['name']}"

    await encounter["channel"].send(text)

    #embed = discord.Embed(description="This text should be red", color=discord.Color.red())
    #await encounter["channel"].send(embed=embed)


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

        encounter["members"].append({
            "init": init,
            "name": adjName,
            "hp": hp,
            "ac": ac
        })

    encounter.members.sort(reverse=True, key=lambda e: e["initiative"])
            
    await ctx.message.author.send(f'Add complete {encounter}')
    await ctx.send(f'Add complete {encounter}')

bot.run(TOKEN)