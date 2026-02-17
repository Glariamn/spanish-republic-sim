import content.game_data as gd
import random

def calculate_parliament_vote(state, bill):
    votes = {"yes": 0, "no": 0, "abstain": 0}
    details = [] 
    player_p = state.player_party
    
    for party_id, seats in state.parliament['seats'].items():
        if seats == 0: continue
        party_data = state.parties.get(party_id, gd.PARTIES['others'])
        
        dist = abs(party_data.get('ideology_index', 5) - bill["vote_config"]['ideology_target'])
        score = 50 - (dist * 10)
        
        if party_id == player_p: score += 50
        elif party_id == bill.get('author_party'): score += 30
        
        rel = party_data.get('relations', {}).get(bill.get('author_party'), 50)
        if rel < 30: score -= 20
        if rel > 70: score += 10
        score += bill.get('modifier', 0)
        
        yes_share = max(0.0, min(1.0, (score + 50) / 100))
        yes_share = max(0.0, min(1.0, yes_share + random.uniform(-0.05, 0.05)))
        
        yeas = int(seats * yes_share)
        nays = seats - yeas
        
        votes["yes"] += yeas
        votes["no"] += nays
        details.append({"party": party_data['name'], "color": party_data['color'], "text": f"{yeas} Y / {nays} N"})
        
    return (votes["yes"] > votes["no"]), votes, details

def calculate_confidence_vote(state):
    votes = {"yes": 0, "no": 0, "abstain": 0}
    gov_parties = state.government['coalition']
    
    for p_id in gov_parties:
        votes['yes'] += state.parliament['seats'].get(p_id, 0)
        
    for p_id, seats in state.parliament['seats'].items():
        if p_id not in gov_parties:
            votes['no'] += seats
            
    stability_mod = state.metrics['coalition_stability'] / 100.0 
    rebels = int(votes['yes'] * (1 - stability_mod) * 0.2) 
    votes['yes'] -= rebels
    votes['no'] += rebels
    
    return (votes['yes'] > votes['no']), votes