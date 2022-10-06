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

parser = argparse.ArgumentParser("@e", add_help=False)
subparsers = parser.add_subparsers(dest="command", help="Commands")

parser_start = subparsers.add_parser("start", aliases=["s"], help="Start an encounter", add_help=False)
parser_start.add_argument("channelName", type=str, help="Channel name to display encounter to players")

parser_end = subparsers.add_parser("end", aliases=["e"], help="End an encounter", add_help=False)

parser_join = subparsers.add_parser("join", aliases=["j"], help="Join a PC to an encounter", add_help=False)
parser_join.add_argument("name", type=str, help="Name")
parser_join.add_argument("initiative", type=int, help="Initiative")
parser_join.add_argument("-hp", type=int, help="current hps", default=-1)
parser_join.add_argument("-maxhp", "-max", "-m", type=int, help="maximum hps", default=-1)
parser_join.add_argument("-temphp", "-temp", "-tmp", "-t", type=int, help="temporary hps", default=-1)
parser_join.add_argument("-roll", "-r", help="true to roll initiative (initiative becomes modifier)", action="store_true")

parser_display = subparsers.add_parser("display", aliases=["d"], help="Display an encounter", add_help=False)

parser_next = subparsers.add_parser("next", aliases=["n"], help="Next turn", add_help=False)

parser_prev = subparsers.add_parser("prev", aliases=["p"], help="Previous turn", add_help=False)

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
        if len(a) > 0:
            match a[0]:
                case "start" | "s":
                    await ctx.send(parser_start.format_help())
                case "end" | "e":
                    await ctx.send(parser_end.format_help())
                case "join" | "j":
                    await ctx.send(parser_join.format_help())
                case "display" | "d":
                    await ctx.send(parser_display.format_help())
                case "next" | "n":
                    await ctx.send(parser_next.format_help())
                case "prev" | "p":
                    await ctx.send(parser_prev.format_help())
                case _:
                    await ctx.send("invalid command")
        else:
            await ctx.send("invalid command")
        
        return

    match args.command:
        case "start" | "s":
            await start(ctx, args)
        case "end" | "e":
            await end(ctx, args)
        case "join" | "j":
            await join(ctx, args)
        case "display" | "d":
            await display(ctx, args)
        case "next" | "n":
            await nextTurn(ctx, args)
        case "prev" | "p":
            await prevTurn(ctx, args)
        case _:
            await ctx.send(parser.format_help())

async def start(ctx, args):
    if encounter["running"]:
        await ctx.send('Combat alreay running.  Use "end" to stop.')
        return

    initialize(ctx, args.channelName)
    await ctx.send(f'Combat ready')
    await encounter["channel"].send(f"Please join using command:\n `@e j [name] [initative]`")

async def end(ctx, args):
    if encounter["running"] == False:
        await ctx.send('Combat is not running.  Use "start" to start.')
        return

    if ctx.author.id != encounter["owner"].id:
        await ctx.send('Only the DM can use this command')
        return

    encounter["running"] = False
    await ctx.send(f'Encounter ended')
    await encounter["channel"].send(f"Encounter has ended")

async def join(ctx, args):
    if encounter["running"] == False:
        await ctx.send('Combat is not running.  Please wait for the DM')
        return

    encounter["members"].append({
        "name": args.name,
        "initiative": args.initiative,
        "hp": args.hp,
        "maxHp": args.maxhp,
        "tempHp": args.temphp
    })

    message = f"{args.name} added to encounter with initative {args.initiative}"
    if args.roll:
        rollspec = "1d20"
        if args.initiative > 0:
            rollspec = rollspec + f"+{args.initiative}"
        else:
            rollspec = rollspec + f"{args.initiative}"

        roll = d20.roll(rollspec)
        args.initiative = roll.total
        message = f"{args.name} added to encounter and rolled initative {roll}"

    encounter["members"].sort(reverse=True, key=lambda e: e["initiative"])

    await ctx.send(message)
    await encounter["channel"].send(message)

