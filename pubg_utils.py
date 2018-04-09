from pubg_python.domain.telemetry.events import LogPlayerKill, LogPlayerTakeDamage
from datetime import datetime
from weapons_url import weapons_url_dict
import pdb

def search_rosters(rosters, player):
    for i in range(0, len(rosters)):
        for k in range(0, len(rosters[i].participants)):
            if rosters[i].participants[k].player_id == player.id:
                return rosters[i].participants[k]

def get_match_id(matches):
    match_arr = []
    for match in matches:
        match_arr.append(match.id)
    return match_arr

def friendly_match_duration(duration):
    return str(int(duration / 60)) + ":" + str(duration % 60)

def friendly_match_time(match):
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

def get_weapon_img_url(events, ign):
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