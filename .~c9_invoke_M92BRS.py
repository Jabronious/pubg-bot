import discord
import asyncio
import json
import pdb
import requests
from discord.ext import commands
from pubg_python import PUBG, Shard, exceptions
import bot_utils
import sys
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

@bot.event
@asyncio.coroutine
def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    # Test server channel, '#general,' will receive the message.
    # Thought this best to not blow people up if the bot isnt working and
    # we need to restart it a lot.
    channel = bot.get_channel('422922120608350210')
    yield from bot.send_message(channel, "I was restarted. Don't worry though... I'm back up and running!")

def reset_pubg_client_shard():
    PUBG_CLIENT.shard = Shard.PC_NA

##################################
#                                #
#                                #
#        Matches commands        #
#                                #
#                                #
##################################
@bot.group(pass_context=True)
@commands.cooldown(rate=3, per=10.0, type=commands.BucketType.user)
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

        #displays a list of matches
        emoji_list = bot_utils.get_random_emoji_list()
        for idx, match in enumerate(player.matches[:len(emoji_list)]):
            match_dict[emoji_list[idx]] = match.id
            embed.add_field(name=emoji_list[idx] + ': ', value=match.id, inline=False)
        yield from bot.say(embed=embed)

        logging.info(">>>>>>>>>>>>>waiting for reaction from %s<<<<<<<<<<<<<<<<<<<", ctx.message.author)
        res = yield from bot.wait_for_reaction(user=ctx.message.author, timeout=20000) #Waits for 10000ms (maybe?) for a user to react.
        logging.info("reaction occurred from %s", ctx.message.author)

        match = PUBG_CLIENT.matches().get(match_dict[res.reaction.emoji]) #splits message and pulls id
        
        yield from bot.say("Let me get " + match_dict[res.reaction.emoji] + " match's data.")
        embed = bot_utils.build_embed_message(match, player, PUBG_CLIENT, False)
        yield from bot.say(embed=embed)

@matches.command(name='last', pass_context=True)
@commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
@asyncio.coroutine
def _last(ctx, ign : str, number_of_matches : int, *shard : str):
    """'EX: <!matches last Jabronious 10> - This will provide 10 matches for Jabronious
    """
    if shard:
        PUBG_CLIENT.shard = Shard(shard[0])

    try:
        logging.info(">>>>>>>>>>>>>searching for player %s<<<<<<<<<<<<<<<<<<<", ign)
        player = PUBG_CLIENT.players().filter(player_names=[ign])
        player = player[0]
        logging.info(">>>>>>>>>>>>>player found<<<<<<<<<<<<<<<<<<<")
    except exceptions.NotFoundError:
        yield from bot.say('That player does not exist. Make sure the name is identical')
        return

    match_dict = {}
    logging.info(">>>>>>>>>>>>>printing " + str(number_of_matches) + " matches<<<<<<<<<<<<<<<<<<<")
    embed = discord.Embed(title="React to the match you wish to see data for:",
                            colour=discord.Colour(14066432))

    #displays a list of matches
    emoji_list = bot_utils.get_random_emoji_list(number_of_matches)
    for idx, match in enumerate(player.matches[:len(emoji_list)]):
        match_dict[emoji_list[idx]] = match.id
        embed.add_field(name=emoji_list[idx] + ': ', value=match.id, inline=False)
    yield from bot.say(embed=embed)

    logging.info(">>>>>>>>>>>>>waiting for reaction from %s<<<<<<<<<<<<<<<<<<<", ctx.message.author)
    res = yield from bot.wait_for_reaction(user=ctx.message.author, timeout=20000) #Waits for 10000ms (maybe?) for a user to react.
    logging.info("reaction occurred from %s", ctx.message.author)

    match = PUBG_CLIENT.matches().get(match_dict[res.reaction.emoji]) #splits message and pulls id

    yield from bot.say("Let me get " + match_dict[res.reaction.emoji] + " match's data.")
    embed = bot_utils.build_embed_message(match, player, PUBG_CLIENT, False)
    reset_pubg_client_shard()
    yield from bot.say(embed=embed)

