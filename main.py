#!/usr/bin/python3
import sys
import configparser as configp
import discord
from discord import Color, Embed
from discord.ext import tasks, commands
import json
import asyncio
from random import randint
import hangman.commands as hangman

import logging, traceback

# Config part
config = configp.ConfigParser()
config.read(sys.argv[1])
WORKING_PATH=config.get("Initialize", "WorkingPath")


async def on_error(event, *args, **kwargs):
    print('Something went wrong!')
    logging.warning(traceback.format_exc())


class BobyGames(commands.Bot):
    def __init__(self, description='', language='fr'):
        """description: str -> description of the bot
           language: str -> language of the bot ; must be in ['fr', 'en'] """
        super().__init__(command_prefix="%", description=description)
        self.language = language
        self.mood = randint(0, 100)
        print(self.mood)

    async def on_ready(self):
        print("Bot is ready")

    #------------------------------------------------------------------------------------

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
        self.boby_mood.start()

    #------------------------------------------------------------------------------------

    def check_language(self, reaction, user):
        """Check if the reaction is correct"""
        return str(reaction.emoji) in ['\U0001f1eb\U0001f1f7', '\U0001f1ec\U0001f1e7'] and user == self.__current_user

    #------------------------------------------------------------------------------------

    @tasks.loop(seconds=5.0)
    async def boby_mood(self):
        """Define a new mood for boby"""
        self.__bot.mood = randint(0, 100)
        print(self.__bot.mood)
    
    #------------------------------------------------------------------------------------

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Send a message in general channel when there is a new member"""
        print("coucou new member")
        if member.guild.system_channel is None:
            return

        if  self.mood < 10:
            msg = f"{member.mention}, qu'est ce que tu fou là ??? Pourquoi tu me fais chier sérieux, je dormais...\nDe toutes façons t'es adopté"

        elif self.mood < 25:
            msg = f"Salut {member.mention}. Allez maintenant casse toi et laisse moi faire mon boulot"

        elif self.mood < 40:
            msg = f"Salut {member.mention}. Allez maintenant vas voir ailleurs si j'y suis et laisse moi dormir"

        elif self.mood < 75:
            msg = f"Salutations {member.mention}, et bienvenue chez {member.guild} !"

        elif self.mood < 90:
            msg = f"Salut {member.mention}, et bienvenue chez {member.guild}, une guilde super sympatique avec pleins de trucs à faire !"

        else:
            msg = f"Salut à toi {member.mention} !  Bienvenue chez {member.guild}, une guilde composée uniquement de gens sympa ! (Et en plus y'a pleins de trucs à faire :wink:)"

        await member.guild.system_channel.send(embed=Embed(color=Color.random(), description=msg))

    #------------------------------------------------------------------------------------

    @commands.command()
    async def ping(self, ctx):
        await ctx.channel.send(embed=Embed(color=Color.green(), description="Pong ! {0}s".format(round(self.__bot.latency, 2))))

    #------------------------------------------------------------------------------------

    @commands.command(aliases=['main_channel'])
    async def set_main_channel(self, ctx):
        """Set the channel used to welcome members
        Type that command directly into the channel you want to use"""
        self.__bot.main_channel = ctx.channel
        await ctx.channel.send(embed=Embed(color=Color.green(), description="C'est fait !"))

    #------------------------------------------------------------------------------------

    @commands.command()
    async def hello(self, ctx):
        await ctx.channel.send(embed=Embed(color=Color.green(), description="Salut ! Moi c'est Boby !"))

    #------------------------------------------------------------------------------------

    @commands.command(aliases=['language', 'langue'])
    async def set_language(self, ctx):
        """Define the language used by the bot
        Choosen by reacting to the bot message """
        self.__current_user = ctx.author

        with open(WORKING_PATH+"/translations/"+self.__bot.language+".json", "r") as f:
            replies = json.load(f)

        choice = await ctx.channel.send(embed=Embed(color=Color.light_grey(), description=replies["changeLanguage"], footer=replies["footerReaction"]))

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
        with open(WORKING_PATH+"/translations/"+self.__bot.language+".json", "r") as f:
            replies = json.load(f)

        await ctx.channel.send(embed=Embed(color=Color.green(), description=replies["changedLanguage"]))

        self.__current_user = None

    #------------------------------------------------------------------------------------

description = '''A small bot to play small games'''

bot = BobyGames(description)
bot.add_cog(BobyCommands(bot))
bot.add_cog(hangman.HangmanCommands(bot))
bot.run(config.get('Initialize', 'Token'))

