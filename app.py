# bot.py
from email import message
import os
import random
from bs4 import MarkupResemblesLocatorWarning
import discord
from dotenv import load_dotenv
import pyperclip
import json

from discord.ext import commands

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(intents=intents, command_prefix='@')

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

@bot.command(name='start')
async def start(ctx, channelName: str):
    if encounter["running"]:
        await ctx.send('Combat alreay running.  Use "end" to stop.')
        return

    initialize(channelName)
    await ctx.send(f'Combat ready')
    await encounter["channel"].send("channel message")

@bot.command(name ='add')
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