@matches.command(name='latest', pass_context=True)
@commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
@asyncio.coroutine
def _latest(ctx, ign : str, *shard : str, name='latest'):
    """'latest <in-game name>. Will provide stats from the most recent match.'"""
    if shard:
        PUBG_CLIENT.shard = Shard(shard[0])

    try:
        logging.info(">>>>>>>>>>>>>searching for player %s, subcommand: %s<<<<<<<<<<<<<<<<<<<", ign, ctx.subcommand_passed)
        player = PUBG_CLIENT.players().filter(player_names=[ign])
        player = player[0]
        logging.info(">>>>>>>>>>>>>player found<<<<<<<<<<<<<<<<<<<")
    except exceptions.NotFoundError:
        yield from bot.say('That player does not exist. Make sure the name is identical')
        return
    match = PUBG_CLIENT.matches().get(player.matches[0].id)
    
    yield from bot.say("Let me get that match's data.")
    embed = bot_utils.build_embed_message(match, player, PUBG_CLIENT)
    reset_pubg_client_shard()
    yield from bot.say(embed=embed)

@matches.command(name='date', pass_context=True)
@asyncio.coroutine
def _date(ctx, ign : str, *date : int):
    #TODO: ADD LOGGING
    """'date <in-game name> <date> : Format the MM DD YYYY EX: 04 03 2018'"""
    date = datetime(year=date[2], month=date[1], day=date[0])
    matches = PUBG_CLIENT.matches().filter(
        created_at_start=str(date),
        created_at_end=str(date + timedelta(days=1))
    )
    yield from bot.say("This feature is not available yet.")

##################################
#                                #
#                                #
#         Shard Commands         #
#                                #
#                                #
##################################
@bot.command(name='shards', pass_context=True)
@asyncio.coroutine
def list_shards(name='shards'):
    """
    This will list all the available shards
    """
    embed = discord.Embed(title="Shards:", colour=discord.Colour(14066432))
    embed.set_footer(text="Donations")
    for idx, shard in enumerate(Shard):
        embed.add_field(name=str(idx + 1) + ": ", value=shard.value, inline=True)
    yield from bot.say(embed=embed)

##################################
#                                #
#                                #
#         Update Commands        #
#                                #
#                                #
##################################
@bot.command(pass_context=True)
@asyncio.coroutine
def whatsnew(ctx):
    """
    Displays all the new stuff we added!
    """
    embed = discord.Embed(title="Updates:", colour=discord.Colour(14066432))
    embed.set_footer(text="Donations")
    embed.add_field(name="**__New Updates__**", value="---------")
    embed.add_field(name="**Region/Platform Selection:**",
        value="For matches' subcommands 'latest' and 'last' you can type a platform and region to look for matches now (Ex: '!matches latest Jabronious pc-na'). "
        + "Find the list of shards using !shards")
    embed.add_field(name="**__Recent Updates__**", value="---------")
    embed.add_field(name="**Cooldowns:**", value="Matches' commands will have cooldowns now. If you exceed them they will tell how long you have to wait.")
    embed.add_field(name="**Showing Updates:**", value="This too is a new command that can help keep you updated on things that new to the bot!")
    yield from bot.say(embed=embed)

##################################
#                                #
#                                #
#            Errors              #
#                                #
#                                #
##################################
@matches.error
@_latest.error
@_last.error
@asyncio.coroutine
def matches_error(error, ctx):
    logging.debug('***********Invoked Command: ' + ctx.invoked_with + ", Invoked Subcommand: " + str(ctx.invoked_subcommand) + "(" + ctx.subcommand_passed + "), "
                    + "Error: " + str(error) + ", Message author: " + ctx.message.author.name + ", Message: " + ctx.message.content + "***********")
    if type(error) == discord.ext.commands.errors.CommandOnCooldown:
        yield from bot.say(str(error))
    else:
        yield from bot.say("Something Happened, OH NO!! Don't worry, you just need to make sure you have entered the command correctly " +
            "or the player's in-game name is identical.")

##################################
#                                #
#                                #
#        Admin commands          #
#                                #
#                                #
##################################
@bot.command(pass_context=True, hidden=True)
@asyncio.coroutine
def restart(ctx):
    message = ctx.message
    logging.info("Restart >>>INITIATED<<< in server(" + message.author.server.name + ") by " + message.author.name)
    # This will only work for Test Server and Jabronious/burnNturn3 users
    if message.author.server.id == '422922120608350208' and message.author.id == '304806386536153088' or message.author.id == '176648415428476930':
        yield from bot.send_message(message.channel, 'Restarting')
        logging.info("Restart >>>SUCCESSFUL<<< in server(" + message.author.server.name + ") by " + message.author.name)
        python = sys.executable
        os.execl(python, python, * sys.argv)
    logging.info("Restart >>>FAILED<<< in server(" + message.author.server.name + ") by " + message.author.name)

bot.run(DATA['TOKEN'])