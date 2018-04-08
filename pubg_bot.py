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

description = """>>>>>Mr. Pubg-bot<<<<<
This bot will be your go-to pubg information buddy! Look at these neat commands:
All commands begin with "!"

"""
bot = commands.Bot(command_prefix='!', description=description)

DATA = json.load(open('bot_info.json'))
PUBG_CLIENT = PUBG(DATA["PUBG_API_KEY"], Shard.PC_NA)

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
            player = PUBG_CLIENT.players().filter(player_names=[ctx.subcommand_passed])
            player = player[0]
        except exceptions.NotFoundError:
            yield from bot.say('That player does not exist. Make sure the name is identical')
            return
        match_ids = pubg_utils.get_match_id(player.matches[:5])
        matches = PUBG_CLIENT.matches().filter(match_ids=match_ids)
        for idx, match in enumerate(matches):
            participant = pubg_utils.search_rosters(match.rosters, player)
            yield from bot.say("Game #" + str(idx) + ": Time Survived: " +  str(participant.stats['timeSurvived'])
                + " Place: " + str(participant.stats['winPlace']) + " Kills: " + str(participant.stats['kills']))

@matches.command(name='latest')
@asyncio.coroutine
def _latest(ign : str, name='latest-match'):
    """'latest <in-game name>. Will provide stats from the most recent match.'"""
    try:
        player = PUBG_CLIENT.players().filter(player_names=[ign])
        player = player[0]
    except exceptions.NotFoundError:
        yield from bot.say('That player does not exist. Make sure the name is identical')
        return
    match = PUBG_CLIENT.matches().get(player.matches[0].id)
    participant = pubg_utils.search_rosters(match.rosters, player)
    
    embed = discord.Embed(title=player.name + "'s Latest Match",
                colour=discord.Colour(14066432))

    embed.set_thumbnail(url="https://raw.githubusercontent.com/pubg/api-assets/master/assets/weapons/Item_Weapon_Pan.png")
    embed.set_footer(text="Donations")
    
    embed.add_field(name="Match Data", value="Game Mode: " + match.game_mode + 
            "\nTime: " + pubg_utils.friendly_match_time(match) + "\nDuration: "
            + pubg_utils.friendly_match_duration(match.duration), inline=False)
    embed.add_field(name="Player Stats", value=pubg_utils.build_player_game_stats(participant), inline=False)

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