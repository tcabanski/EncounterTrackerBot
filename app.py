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

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')

@bot.command(name='start')
async def xx(ctx):
    encounter = json.loads(pyperclip.paste())
    await ctx.message.author.send(f'Hello from bot {encounter}')
    await ctx.send(f'Hello from bot {encounter}')

bot.run(TOKEN)