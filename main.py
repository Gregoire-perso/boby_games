import configparser as configp
import discord
from discord.ext import commands
import logging
import hangman.commands as hangman

# Config part
config = configp.ConfigParser()
config.read('config.ini')

"""
# Log part
logger = logging.getLogger('discord')
logging.basicConfig(level=logging.DEBUG)
handler = logging.FileHandler(filename='faw.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
"""

class BobyGames(commands.Bot):
    def __init__(self, description=''):
        super().__init__(command_prefix="%", description=description)

    async def on_ready(self):
        print("Bot is ready")

    #async def on_message(self, message):
    #    if message.author == self.user:
    #        return 
    #
    #    if message.content.lower() == "ping":
    #        print(message.channel)
    #        await message.channel.send("Pong !")
    #
    #    await self.process_commands(message)

    #async def on_command_error(self, ctx, error):
    #    """Errors handler for the whole bot"""
    #    pass

#------------------------------------------------------------------------------------------

class BobyCommands(commands.Cog):
    def __init__(self, bot):
        self.__bot = bot
    
    @commands.command()
    async def ping(self, ctx):
        await ctx.channel.send(embed=discord.Embed(color=discord.Color.green(), description="Pong ! {0}s".format(round(self.__bot.latency, 2))))

    @commands.command()
    async def hello(self, ctx):
        await ctx.channel.send(embed=discord.Embed(color=discord.Color.green(), description="Salut ! Moi c'est Boby !"))


#------------------------------------------------------------------------------------------

description = '''A small bot to play small games'''

bot = BobyGames(description)
bot.add_cog(BobyCommands(bot))
bot.add_cog(hangman.HangmanCommands(bot))
bot.run(config.get('Initialize', 'Token'))
