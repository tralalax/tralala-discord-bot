import datetime
import logging
from configparser import ConfigParser

import nextcord
from nextcord.ext import commands

# create log handler for discord.py
log_handler = logging.FileHandler(filename='discordBot.log', encoding='utf-8', mode='w')

# load config file
config_object = ConfigParser()
config_object.read("config.ini")

botConfig = config_object['BOT_CONFIG']

# create bot instance
bot = commands.Bot(command_prefix='$', case_insensitive=True, intents=nextcord.Intents.all())

# get curent date
currentDate = datetime.datetime.now().strftime("%Y-%m-%d")

# file logging
logging.basicConfig(filename='logs/bot-log-'+currentDate+'.log', format='%(asctime)s %(message)s', filemode='w', level=logging.INFO)

# cogs file declaration
initial_extensions = ['cogs.shell', 'cogs.commands']

# load cogs extension
def load_cogs():

    logging.info("loading Cogs...")

    for extension in initial_extensions:
        logging.info("loading cog : "+extension)

        bot.load_extension(extension)


@bot.event
async def on_ready():
    await bot.wait_until_ready()

    print('Logged in as')
    print(bot.user)
    print('------')

    # await bot.tree.sync()

    logging.info("bot ready")


if __name__ == '__main__':

    print("received start")

    # load cogs
    load_cogs()

    logging.info("bot started")
    # run Bot

    bot.run(botConfig["token"])
    logging.fatal("bot shutdown, ending loop")

