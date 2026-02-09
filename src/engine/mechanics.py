import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from content.initiatives.politics.coalition_crisis import CoalitionCrisisEvent
from content.initiatives.party.faction_schism import FactionSchismEvent
from content.events.historical.burning_convents import BurningConventsEvent

import random
import content.game_data as gd

# --- BASIC CALCULATIONS ---

def calculate_outcome(base_chance, modifiers, game_state):
    """
    Berechnet die Wahrscheinlichkeit und würfelt.
    Args:
        base_chance (int): Grundchance (0-100).
        modifiers (dict): Welche Stats beeinflussen das? 
                          z.B. {'public_order': 0.5} (Order hilft halb stark)
                          z.B. {'army_loyalty': -1.0} (Loyalty schadet voll)
        game_state (session_state): Damit wir auf die aktuellen Werte zugreifen können.
    Returns:
        success (bool): Hat es geklappt?
        roll (int): Was wurde gewürfelt?
        final_chance (int): Wie hoch war die Chance am Ende?
        breakdown (list): Text-Erklärung für den Tooltip (Warum war die Chance so?)
    """
    current_chance = base_chance
    breakdown = [f"Base Probability: {base_chance}%"]
    
    metrics = game_state.metrics
    
    for stat_key, weight in modifiers.items():
        if stat_key in metrics:
            val = metrics[stat_key]
            # > 50 helps, < 50 hurts
            deviation = val - 50
            effect = int(deviation * weight)
            
            if effect != 0:
                current_chance += effect
                sign = "+" if effect > 0 else ""
                breakdown.append(f"{sign}{effect}% due to {stat_key.replace('_', ' ').title()}")

    # Limitation: Immer min 5% Chance, max 95%
    final_chance = max(5, min(95, current_chance))

    roll = random.randint(1, 100)
    success = roll <= final_chance
    
    return success, roll, final_chance, breakdown

def calculate_election_results(game_state):
    """
    Simuliert die Wahl basierend auf den aktuellen Demographien.
    """
    # 1. Bevölkerungsgewichtung
    CLASS_WEIGHTS = {
        "aristocracy": 1,
        "clergy": 2,
        "bourgeoisie": 5,
        "workers_urban": 10,
        "workers_rural": 15,
        "soldiers": 3,
        "catalans": 4,  
        "basques": 2
    }
    
    demographics = game_state.election_demographics
    votes = {}

    # 2. Stimmen auszählen
    for group_name, weight in CLASS_WEIGHTS.items():
        # Parteipräferenzen (z.B. {PSOE: 0.6, DLR: 0.4})
        if group_name in demographics:
            preferences = demographics[group_name]
            
            for party_id, percentage in preferences.items():
                # Gewicht der Gruppe * Prozentanteil
                vote_share = weight * percentage
                
                # Zur Partei addieren
                if party_id not in votes:
                    votes[party_id] = 0
                votes[party_id] += vote_share

    # 3. Sitze verteilen (Proportional auf 470 Sitze)
    total_vote_points = sum(votes.values())
    total_parliament_seats = 470
    
    new_seats = {}
    
    # Debug Info
    print("--- ELECTION DEBUG ---")
    
    current_seat_sum = 0
    
    for party_id, score in votes.items():
        if total_vote_points > 0:
            share = score / total_vote_points
            seats = int(share * total_parliament_seats)
            new_seats[party_id] = seats
            current_seat_sum += seats
            print(f"{party_id}: {share:.2%} -> {seats} Seats")
    
    # 4. Rest-Sitze (Rundungsdifferenzen) an die Sieger verteilen oder "Others"
    remainder = total_parliament_seats - current_seat_sum
    if remainder > 0:
        if "others" not in new_seats:
            new_seats["others"] = 0
        new_seats["others"] += remainder
        
    return new_seats

# --- VOTER SHIFTING ---

