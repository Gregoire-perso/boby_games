#!/usr/bin/python3
import configparser as configp
import discord
from discord.ext import commands
#import logging
import json
import asyncio
import hangman.commands as hangman

ASBOLUTE_PATH="."
# Config part
config = configp.ConfigParser()
config.read(ABSOLUTE_PATH+"/config.ini")



"""
# Log part
logger = logging.getLogger('discord')
logging.basicConfig(level=logging.DEBUG)
handler = logging.FileHandler(filename='faw.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
"""

class BobyGames(commands.Bot):
    def __init__(self, description='', language='fr'):
        """description: str -> description of the bot
           language: str -> language of the bot ; must be in ['fr', 'en'] """
        super().__init__(command_prefix="%", description=description)
        self.language = language

    async def on_ready(self):
        print("Bot is ready")

    async def on_message(self, message):
        if message.author == self.user:
            return 
    
        await self.process_commands(message)

    #async def on_command_error(self, ctx, error):
    #    """Errors handler for the whole bot"""
    #    pass

#----------------------------------------------------------------------------------------

class BobyCommands(commands.Cog):
    def __init__(self, bot):
        self.__bot = bot
        self.__current_user = None

#----------------------------------------------------------------------------------------

    def check_language(self, reaction, user):
        """Check if the reaction is correct"""
        return str(reaction.emoji) in ['\U0001f1eb\U0001f1f7', '\U0001f1ec\U0001f1e7'] and user == self.__current_user
    
#----------------------------------------------------------------------------------------

    @commands.command()
    async def ping(self, ctx):
        await ctx.channel.send(embed=discord.Embed(color=discord.Color.green(), description="Pong ! {0}s".format(round(self.__bot.latency, 2))))

#----------------------------------------------------------------------------------------

    @commands.command()
    async def hello(self, ctx):
        await ctx.channel.send(embed=discord.Embed(color=discord.Color.green(), description="Salut ! Moi c'est Boby !"))

#----------------------------------------------------------------------------------------

    @commands.command(aliases=['language', 'langue'])
    async def set_language(self, ctx):
        """Define the language used by the bot
        Choosen by reacting to the bot message """
        self.__current_user = ctx.author

        with open(ABSOLUTE_PATH+"/translations/"+self.__bot.language+".json", "r") as f:
            replies = json.load(f)

        choice = await ctx.channel.send(embed=discord.Embed(color=discord.Color.light_grey(), description=replies["changeLanguage"], footer=replies["footerReaction"]))

        # Adding reactions
        await choice.add_reaction('\U0001f1eb\U0001f1f7') # French flag
        await choice.add_reaction('\U0001f1ec\U0001f1e7') # UK Flag

        # Waiting for a reaction
        try:
            reaction, user = await self.__bot.wait_for('reaction_add', timeout=60.0, check=self.check_language)

        except asyncio.TimeoutError:
            self.__current_user = None
            return
                    
        # Process reactions
        if str(reaction.emoji) == '\U0001f1eb\U0001f1f7': # French
            self.__bot.language = 'fr'

        else: # English (default)
            self.__bot.language = 'en'

        await choice.remove_reaction(reaction.emoji, self.__current_user)
        # Reloading language
        with open(ABSOLUTE_PATH+"/translations/"+self.__bot.language+".json", "r") as f:
            replies = json.load(f)

        await ctx.channel.send(embed=discord.Embed(color=discord.Color.green(), description=replies["changedLanguage"]))

        self.__current_user = None

#----------------------------------------------------------------------------------------

description = '''A small bot to play small games'''

bot = BobyGames(description)
bot.add_cog(BobyCommands(bot))
bot.add_cog(hangman.HangmanCommands(bot))
bot.run(config.get('Initialize', 'Token'))

