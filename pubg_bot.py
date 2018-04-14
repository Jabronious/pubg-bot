import discord
import asyncio
import json
import pdb
import requests
from discord.ext import commands
from pubg_python import PUBG, Shard, exceptions
import pubg_utils
import os
from datetime import datetime, timedelta
import logging

logging.basicConfig(filename='debug.log',level=logging.DEBUG, format='%(asctime)s %(message)s')

description = """>>>>>Mr. Pubg-bot<<<<<
This bot will be your go-to pubg information buddy! Look at these neat commands:
All commands begin with "!"

"""
bot = commands.Bot(command_prefix='!', description=description)

DATA = json.load(open('bot_info.json'))
PUBG_CLIENT = PUBG(DATA["PUBG_API_KEY"], Shard.PC_NA)
EMOJIS = ["💩", "👌", "💯", "😁", "😍"]

@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.group(pass_context=True)
@asyncio.coroutine
def matches(ctx):
    """'Provides match data for the last 5 matches for the in-game name provided.
    By providing a date it will get all matches that day.'
    """
    if ctx.invoked_subcommand is None:
        try:
            logging.info(">>>>>>>>>>>>>searching for player %s<<<<<<<<<<<<<<<<<<<", ctx.subcommand_passed)
            player = PUBG_CLIENT.players().filter(player_names=[ctx.subcommand_passed])
            player = player[0]
            logging.info(">>>>>>>>>>>>>player found<<<<<<<<<<<<<<<<<<<")
        except exceptions.NotFoundError:
            yield from bot.say('That player does not exist. Make sure the name is identical')
            return
        
        #TODO: Make sure that if there are not 5 matches it only displays available matches
        match_dict = {}
        logging.info(">>>>>>>>>>>>>printing five matches<<<<<<<<<<<<<<<<<<<")
        embed = discord.Embed(title="React to the match you wish to see data for:",
                                colour=discord.Colour(14066432))
        for idx, match in enumerate(player.matches[:5]):
            match_dict[EMOJIS[idx]] = match.id
            embed.add_field(name=EMOJIS[idx] + ': ', value=match.id)
        yield from bot.say(embed=embed)

        logging.info(">>>>>>>>>>>>>waiting for reaction from %s<<<<<<<<<<<<<<<<<<<", ctx.message.author)
        res = yield from bot.wait_for_reaction(user=ctx.message.author, timeout=20000) #Waits for 10000ms (maybe?) for a user to react.
        logging.info("reaction occurred from %s", ctx.message.author)

        match = PUBG_CLIENT.matches().get(match_dict[res.reaction.emoji]) #splits message and pulls id
        
        yield from bot.say("Let me get that match's data.")
        embed = pubg_utils.build_embed_message(match, player, PUBG_CLIENT, False)
        yield from bot.say(embed=embed)
        
@matches.command(name='latest')
@asyncio.coroutine
def _latest(ign : str, name='latest-match'):
    """'latest <in-game name>. Will provide stats from the most recent match.'"""
    try:
        logging.info(">>>>>>>>>>>>>searching for player %s, subcommand: !latest<<<<<<<<<<<<<<<<<<<")
        player = PUBG_CLIENT.players().filter(player_names=[ign])
        player = player[0]
        logging.info(">>>>>>>>>>>>>player found<<<<<<<<<<<<<<<<<<<")
    except exceptions.NotFoundError:
        yield from bot.say('That player does not exist. Make sure the name is identical')
        return
    match = PUBG_CLIENT.matches().get(player.matches[0].id)
    
    yield from bot.say("Let me get that match's data.")
    embed = pubg_utils.build_embed_message(match, player, PUBG_CLIENT)
    yield from bot.say(embed=embed)

@matches.error
@asyncio.coroutine
def ign_error(error, ctx):
    yield from bot.say("You need to put a player's in-game name")

@matches.command(name='date')
@asyncio.coroutine
def _date(ign : str, *date : int):
    """'date <in-game name> <date> : Format the MM DD YYYY EX: 04 03 2018'"""
    pdb.set_trace()
    date = datetime(year=date[2], month=date[1], day=date[0])
    matches = PUBG_CLIENT.matches().filter(
        created_at_start=str(date),
        created_at_end=str(date + timedelta(days=1))
    )
    yield from bot.say("This feature is not available yet.")

bot.run(DATA['TOKEN'])