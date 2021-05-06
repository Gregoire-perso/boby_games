""" 
Idées d'amélioration : 
    Faire en sorte que le choix de la langue se fasse en reaction au message

"""

import discord
import asyncio
from discord import Color
from discord import Embed
from discord.ext import commands
import json
from unidecode import unidecode
from random import randint

ABSOLUTE_PATH='./'

class HangmanGame(commands.Cog):
    def __init__(self, bot: commands.Bot, language: str, ctx: commands.Context, multi: bool):
        """Init a game"""
        self.__bot = bot
        self.__language = language
        self.__ctx = ctx
        self.__mystery_word = ""
        self.__tried_letters = []
        self.__nb_essais = 0
        self.__nb_fails = 0
        self.__multi = multi

#----------------------------------------------------------------------------------------

    def __check_message(self, msg):
        if self.__multi:
            return msg.channel == self.__ctx.channel
        else:
            return msg.author == self.__ctx.author and msg.channel == self.__ctx.channel

#----------------------------------------------------------------------------------------

    async def __process_message(self, msg, replies):
        """Process the message content"""
        if len(msg) == 1 and msg in self.__tried_letters:
            await self.__ctx.channel.send(embed=Embed(color=Color.orange(), description=replies["letterAlreadyTried"]))


        elif len(msg) == 1 and msg in self.__mystery_word:
            self.__tried_letters.append(msg)
            await self.__ctx.channel.send(embed=Embed(color=Color.green(), description=replies["rightLetter"]))
            self.__nb_essais += 1


        elif len(msg) == 1:
            self.__tried_letters.append(msg)
            await self.__ctx.channel.send(embed=Embed(color=Color.orange(), description=replies["wrongLetter"]))
            self.__nb_essais += 1
            self.__nb_fails += 1


        elif msg == self.__mystery_word:
            await self.__ctx.channel.send(embed=Embed(color=Color.green(), description=replies["rightWord"].format(self.__nb_essais)))
            self.__nb_essais += 1
            return "WON"


        else:
            await self.__ctx.channel.send(embed=Embed(color=Color.green(), description=replies["wrongWord"].format(self.__nb_essais)))
            self.__nb_essais += 1
            self.__nb_fails += 1

#----------------------------------------------------------------------------------------

    async def __draw_hangman(self):
        """draw the hangman"""
        with open(ABSOLUTE_PATH+"hangman/hangman_"+str(self.__nb_fails)+".txt", "r") as f:
            await self.__ctx.channel.send(embed=Embed(color=Color.light_grey(), description="```\n"+"".join(f.readlines())+"\n```"))


#----------------------------------------------------------------------------------------

    async def start_game(self):
        """Start a game"""
        # Loading replies
        with open(ABSOLUTE_PATH+"hangman/translations/"+self.__language+".json", "r") as f:
            replies = json.load(f)

        # Display rules
        await self.__ctx.channel.send(embed=Embed(color=Color.random(), description=replies["rules"]))
        
        # Choosing a word
        with open(ABSOLUTE_PATH+"hangman/translations/"+self.__language, "r") as f:
            words = f.readlines()

        self.__mystery_word = words[randint(0, len(words)-1)].upper().replace("\n", "")

        # Start the real game !
        found_word = False
        display_word = "_"*len(self.__mystery_word)
        print(self.__mystery_word)
        while not found_word:
            # Displaying the finding pattern
            await self.__ctx.channel.send(embed=Embed(color=Color.light_grey(), description="`"+display_word+"`\n"+replies["askLetter"]))

            # Waiting for an answer
            try:
                message = await self.__bot.wait_for('message', check=self.__check_message, timeout=30.0)

            except asyncio.TimeoutError:
                await self.__ctx.channel.send(embed=Embed(color=Color.red(), description=replies["tooSlow"]))
                await self.__ctx.channel.send(embed=Embed(color=Color.red(), description=replies["printMysteryWord"].format(self.__mystery_word)))
                found_word = True
                continue



            # Testing message
            if await self.__process_message(message.content.upper().replace(" ", ""), replies) == "WON":
                found_word = True
                continue

            elif self.__nb_fails >= 10:
                await self.__draw_hangman()
                await self.__ctx.channel.send(embed=Embed(color=Color.red(), description=replies["loose"]))
                await self.__ctx.channel.send(embed=Embed(color=Color.red(), description=replies["printMysteryWord"].format(self.__mystery_word)))
                found_word = True
                continue

            else:
                await self.__draw_hangman()



            # Modifying display_word
            indexes = [i for i, x in enumerate(self.__mystery_word) if x in self.__tried_letters]
            display_word = ""
            for i in self.__mystery_word:
                if i in self.__tried_letters:
                    display_word += i
                else:
                    display_word += "_"

            if not "_" in display_word:
                await self.__ctx.channel.send(embed=Embed(color=Color.green(), description=replies["rightWord"].format(self.__nb_essais)))
                found_word = True
                continue






class HangmanCommands(commands.Cog):
    """Commands linked to hangman game"""
    def __init__(self, bot):
        self.__bot = bot
    
    @commands.command(aliases=['hangman', 'hm'])
    async def start_hangman(self, ctx):
        game = HangmanGame(self.__bot, self.__bot.language, ctx, multi=False) # Create a new game
        await game.start_game() # Start the new game




