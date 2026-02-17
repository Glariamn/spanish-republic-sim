import content.game_data as gd
import random

def remove_from_coalition(state, party_id):
    if party_id in state.government["coalition"]:
        state.government["coalition"].remove(party_id)
        for key, ministry in state.ministries.items():
            if ministry['party'] == party_id:
                vacate_ministry(state, key)
        state.metrics["coalition_stability"] -= 20
        if party_id == state.player_party:
            state.player_in_government = False
        return True
    return False

def get_coalition_seats(state):
    return sum(state.parliament["seats"].get(p, 0) for p in state.government["coalition"])

def is_majority(state):
    total = sum(state.parliament["seats"].values())
    if total == 0: return True 
    return get_coalition_seats(state) > total // 2

def get_minister_for_event(state, ministry_key):
    ministry = state.ministries.get(ministry_key)
    return {
        "is_player": (ministry['party'] == state.player_party),
        "holder_name": ministry['holder'],
        "holder_party": gd.PARTIES[ministry['party']]['name'],
        "party_id": ministry['party']
    }    

def vacate_ministry(state, ministry_key):
    if ministry_key in state.ministries:
        state.ministries[ministry_key]['holder'] = "Vacant (Interim)"
        state.ministries[ministry_key]['party'] = state.player_party
        return True
    return False

def transfer_ministry_to_partner(state, target_party_id):
    my_mins = [k for k, m in state.ministries.items() if m['party'] == state.player_party and k != "president"]
    if not my_mins: return None
    key = random.choice(my_mins)
    state.ministries[key]['party'] = target_party_id
    state.ministries[key]['holder'] = f"Nominee of {gd.PARTIES[target_party_id]['name']}"
    return state.ministries[key]['name']

def get_coalition_options(state):
    seats = state.parliament['seats']
    total_seats = 470
    majority_thresh = 236
    player = state.player_party
    possible = []
    
    for template in gd.COALITION_DEFINITIONS:
        current_seats = sum(seats.get(p, 0) for p in template['partners'])
        is_majority = current_seats >= majority_thresh
        
        if player in template['partners']:
            sorted_partners = sorted(template['partners'], key=lambda x: seats.get(x, 0), reverse=True)
            leader = sorted_partners[0]
            possible.append({
                "type": template, "seats": current_seats, "majority": is_majority,
                "is_leader": (leader == player), "leader_id": leader
            })
    return possible

def initialize_ministry_draft(state, coalition_partners):
    scores = []
    for p in coalition_partners:
        p_data = gd.PARTIES.get(p, gd.PARTIES["others"])
        rel_sum = 0
        others_count = 0
        for other in coalition_partners:
            if other == p: continue
            rel = p_data.get('relations', {}).get(other, 50)
            rel_sum += rel
            others_count += 1
        avg_rel = rel_sum / max(1, others_count)
        seat_bonus = state.parliament['seats'].get(p, 0) / 5
        scores.append({'party': p, 'score': avg_rel + seat_bonus})
        
    sorted_parties = sorted(scores, key=lambda x: x['score'], reverse=True)
    draft_order = [x['party'] for x in sorted_parties]
    
    return {
        "order": draft_order, "current_index": 0, "round": 1,
        "available": list(state.ministries.keys()), 
        "assignments": {}, "finished": False
    }

def ai_pick_ministry(state, party_id, available_keys):
    preferences = gd.PARTY_MINISTERS.get(party_id, {}).keys()
    wanted = [k for k in preferences if k in available_keys]
    picked_key = wanted[0] if wanted else (available_keys[0] if available_keys else None)
    
    if not picked_key: return None, None
        
    candidates = gd.PARTY_MINISTERS.get(party_id, {}).get(picked_key, ["Party Technocrat"])
    holder_name = random.choice(candidates)
    return picked_key, holder_name