def apply_demographic_vector(state, group_name, changes):
    """
    Wendet Änderungen an und gleicht den Rest automatisch aus.
    changes = {PARTY_ID: 0.05, OTHER_PARTY: -0.02}
    """
    if 'election_demographics' not in state: return
    demos = state.election_demographics
    if group_name not in demos: return
    
    preferences = demos[group_name]
    net_change = 0.0
    active_parties = []
    logs = []

    for party_id, amount in changes.items():
        if party_id not in preferences: preferences[party_id] = 0.0
        old_val = preferences[party_id]
        new_val = max(0.0, old_val + amount)
        actual_diff = new_val - old_val
        
        preferences[party_id] = new_val
        net_change += actual_diff
        active_parties.append(party_id)
        
        p_name = gd.PARTIES.get(party_id, gd.PARTIES["others"])['name']
        if abs(actual_diff) > 0.001:
            logs.append(f"{p_name} {actual_diff*100:+.1f}%")

    # 2. Ausgleich auf Passive Parteien
    passive_parties = [p for p in preferences if p not in active_parties]
    passive_sum = sum(preferences[p] for p in passive_parties)
    
    if passive_parties and abs(net_change) > 0.0001:
        if net_change > 0: # Vergabe des Überschusses
            if passive_sum > 0:
                for p in passive_parties:
                    share = preferences[p] / passive_sum
                    deduction = net_change * share
                    preferences[p] = max(0.0, preferences[p] - deduction)
        
        elif net_change < 0: # Verteilung des Überschusses
            gain_total = abs(net_change)
            if passive_sum > 0:
                 for p in passive_parties:
                    share = preferences[p] / passive_sum
                    preferences[p] += gain_total * share
            elif "others" in preferences:
                     preferences["others"] += gain_total

    # 3. Sicherheits-Normalisierung
    total = sum(preferences.values())
    if total != 0:
        for p in preferences: preferences[p] /= total
        
    if logs: return f"Shift in {group_name}: " + ", ".join(logs)
    return None

def update_voter_sentiment(state):
    """Nur Bestrafung bei Wut (<35). Kein Snowball."""
    if 'society' not in state: return
    
    gov_parties = state.government['coalition']
    
    # Drift target
    opposition_map = {
        "aristocracy": gd.PARTY_MON,
        "clergy": gd.PARTY_CEDA,
        "bourgeoisie": gd.PARTY_CEDA,
        "workers_urban": gd.PARTY_PCE, 
        "workers_rural": gd.PARTY_CNT,
        "soldiers": gd.PARTY_FAL
    }
    
    impact_reports = []

    for group, satisfaction in state.society.items():
        if group in state.election_demographics and satisfaction < 35:
            # 34 -> 0.1% Verlust. 0 -> 3.5% Verlust pro Monat.
            loss = (35 - satisfaction) / 1000
            target = opposition_map.get(group, gd.PARTY_MON)
            
            mech_msg = apply_demographic_vector(state, group, {target: loss})
            
            if loss > 0.005:
                impact_reports.append(f"{group.title()} unhappy: Opposition gains ground.")

    return impact_reports

# --- FACTIONS ---

def modify_faction_dissent(state, target_tag, amount):
    if 'my_factions' not in state:
        import copy
        state.my_factions = copy.deepcopy(gd.PARTIES[state.player_party]['factions'])

    affected_list = []
    
    for key, faction in state.my_factions.items():
        should_modify = False
        
        # Tag Matching Logik
        if target_tag == "all":
            should_modify = True
        elif target_tag == faction['tag']:
            should_modify = True
        elif target_tag.startswith("not_") and faction['tag'] != target_tag[4:]:
            should_modify = True
            
        if should_modify:
            # Dissent ändern (0 bis 100)
            old_val = faction['dissent']
            new_val = max(0, min(100, old_val + amount))
            faction['dissent'] = new_val
            
            diff = new_val - old_val
            if diff != 0:
                sign = "+" if diff > 0 else ""
                affected_list.append(f"{faction['name']} ({sign}{diff} Dissent)")
            
    return affected_list

def execute_faction_split(state, faction_key):
    """
    Entfernt Fration
    """
    if 'my_factions' not in state: return "Error: No factions found."

    factions = state.my_factions
    
    if faction_key not in factions:
        return "Error: Faction not found."

    leaving_faction = factions[faction_key]
    lost_strength = leaving_faction['strength']
    lost_name = leaving_faction['name']

    party_id = state.player_party
    current_members = gd.PARTIES[party_id]['members']
    members_lost = int(current_members * (lost_strength / 100))
    
    if 'party_members' not in state:
        state.party_members = current_members
    state.party_members -= members_lost

    del factions[faction_key]

    remaining_strength_sum = sum(f['strength'] for f in factions.values())

    if remaining_strength_sum > 0:
        factor = 100 / remaining_strength_sum
        
        recalc_details = []
        for f_key, f_data in factions.items():
            old_s = f_data['strength']
            new_s = round(old_s * factor, 1) # Runden
            f_data['strength'] = new_s
            recalc_details.append(f"{f_data['name']}: {old_s}% -> {new_s}%")
            
    else:
        # Partei ist leer (Game Over Szenario?)
        return f"The {lost_name} left, and no one remained. The party has collapsed."

    # Strafe für die Parteikasse
    state.economy['budget_int'] -= 3

    return f"The {lost_name} faction split! Lost {members_lost} members. Remaining factions expanded to fill the void."

