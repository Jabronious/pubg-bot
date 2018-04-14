from pubg_python.domain.telemetry.events import LogPlayerKill, LogPlayerTakeDamage
from datetime import datetime
from weapons_url import weapons_url_dict
import pdb
import discord
import logging

logging.basicConfig(filename='debug.log',level=logging.DEBUG, format='%(asctime)s %(message)s')

def search_rosters(rosters, player):
    """
    Iterates through a roster list to find a player and will return the participant.
    
    rosters: a list of roster objects
    
    player: a player object
    """
    for i in range(0, len(rosters)):
        for k in range(0, len(rosters[i].participants)):
            if rosters[i].participants[k].player_id == player.id:
                return rosters[i].participants[k]

def get_match_id(matches):
    """
    This will accept a list of matches and return their ids in an array.This
    This can have match objects sent in an array via player.matches generally.
    """
    match_arr = []
    for match in matches:
        match_arr.append(match.id)
    return match_arr

def friendly_match_duration(duration):
    """
    Accepts an int, which should be found via match.duration, and returns a 
    string for the user friendly time of a match.
    
    EX: 34:50
    """
    return str(int(duration / 60)) + ":" + str(duration % 60)

def friendly_match_time(match):
    """
    This will accept a match object and then return a string of a user
    friendly time.
    """
    date = datetime(year=int(match.created_at[0:4]), month=int(match.created_at[5:7]), day=int(match.created_at[8:10]), hour=int(match.created_at[11:13]), minute=int(match.created_at[14:16]))
    return date.strftime("%b %d %Y at %-I:%M %p")

def build_player_game_stats(participant):
    return ("**Knocks:** " + str(participant.dbnos)
            + "\n**Win Place:** " + str(participant.win_place)
            + "\n**Kill:** " + str(participant.kills)
            + "\n**Headshots(kills):** " + str(participant.headshot_kills)
            + "\n**Damage Dealt:** " + str(participant.damage_dealt)
            + "\n**Longest Kill:** " + str(participant.longest_kill)
            + "\n**Distance Travelled:** " + str((participant.walk_distance + participant.ride_distance))
            + "\nAssists: " + str(participant.assists)
            + "\nBoosts: " + str(participant.boosts)
            + "\nDeath Type: " + str(participant.death_type)
            + "\nHeals: " + str(participant.heals)
            + "\nPlace(base on kills): " + str(participant.kill_place)
            + "\nKill Points: " + str(participant.kill_points_delta)
            + "\nKill Streaks: " + str(participant.kill_streaks)
            + "\nLast Kill Points: " + str(participant.last_kill_points)
            + "\nLast Win Points: " + str(participant.last_win_points)
            + "\nMost Damage: " + str(participant.most_damage)
            + "\nRevives: " + str(participant.revives)
            + "\nRoad Kills: " + str(participant.road_kills)
            + "\nTeam Kills: " + str(participant.team_kills)
            + "\nTime Survived: " + str(participant.time_survived)
            + "\nVehicles Destroyed: " + str(participant.vehicle_destroys)
            + "\nWeapons Acquired: " + str(participant.weapons_acquired)
            + "\nWin Points: " + str(participant.win_points_delta))

def build_embed_message(match, player, client, latest_match=True):
    """
    This method will create an embedded message that will be returned.
    
    match: should be a PUBG_CLIENT.matches() that is passed.
    
    player: should be a PUBG_CLIENT.player()
    
    client: should be a PUBG_CLIENT object
    
    latest_match: default True, but pass False if this is going to be a match
    that isnt the most recent.
    """
    if latest_match:
        title = player.name + "'s Latest Match"
    else:
        title = player.name + "'s Match"

    embed = discord.Embed(title=title, colour=discord.Colour(14066432))
    logging.info("telemtry data begins for %s", player.name)
    tel = client.telemetry(match.assets[0].url)
    logging.info("telemtry data set for %s", player.name)

    participant = search_rosters(match.rosters, player)

    embed.set_thumbnail(url=get_weapon_img_url(tel.events, player.name))
    embed.set_footer(text="Donations")
    embed.add_field(name="Match Data", value="Game Mode: " + match.game_mode + 
            "\nTime: " + friendly_match_time(match) + "\nDuration: "
            + friendly_match_duration(match.duration), inline=False)
    embed.add_field(name="Player Stats", value=build_player_game_stats(participant), inline=False)
    
    return embed

def get_weapon_img_url(events, ign):
    """
    This method accepts a telemetry events array and an in game name then iterates to 
    find all events where the in game name was the attacker. It then populates a
    weapon_dmg_dict with the various weapons that was the causer of damage and 
    then find ths weapon with the most dmg and returns it's image url.and
    
    events: this should be an entire list of telemetry events
    
    ign: a string of an exact PUBG_CLIENT.player name. player.name should generally be used
    to ensure accuracy
    """
    attacker_events = []
    for event in events:
        if type(event) == LogPlayerTakeDamage and event.attacker.name == ign:
            attacker_events.append(event)

    weapon_dmg_dict = {}
    for attack_event in attacker_events:
        if attack_event.damage_causer_name in weapon_dmg_dict:
            weapon_dmg_dict[attack_event.damage_causer_name] += attack_event.damage
        else:
            weapon_dmg_dict[attack_event.damage_causer_name] = attack_event.damage

    sorted_keys = sorted(weapon_dmg_dict, key=weapon_dmg_dict.get)

    try:
        return weapons_url_dict[sorted_keys[len(sorted_keys)-1]]
    except:
        return weapons_url_dict["Apple"]