import asyncio
import logging
import re
from configparser import ConfigParser
import ipcalc
import nextcord
import requests
from nextcord import SlashOption
from nextcord.ext import commands


# load config file
config_object = ConfigParser()
config_object.read("config.ini")

botConfig = config_object['BOT_CONFIG']

welcome_channel_id = int(botConfig["welcome_chanel"])



class generalCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

        self.bot.remove_command("help")


    @nextcord.slash_command(description="show help message")
    async def help(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Liste des commandes", color=0x69edf8)
        embed.add_field(name="/remindme",
                        value="permet d'envoyé un rappel (message custom) à quelqu'un ou à soi meme apres X minutes",
                        inline=False)
        embed.add_field(name="/anime", value="envoie une images random d'anime girl", inline=True)
        embed.add_field(name="/cat", value="envoie une image random de chat", inline=True)
        embed.add_field(name="/ip <ip> <mask>",
                        value="calcule tout ce qu'il faut calculé sur une IP et un masque. EX: ``/ip ip:192.168.0.0 mask:32`` ou ``/ip ip:10.0.0.0 mask:255.255.0.0``",
                        inline=True)
        embed.add_field(name="/convert <valeur>",
                        value="convertis une ``valeur`` (bin: 0bVALEUR ; hex: 0xVALEUR ; dec: VALEUR) dans les autres bases EX: ``/convert valeur:0b1010`` ou ``/convert valeur:0xA5C``",
                        inline=True)
        await interaction.response.send_message(embed=embed)


    @nextcord.slash_command(description="remind someone, to do something, in sometime")
    async def remindme(self, interaction: nextcord.Interaction,
                    todo: str = SlashOption(name="the-thing", description="the thing to do", required=True),
                    time: int = SlashOption(name="in-minutes", description="the reminder will be send in X minutes", required=True, max_value=240),
                    user: nextcord.Member = SlashOption(name="the-user", description="the reminder msg will be sent to this user", required=False)
                    ):

        user = interaction.user if user is None else user

        ReminderEmbed = nextcord.Embed(title=f"{todo}", color=nextcord.Color.red(), description=f"de la part de {interaction.user.name} ; reminder enregistré il y à {time} min")

        # convert to second and wait
        time_sec = time * 60

        ReminderOkEmbed = nextcord.Embed(title=f"Reminder enregistré !", color=nextcord.Color.green(), description=f"{user.name} recevra un message dans {time} minutes ({time_sec} second)")

        await interaction.response.send_message(embed=ReminderOkEmbed)

        await asyncio.sleep(time_sec)
        await user.send(embed=ReminderEmbed)


    @nextcord.slash_command(description="get a random anime pic")
    async def anime(self, interaction: nextcord.Interaction):

        response = requests.get("https://api.nekosapi.com/v3/images/random", params={"limit": 1, "is_nsfw": False})
        # "is_nsfw": False doesn't work

        if response.status_code == 200:
            await interaction.response.send_message(response.json()['items'][0]['image_url'])
        else:
            await interaction.response.send_message("request ended in a non 200 exit code : "+str(response.status_code))


    @nextcord.slash_command(description="get a random cat pic (specialement fait pour kilou)")
    async def cat(self, interaction: nextcord.Interaction):

        # await interaction.response.send_message(f"https://cataas.com/cat?random={random.randint(1, 1000)}")
        response = requests.get("https://api.thecatapi.com/v1/images/search?limit=1")

        if response.status_code == 200:
            await interaction.response.send_message(response.json()[0]['url'])
        else:
            await interaction.response.send_message("request ended in a non 200 exit code : "+str(response.status_code))


    @nextcord.slash_command(description="calcul tout ce qu'il faut calculé à propos d'une IP")
    async def ip(self, interaction: nextcord.Interaction,
                 ip: str = SlashOption(name="ip", description="ip address", required=True),
                 mask: str = SlashOption(name="mask", description="ip mask", required=True)):

        if not re.match(r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$", ip):
            await interaction.response.send_message("invalid IP")
            return

        # mask is a CIDR, else convert it to CIDR
        if re.match(r"^(0|[1-9][0-9]*)$", mask):
            mask_cidr = int(mask)

        elif re.match(r"^((25[0-5]|(2[0-4]|1\d|[1-9]|)\d)\.?\b){4}$", mask):
            octets = mask.split('.')
            binary_str = ''.join([bin(int(octet)).lstrip('0b').zfill(8) for octet in octets])
            mask_cidr = binary_str.count('1')

        else:
            await interaction.response.send_message("invalid mask")
            return

        network = ipcalc.Network(f"{ip}/{mask_cidr}")

        embed_content = f"""
```
address :                     {network.dq}
address (bin) :     {network.bin()}
masque (mask) :               {network.netmask()}
masque (cidr) :               {network.mask}
masque (bin) :      {network.netmask().bin()}
reseau (network) :            {network.network()}
diffusion (broadcast) :       {network.broadcast()}
hote min (smallest) :         {network.host_first()}
hote max (largest) :          {network.host_last()}
network size :                {network.size()}
```
        """

        EmbedRes = nextcord.Embed(title="Calculette IP", color=nextcord.Color.blue())
        EmbedRes.add_field(name="", value=embed_content)

        await interaction.response.send_message(embed=EmbedRes)


    @nextcord.slash_command(description="convertis en hex en bin et en dec")
    async def convert(self, interaction: nextcord.Interaction,
                      value: str = SlashOption(name="value", description="value", required=True)):

        value = value.strip()

        try:
            # Check if the input is in binary
            if value.startswith('0b') or value.startswith('%'):
                base = 2
                num = int(value, base)
            # Check if the input is in hexadecimal
            elif value.startswith('0x'):
                base = 16
                num = int(value, base)
            # Otherwise, assume it is a decimal
            else:
                base = 10
                num = int(value, base)

        except ValueError as val_err:
            await interaction.response.send_message(f"incorrect input value : {val_err}")
            return

        # Convert to the other formats
        decimal_value = num
        hex_value = hex(num)
        binary_value = bin(num)

        EmbedRes = nextcord.Embed(title="Convertisseur hex/bin/dec", description="put ``0x`` for a hex value \n put ``0b`` or ``%`` for a bin \n just put the number for decimal",color=nextcord.Color.blue())
        EmbedRes.add_field(name="Input value :", value=value, inline=False)
        EmbedRes.add_field(name="Decimal value :", value=decimal_value)
        EmbedRes.add_field(name="Hexadecimal value :", value=hex_value)
        EmbedRes.add_field(name="Binary value :", value=binary_value)

        await interaction.response.send_message(embed=EmbedRes)






    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: nextcord.Interaction, error):
        logging.error(f"Error in cog.commands : {error}")


    @commands.Cog.listener()
    async def on_member_join(self, member: nextcord.Member):
        channel = self.bot.get_channel(welcome_channel_id)

        if channel is not None:
            await channel.send(f"et on dit bienvenue à {member.mention}")

        else:
            logging.error(f"channel with ID {welcome_channel_id} not found")
            logging.info(f"new member {member.name} joined")
            return


    @commands.Cog.listener()
    async def on_member_remove(self, member: nextcord.Member):
        channel = self.bot.get_channel(welcome_channel_id)

        if channel is not None:
            await channel.send(f"et on dit aurevoir à {member.mention}")

        else:
            logging.error(f"channel with ID {welcome_channel_id} not found")
            logging.info(f"member {member.name} leaved the guild")
            return



# registre cog to the Bot
def setup(bot: commands.Bot):
    bot.add_cog(generalCommand(bot))