# --- GOVERNMENT & PARLIAMENT ---

def calculate_parliament_vote(state, bill):
    """
    Berechnet das Wahlergebnis im Parlament. 
    Args:
        bill (dict): Enthält 'ideology' (-10 links bis +10 rechts), 'modifier', 'author_party'.
    """
    votes = {"yes": 0, "no": 0, "abstain": 0}
    details = [] # Wer hat wie gestimmt?

    ideology_target = bill.vote_config["ideology_target"]
    modifier = bill.vote_config.get("modifier", 0)
    author_party = bill.vote_config.get("author_party")

    coalition_stability = state.metrics["coalition_stability"]
    
    player_party = state.player_party
    
    for party_id, seats in state.parliament['seats'].items():
        if seats == 0: continue
        
        party_data = state.parties.get(party_id, gd.PARTIES['others'])
        
        # 1. Haltung berechnen (Score)
        # Startwert: Ideologische Distanz
        # Wenn Bill Ideologie = 2 (Links-Mitte) und Partei = 8 (Rechts): Distanz) = Penalty.
        dist = abs(party_data.get('ideology_index', 5) - bill["vote_config"]['ideology_target'])
        
        # Je größer die Distanz, desto niedriger der Score.
        # Max Distanz ist ca 10. 
        # Score geht von +50 (Perfektes Match) bis -50 (Gegenteil).
        score = 50 - (dist * 10)
        
        # 2. Modifikatoren
        # Eigene Partei stimmt meist zu.
        if party_id == player_party:
            score += 50
        elif party_id == bill.get('author_party'): # Koalitionspartner?
            score += 30
        
        # Relations-Check, abhängig von Beziehung zur Autorpartei.
        rel = party_data.get('relations', {}).get(bill.get('author_party'), 50)
        
        # Spezifischer Bill Modifier
        score += bill.get('modifier', 0)
        
        # 3. Stimmen verteilen
        # Sigmoid-artige Kurve oder simple Linearität
        # Score 50+ -> 100% Ja
        # Score 0   -> 50% Ja (Spaltung)
        # Score -50 -> 0% Ja
        
        yes_share = max(0.0, min(1.0, (score + 50) / 100))
        
        # - +/- 5% Abweichung
        import random
        wobble = random.uniform(-0.05, 0.05)
        yes_share = max(0.0, min(1.0, yes_share + wobble))
        
        yeas = int(seats * yes_share)
        nays = seats - yeas
        
        # Enthaltungen? (Wenn Score nahe 0 ist)
        if abs(score) < 15:
            abstentions = int(nays * 0.5) # Hälfte der Nein-Sager enthält sich eher
            nays -= abstentions
        else:
            abstentions = 0
            
        votes["yes"] += yeas
        votes["no"] += nays
        votes["abstain"] += abstentions
        
        # Log für den Spieler
        vote_str = f"{yeas} Y / {nays} N"
        if abstentions > 0: vote_str += f" / {abstentions} A"
        
        details.append({
            "party": party_data['name'],
            "color": party_data['color'],
            "text": vote_str,
            "score": score # Zum Debuggen des Scores
        })
        
    passed = votes["yes"] > votes["no"]
    return passed, votes, details

def remove_from_coalition(state, party_id):
    """Entfernt Partei und leert ihre Ministerien."""
    if party_id in state.government["coalition"]:
        state.government["coalition"].remove(party_id)
        
        for key, ministry in state.ministries.items():
            if ministry['party'] == party_id:
                vacate_ministry(state, key)
        
        state.metrics["coalition_stability"] -= 20
        
        # Falls Spielerpartei austritt (Spezialfall)
        if party_id == state.player_party:
            state.player_in_government = False
            
        return True
    return False

