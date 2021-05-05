""" 
Idées d'amélioration : 
    Faire en sorte que le choix de la langue se fasse en reaction au message

"""

import discord
from discord import Color
from discord import Embed
from discord.ext import commands
import json
from unidecode import unidecode
from random import randint

class HangmanGame(commands.Cog):
    def __init__(self, bot: commands.Bot, language: str, ctx: commands.Context):
        """Init a game"""
        self.__bot = bot
        self.__language = language
        self.__ctx = ctx


    def __check_message(self, msg):
        return msg.author == self.__ctx.author and msg.channel == self.__ctx.channel


    async def start_game(self):
        """Start a game"""
        # Loading replies
        with open("./hangman/translations/"+self.__language+".json", "r") as f:
            replies = json.load(f)

        # Display rules
        await self.__ctx.channel.send(embed=Embed(color=Color.orange(), description=replies["rules"]))
        
        # Choosing a word
        with open("./hangman/translations/"+self.__language+".txt", "r") as words:
            mystery_word = words.readlines()

        mystery_word = mystery_word[randint(0, len(mystery_word)-1)]

        # Start the real game !
        found_word = False
        while not found_word:
            # Displaying the finding pattern
            display_word = "_ "*len(mystery_word)
            await self.__ctx.channel.send(embed=Embed(color=Color.grey(), description=display_word))

            # Waiting for an answer
            try:
                message = await self.__bot.wait_for('message', check=self.__check_message, timeout=30.0)

            except asyncio.TimeoutError:
                await self.__ctx.channel.send(embed=Embed(color=Color.red(), description="Vous avez été bien trop lent cow-boy, vous êtes morts... :skull:"))
                return

        
        
        
    



class HangmanCommands(commands.Cog):
    """Commands linked to hangman game"""
    def __init__(self, bot, language="french"):
        self.__bot = bot
        self.__language = language

    @commands.command()
    async def set_language(self, ctx, text: str):
        """Define the language
        Must be 'french' or 'english' """
        if not unidecode(text).lower() in ['french', 'english', 'francais', 'anglais']:
            with open("./hangman/translations/"+self.__language+".json", "r") as replies:
                wrong_language_choice = json.load(replies)["wrongLanguageChoice"]

            await ctx.channel.send(embed=discord.Embed(color=discord.Color.red(), description=wrong_language_choice))

        else:
            self.__language = unidecode(text).lower()


    @commands.command()
    async def start_hangman(self, ctx):
        game = HangmanGame(self.__bot, self.__language, ctx) # Create a new game
        await game.start_game() # Start the new game




