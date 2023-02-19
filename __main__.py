import discord
import asyncio
import logging
from discord.ext import commands

# create bot instance
bot = commands.Bot(command_prefix=command_prefix, description=description, case_insensitive=True, intents=discord.Intents.all())

# create log handler for discord.py
log_handler = logging.FileHandler(filename='discordBot.log', encoding='utf-8', mode='w')



cogsCommand = ['cogs.test']

if __name__ == '__main__':

    '''load cogs'''

    for extension in cogsCommand:
        bot.load_extension(extension)


@bot.event 
async def on_ready():
    print('Logged in as')
    print(bot.user)
    print('------')

