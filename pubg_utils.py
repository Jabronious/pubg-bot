
def search_rosters(rosters, player):
    for i in range(0, len(rosters)):
        for k in range(0, len(rosters[i].participants)):
            if rosters[i].participants[k].player_id == player.id:
                return rosters[i].participants[k]

def get_last_five_matches(matches, client):
    match_arr = []
    for match in matches:
        match_arr.append(client.matches().get(match.id))
    return match_arr