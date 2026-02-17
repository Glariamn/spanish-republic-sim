import content.game_data as gd
import copy

def modify_faction_dissent(state, changes):
    if 'my_factions' not in state: return

    # A) TAGS
    if "tag" in changes and "amount" in changes:
        target_tag = changes["tag"]
        amount = changes["amount"]
        
        for key, faction in state.my_factions.items():
            faction_tags = faction.get('tags', [])
            should_modify = False
            
            if target_tag == "all": should_modify = True
            elif target_tag.startswith("not_"):
                if target_tag[4:] not in faction_tags: should_modify = True
            elif target_tag in faction_tags: should_modify = True

            if should_modify:
                faction['dissent'] = max(0, min(100, faction['dissent'] + amount))

    # B) KEYS
    else:
        for key, amount in changes.items():
            if key in state.my_factions:
                state.my_factions[key]['dissent'] = max(0, min(100, state.my_factions[key]['dissent'] + amount))

def execute_faction_split(state, faction_key):
    if 'my_factions' not in state: return "Error."
    factions = state.my_factions
    if faction_key not in factions: return "Error."

    leaving = factions[faction_key]
    
    # Mitglieder
    if 'party_members' not in state: # Init fallback
        state.party_members = gd.PARTIES[state.player_party]['members']
        
    members_lost = int(state.party_members * (leaving['strength'] / 100))
    state.party_members -= members_lost
    del factions[faction_key]

    # Recalculate
    rem_sum = sum(f['strength'] for f in factions.values())
    if rem_sum > 0:
        factor = 100 / rem_sum
        for f in factions.values(): f['strength'] = round(f['strength'] * factor, 1)
            
    state.economy['budget_int'] -= 3
    return f"{leaving['name']} split! Lost {members_lost} members."

def modify_party_relation(state, source_party, target_party, amount):
    if 'parties' not in state: return
    s_party = state.parties.get(source_party)
    if s_party:
        current = s_party['relations'].get(target_party, 50)
        s_party['relations'][target_party] = max(0, min(100, current + amount))
        
        p1 = s_party['name']
        p2 = state.parties.get(target_party, {'name': target_party})['name']
        sign = "+" if amount > 0 else ""
        return f"Relation: {p1} -> {p2} ({sign}{amount})"
    return None