def get_coalition_seats(state):
    """Summiert die Sitze aller Koalitionsparteien."""
    seats = 0
    return sum(
        state.parliament["seats"].get(p, 0)
        for p in state.government["coalition"]
    )

def is_majority(state):
    total = sum(state.parliament["seats"].values())
    if total == 0: return True # Provisorische Regierung ohne Parlamentssitze
    return get_coalition_seats(state) > total // 2

def get_minister_for_event(state, ministry_key):
    """
    Prüft, wer für eine Entscheidung zuständig ist.
    
    Args:
        state: session_state
        ministry_key: z.B. 'interior', 'war', 'labor'
        
    Returns:
        dict: Infos über den Entscheidungsträger
    """
    ministry = state.ministries.get(ministry_key)
    holder_party_id = ministry['party']
    player_party_id = state.player_party
    
    is_player = (holder_party_id == player_party_id)
    
    minister_name = ministry['holder']
    party_name = gd.PARTIES[holder_party_id]['name']
    
    return {
        "is_player": is_player,
        "holder_name": minister_name,
        "holder_party": party_name,
        "party_id": holder_party_id
    }    

def vacate_ministry(state, ministry_key):
    """Setzt ein Ministerium zurück auf den Spieler (Interim)."""
    if ministry_key in state.ministries:
        state.ministries[ministry_key]['holder'] = "Vacant (Interim)"
        state.ministries[ministry_key]['party'] = state.player_party
        return True
    return False

def transfer_ministry_to_partner(state, target_party_id):
    """
    Nimmt dem Spieler ein Ministerium weg und gibt es der Zielpartei.
    Priorisiert 'unwichtigere' Ministerien zuerst, aber wenn nötig auch wichtige.
    """
    player_party = state.player_party
    
    # Welche Ministerien hält der Spieler aktuell?
    my_ministries = []
    for key, m in state.ministries.items():
        # Der Präsidenten-Posten (Head of Govt) ist meist tabu, außer man tritt zurück.
        # Wir nehmen an, den behält man.
        if m['party'] == player_party and key != "president":
            my_ministries.append(key)
    
    if not my_ministries:
        return None # Spieler hat nichts mehr zu geben!
    
    # Wir nehmen einfach das erste verfügbare (oder zufällig)
    # Besser: Wir könnten eine Prioritätenliste haben, aber random ist ok für den Start.
    ministry_key = random.choice(my_ministries)
    
    # Transfer
    state.ministries[ministry_key]['party'] = target_party_id
    state.ministries[ministry_key]['holder'] = f"Nominee of {gd.PARTIES[target_party_id]['name']}"
    
    return state.ministries[ministry_key]['name']

def modify_party_relation(state, source_party, target_party, amount):
    if 'parties' not in state: return
    
    s_party = state.parties.get(source_party)
    
    if s_party:
        current = s_party['relations'].get(target_party, 50)
        new_val = max(0, min(100, current + amount))
        s_party['relations'][target_party] = new_val
        
        p1 = s_party['name']
        p2 = state.parties.get(target_party, {'name': target_party})['name']
        sign = "+" if amount > 0 else ""
        return f"Relation: {p1} -> {p2} ({sign}{amount})"
        
    return None

def get_coalition_options(state):
    """
    Prüft, welche historischen Konstellationen eine Mehrheit haben.
    Gibt zurück:
    - options: Liste möglicher Koalitionen
    - status: 'formateur' (Du führst), 'partner' (Du wirst eingeladen), 'opposition' (Keine Chance)
    """
    seats = state.parliament['seats']
    total_seats = 470
    majority_thresh = 236
    player = state.player_party
    
    possible = []
    
    for template in gd.COALITION_DEFINITIONS:
        # 1. Sitze zählen
        current_seats = sum(seats.get(p, 0) for p in template['partners'])
        is_majority = current_seats >= majority_thresh
        
        # 2. Ist Spieler dabei?
        if player in template['partners']:
            # 3. Wer führt? (Größte Partei in der Koalition)
            # Sortiere Partner nach Sitzen
            sorted_partners = sorted(template['partners'], key=lambda x: seats.get(x, 0), reverse=True)
            leader = sorted_partners[0]
            
            is_leader = (leader == player)
            
            possible.append({
                "type": template,
                "seats": current_seats,
                "majority": is_majority,
                "is_leader": is_leader,
                "leader_id": leader
            })
            
    return possible

