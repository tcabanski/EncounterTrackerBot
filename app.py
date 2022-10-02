# bot.py
from email import message
import os
import random
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
    'round': 0, 
    'members': []
}

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='start')
async def xx(ctx):
    encounter = {
        'round': 0, 
        'members': []
    }
    await ctx.message.author.send(f'Hello from bot {encounter}')
    await ctx.send(f'Hello from bot {encounter}')

@bot.command(name ='add')
async def add(ctx, name: str, hp: int, ac: int, init: str):
    if init == None:
        init = '+0'

    encounter['members'].append({
        "init": init,
        "name": name,
        "hp": hp,
        "ac": ac
    })
    await ctx.message.author.send(f'Add complete {encounter}')
    await ctx.send(f'Add complete {encounter}')


bot.run(TOKEN)