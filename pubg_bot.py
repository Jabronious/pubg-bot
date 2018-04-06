import discord
import asyncio
import json
import pdb
import requests
from discord.ext import commands
from pubg_python import PUBG, Shard, exceptions
import pubg_utils
import os

description = """>>>>>Mr. Pubg-bot<<<<<
This bot will be your go-to pubg information buddy! Look at these neat commands:
All commands should begin with "!"

"""
bot = commands.Bot(command_prefix='!', description=description)

"""
This will change depending on whether it is passed to master
or not for heroku
"""

#DATA = json.load(open('bot_info.json'))
#PUBG_CLIENT = PUBG(DATA["PUBG_API_KEY"], Shard.PC_NA)
PUBG_CLIENT = PUBG(os.environ["PUBG_API_KEY"], Shard.PC_NA)
PUBG_URL = "https://api.playbattlegrounds.com/shards/pc-na/"

@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command()
@asyncio.coroutine
def latest_match(ign : str, name='latest-match'):
    """type !latest-match <in-game name>. Will provide stats from the most recent match.
    
    """
    try:
        player = PUBG_CLIENT.players().filter(player_names=[ign])
        player = player[0]
    except exceptions.NotFoundError:
        yield from bot.say('That player does not exist. Make sure the name is identical')
        return
    match = PUBG_CLIENT.matches().get(player.matches[0].id)
    participant = pubg_utils.search_rosters(match.rosters, player)
    yield from bot.say(participant.stats)

@bot.group(pass_context=True)
@asyncio.coroutine
def matches(ctx, ign : str):
    """Provides match data for the last 5 matches for the in-game name provided.
    By providing a date it will get all matches that day.
    """
    if ctx.invoked_subcommand is None:
        try:
            player = PUBG_CLIENT.players().filter(player_names=[ign])
            player = player[0]
        except exceptions.NotFoundError:
            yield from bot.say('That player does not exist. Make sure the name is identical')
            return
        #needs to format the most 5 most recent matches
        match_ids = pubg_utils.get_match_id(player.matches[:5])
        matches = PUBG_CLIENT.matches().filter(match_ids=match_ids)
        for idx, match in enumerate(matches):
            participant = pubg_utils.search_rosters(match.rosters, player)
            yield from bot.say("Game #" + idx +" - Time Survived: " +  participant.timeSurvived
                + " Place: " + participant.winPlace + " Kills: " + participant.kills)

@matches.error
@asyncio.coroutine
def ign_error(error, ctx):
    yield from bot.say("You need to put a player's in-game name")

@matches.command(name='date')
@asyncio.coroutine
def _date(*date : str):
    """Format the MM DD YYYY EX: 04 03 2018"""
    yield from bot.say('Yes, the bot is cool.')

"""
This will change depending on whether it is passed to master
or not for heroku
"""
bot.run(os.environ["TOKEN"])
#bot.run(DATA['TOKEN'])