def initialize_ministry_draft(state, coalition_partners):
    """
    Bereitet den 'Draft' vor.
    Reihenfolge: Beliebtheit (Average Relations zu allen Partnern) + Sitzanzahl (Tiebreaker).
    """
    # 1. Draft Order berechnen
    scores = []
    for p in coalition_partners:
        # Score = Average Relation zu anderen Partnern + (Sitze / 10)
        rel_sum = 0
        others_count = 0
        p_data = gd.PARTIES.get(p, gd.PARTIES["others"])
        
        for other in coalition_partners:
            if other == p: continue
            rel = p_data.get('relations', {}).get(other, 50)
            rel_sum += rel
            others_count += 1
            
        avg_rel = rel_sum / max(1, others_count)
        seat_bonus = state.parliament['seats'].get(p, 0) / 5
        
        total_score = avg_rel + seat_bonus
        scores.append({'party': p, 'score': total_score})
        
    # Sortieren: Höchster Score zuerst
    sorted_parties = sorted(scores, key=lambda x: x['score'], reverse=True)
    draft_order = [x['party'] for x in sorted_parties]
    
    # State initialisieren
    return {
        "order": draft_order,
        "current_index": 0, # Wer ist dran? (Index in order)
        "round": 1,
        "available": list(state.ministries.keys()), # ['war', 'interior', ...]
        "assignments": {}, # 'war': {'party': 'psoe', 'holder': 'Caballero'}
        "finished": False
    }

def ai_pick_ministry(state, party_id, available_keys):
    """
    KI entscheidet, welches Ministerium sie will.
    """
    # 1. Präferenzen laden (aus PARTY_MINISTERS Keys oder Hardcoded Logic)
    preferences = gd.PARTY_MINISTERS.get(party_id, {}).keys()
    
    # 2. Prüfen was noch da ist
    wanted = [k for k in preferences if k in available_keys]
    
    picked_key = None
    if wanted:
        picked_key = wanted[0] # Nimm das Liebste zuerst
    else:
        # Nimm irgendeins (Priorität: Interior > War > Finance > Rest)
        priority = ['interior', 'war', 'finance', 'state', 'labor', 'agriculture', 'justice']
        for p in priority:
            if p in available_keys:
                picked_key = p
                break
                
    # Fallback
    if not picked_key and available_keys:
        picked_key = available_keys[0]
        
    # Name wählen
    candidates = gd.PARTY_MINISTERS.get(party_id, {}).get(picked_key, ["Party Technocrat"])
    import random
    holder_name = random.choice(candidates)
    
    return picked_key, holder_name

# --- MONTHLY TICK ---

def process_monthly_tick(state):
    state.date['month'] += 1
    if state.date['month'] > 12:
        state.date['month'] = 1
        state.date['year'] += 1
        
    # 2. Finanzen
    revenue = state.economy['tax_revenue_int']
    expenses = 4 
    state.economy['budget_int'] += (revenue - expenses)

    historical_id = None
    year = state.date['year']
    month = state.date['month']
    
    if year == 1931:
        if month == 4:
            historical_id = "1931_macia_declaration" 
        elif month == 5:
            historical_id = "1931_cardinal_segura"
        elif month == 6:
            historical_id = "1931_june_elections"
            
    if historical_id:
        return "Historical Event Imminent.", None, historical_id
    
    sentiment_logs = update_voter_sentiment(state)
    
    # 3. Das Land (Optional: Ernten etc. lassen wir erstmal weg)

    triggered_crisis = None
    
    # 2. MINORITY GOVERNMENT
    total_seats = sum(state.parliament['seats'].values())
    if total_seats > 0:
        gov_seats = get_coalition_seats(state)
        if gov_seats <= (total_seats // 2):
            if not state.government.get('is_minority', False):
                 triggered_crisis = {
                    "type": "minority_government",
                    "msg": "Warning: Minority Government."
                }
                 return "Month processed.", triggered_crisis

    # 3. EVENT CHECKER SYSTEM
    possible_events = [
        FactionSchismEvent(state),
        BurningConventsEvent(state),
        CoalitionCrisisEvent(state),
    ]
    
    for event in possible_events:
        if event.should_trigger():
            data = event.get_data()
            triggered_crisis = {
                "type": "event_trigger",
                "event_data": data
            }
            break

    return "Month processed.", triggered_crisis, None