async def display(ctx, args):
    if encounter["running"] == False:
        await ctx.send('Combat is not running.  Please wait for the DM')
        return

    if ctx.author.id != encounter["owner"].id:
        await ctx.send('Only the DM can use this command')
        return

    text = "```prolog\n========================="
    if encounter["round"] < 0:
       text = text + f"\nEncounter round: NONE" 
    else:
        text = text + f"\nEncounter round: {encounter['round'] + 1}"
    
    members = encounter["members"]
    
    if len(members) == 0:
        text = text + "\nNo creatures in encounter"
    else:
        for x in range(0, len(members)):
            text = text + await addMemberToDisplayText(ctx, x)

    text = text + "\n```"

    await encounter["channel"].send(text)

async def addMemberToDisplayText(ctx, index):
    members = encounter["members"]
    member = members[index]
    turn = encounter["turn"]

    text = ""

    if index == turn:
        text = text + f"\n**{member['initiative']}: {member['name']}({index + 1}) {getHealthIndicator(index)}**"
    else:
        text = text + f"\n{member['initiative']}: {member['name']}({index + 1}) {getHealthIndicator(index)}"

    return text

def getHealthIndicator(index):
    if index >= len(encounter["members"]):
        return ""

    member = encounter["members"][index]

    if member["hp"] < 0:
        return ""

    hp = member["hp"]

    if member["tempHp"] >= 0:
        hp = hp + member["tempHp"]

    if member["maxHp"] < 0:
        if hp > 0:
            return "<'Alive'>"
        
        return "<dead>"
    
    maxHp = member["maxHp"]

    if hp > (maxHp / 2):
        return "<'Healty'>"
    elif hp > 0:
        return "<Wounded>"
    
    return "<dead>"


async def nextTurn(ctx, args):
    if encounter["running"] == False:
        await ctx.send('Combat is not running.  Please wait for the DM')
        return

    if ctx.author.id != encounter["owner"].id:
        await ctx.send('Only the DM can use this command')
        return

    turn = encounter["turn"] 
    round = encounter["round"]
    members = encounter["members"]

    if len(members) < 1:
        await ctx.send('No creatures in encounter.  Use join for PCs or add for monsters.')
        return

    if round < 0:
        round = round + 1

    turn = turn + 1
    if turn >= len(members):
        turn = 0
        round = round + 1

    encounter["round"] = round
    encounter["turn"] = turn

    await displayTurn(ctx)

async def prevTurn(ctx, args):
    if encounter["running"] == False:
        await ctx.send('Combat is not running.  Please wait for the DM')
        return

    if ctx.author.id != encounter["owner"].id:
        await ctx.send('Only the DM can use this command')
        return

    turn = encounter["turn"] 
    round = encounter["round"]
    members = encounter["members"]

    if len(members) < 1:
        await ctx.send('No creatures in encounter.  Use join for PCs or add for monsters.')
        return

    if turn == 0 and round == 0:
        await ctx.send('Already on first turn of the encounter. There is no previous turn.')
        return

    turn = turn - 1
    if turn < 0:
        turn = len(members) - 1
        round = round - 1

    encounter["round"] = round
    encounter["turn"] = turn

    await displayTurn(ctx)

async def displayTurn(ctx):
    text = "========================="
    text = text + f"\nEncounter round: {encounter['round'] + 1}"
    members = encounter["members"]
    turn = encounter["turn"]
    nextTurn = turn + 1
    prevTurn = turn - 1 

    if nextTurn == len(members):
        nextTurn = 0

    if prevTurn < 0:
        prevTurn = len(members) - 1

    text = text + await addMemberToDisplayText(ctx, prevTurn)
    text = text + await addMemberToDisplayText(ctx, turn)
    text = text + await addMemberToDisplayText(ctx, nextTurn)

    await encounter["channel"].send(text)

bot.run(TOKEN)