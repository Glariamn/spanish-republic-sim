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
    # president_republic is filled by the presidential election mechanic, never vacated to player
    if ministry_key == "president_republic":
        return False
    if ministry_key in state.ministries:
        state.ministries[ministry_key]['holder'] = "Vacant (Interim)"
        state.ministries[ministry_key]['party'] = state.player_party
        return True
    return False

def transfer_ministry_to_partner(state, target_party_id):
    my_mins = [k for k, m in state.ministries.items() if m['party'] == state.player_party and k != "prime_minister"]
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
    coalition_seats = sum(state.parliament["seats"].get(p, 0) for p in coalition_partners)
    SEAT_THRESHOLD = max(5, int(coalition_seats * 0.08))

    pre_assignments = {}
    # president_republic is filled by presidential election, never drafted
    # prime_minister is filled by PM nomination investiture, never drafted
    excluded = {"president_republic", "prime_minister"}
    available = [k for k in state.ministries.keys() if k not in excluded]
    
    # --- 2. MINISTROS (Ministers) ---
    def qualifies(p):
        if p == state.player_party: return True
        if p not in gd.PARTY_MINISTERS: return False
        if p == gd.PARTY_DLR: return False  # Already handled via pre-assignment
        return state.parliament["seats"].get(p, 0) >= SEAT_THRESHOLD
    
    major_partners = [p for p in coalition_partners if qualifies(p)]

    # --- 3. PRESIDENTE DEL GOBIERNO (Prime Minister) ---
    # Goes to the largest party weighted by institutionalization — reflecting willingness
    # to lead. (Historically PSOE refused the PM role in 1931 despite having most seats.)
    # The player always gets PM if they are the largest qualifying party.
    if "prime_minister" in available and major_partners:
        def pm_score(p):
            seats = state.parliament["seats"].get(p, 0)
            inst = gd.PARTIES.get(p, {}).get("institutionalization", 50)
            # Player gets a strong bonus so they lead their own coalition
            return (seats * inst / 100)

        pm_party = max(major_partners, key=pm_score)
        candidates = gd.PARTY_MINISTERS.get(pm_party, {}).get("prime_minister", ["Party Leader"])
        pre_assignments["prime_minister"] = {"party": pm_party, "holder": candidates[0]}
        available.remove("prime_minister")
        # PM party still picks more ministries in the draft — don't remove from major_partners

    # --- 4. DRAFT ORDER: by seats, weighted by coalition relations ---
    scores = []
    for p in major_partners:
        p_data = gd.PARTIES.get(p, gd.PARTIES["others"])
        rel_sum = sum(p_data.get("relations", {}).get(other, 50)
                      for other in major_partners if other != p)
        avg_rel = rel_sum / max(1, len(major_partners) - 1)
        seat_share = state.parliament["seats"].get(p, 0) / max(1, coalition_seats)
        scores.append({"party": p, "score": avg_rel + (seat_share * 100)})

    sorted_parties = sorted(scores, key=lambda x: x["score"], reverse=True)
    draft_order = [x["party"] for x in sorted_parties]
    
    return {
        "order": draft_order, "current_index": 0, "round": 1,
        "available": available,
        "assignments": pre_assignments, "finished": False
    }

def ai_pick_ministry(state, party_id, available_keys):
    party_data = state.parties.get(party_id, {})
    preferences = party_data.get("preferred_portfolios", [])
    wanted = [k for k in preferences if k in available_keys]
    picked_key = None
    if wanted:
        picked_key = wanted[0]
    else:
        priority = ['interior', 'war', 'finance', 'state', 'labor', 'agriculture', 'justice']
        for p in priority:
            if p in available_keys:
                picked_key = p
                break
    
    if not picked_key: return None, None
        
    candidates = gd.PARTY_MINISTERS.get(party_id, {}).get(picked_key, ["Party Technocrat"])
    holder_name = random.choice(candidates)
    return picked_key, holder_name