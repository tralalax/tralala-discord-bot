import logging
import os
import pty
import subprocess
from configparser import ConfigParser

import nextcord
from nextcord.ext import application_checks
from nextcord.ext import commands

# load config file
config_object = ConfigParser()
config_object.read("config.ini")

botConfig = config_object['BOT_CONFIG']

encoding = botConfig["encoding"]
authorized_ID = list(map(int, botConfig["authorized_ID"].split(',')))



class ShellCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot: commands.Bot = bot

    @nextcord.slash_command(description="execute a command with subprocess run")
    async def execute(self, interaction: nextcord.Interaction, args: str):

        ''' execute a command on the server '''

        # check user perms
        if interaction.user.id not in authorized_ID:
            return

        args_list = args.split(" ")

        # create embed
        resultEmbed = nextcord.Embed(title="Server answer :", color=nextcord.Color.blue())

        try:
            # run_res = subprocess.run(args_list, shell=True, capture_output=True).stdout.decode(encoding, errors="replace") # , text=True
            run_res = subprocess.run(args_list, stdout=subprocess.PIPE).stdout.decode(encoding) # encoding

        except Exception as err:
            resultEmbed.add_field(name="Error executing comand : ", value=f"```{err}```", inline=False)
            await interaction.response.send_message(embed=resultEmbed)

        # split into multiple field (25 max) if the size is too big (1024 max)
        if len(run_res) > 1000:
            run_res_chunks = [run_res[i:i + 1000] for i in range(0, len(run_res), 1000)]

            for i, chunk in enumerate(run_res_chunks):
                resultEmbed.add_field(name=f"", value="```" + chunk + "```", inline=False)

        else:
            resultEmbed.add_field(name="", value="```" + run_res + "```", inline=False)

        await interaction.response.send_message(embed=resultEmbed)


    @execute.error
    async def perms_error(self, interaction: nextcord.Interaction, error):
        if isinstance(error, application_checks.ApplicationMissingPermissions):
            ErrorPermsEmbed = nextcord.Embed(title="Nope !", color=nextcord.Color.blue())
            ErrorPermsEmbed.add_field(name="",
                                      value="Désolé. Vous n'avez pas les permissions nécessaires pour utiliser cette commande.\n")
            ErrorPermsEmbed.add_field(name="", value="Sorry. You don't have permission to use this command.")

            await interaction.response.send_message(embed=ErrorPermsEmbed)

    @commands.Cog.listener()
    async def on_application_command_error(self, interaction: nextcord.Interaction, error):
        logging.error(f"Error in cog.shell : {error}")






# registre cog to the Bot
def setup(bot: commands.Bot):
    bot.add_cog(ShellCog(bot))