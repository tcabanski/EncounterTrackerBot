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

members = []
round = 0
currentTurn = None

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='start')
async def xx(ctx):
    members = []
    round = 0
    currentTurn = None
    await ctx.send(f'Combat ready')

@bot.command(name ='add')
async def add(ctx, qty: int, name: str, hp: int, ac: int, init: str):
    if init == None:
        init = '+0'

    for x in range(1, qty + 1):
        if qty > 1:
            adjName = f'{name}{x}'
        else:
            adjName = name

        members.append({
            "init": init,
            "name": adjName,
            "hp": hp,
            "ac": ac
        })
            
    await ctx.message.author.send(f'Add complete {members}')
    await ctx.send(f'Add complete {members}')


bot.run(TOKEN)