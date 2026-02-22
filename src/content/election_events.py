import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import engine.mechanics as mech
import content.game_data as gd

def analyze_election_outcome(state):
    """Erstellt einen dynamischen Text basierend auf der Sitzverteilung."""
    seats = state.parliament['seats']
    total = sum(seats.values())
    if total == 0: return "No results yet."
    
    # Blöcke definieren
    left_bloc = [gd.PARTY_PSOE, gd.PARTY_AR, gd.PARTY_PRRS, gd.PARTY_ERC, gd.PARTY_PCE]
    right_bloc = [gd.PARTY_CEDA, gd.PARTY_MON, gd.PARTY_PA, gd.PARTY_FAL, gd.PARTY_LLIGA]
    center_bloc = [gd.PARTY_PRR, gd.PARTY_DLR, gd.PARTY_PNV]
    
    left_seats = sum(seats.get(p, 0) for p in left_bloc)
    right_seats = sum(seats.get(p, 0) for p in right_bloc)
    center_seats = sum(seats.get(p, 0) for p in center_bloc)
    
    winner_id = max(seats, key=seats.get)
    winner_name = gd.PARTIES[winner_id]['name']
    
    text = f"**The votes are counted.**\n\nThe **{winner_name}** has emerged as the largest single party. "
    
    if left_seats > 235:
        text += "The Left has secured an absolute majority. The streets are celebrating the triumph of the Republic."
    elif right_seats > 235:
        text += "The Right has swept the polls. The 'Black Two Years' seem imminent."
    elif center_seats > 150:
        text += "The Center holds the balance of power. No government can form without them."
    else:
        text += "The parliament is deadlocked. The President of the Republic is frantically consulting with party leaders."
        
    return text

def get_event_general_election(state):
    # 1. Mögliche Koalitionen berechnen
    opts = mech.get_coalition_options(state)
    
    # 2. Text generieren
    intro_text = analyze_election_outcome(state)
    
    choices = []
    
    # 3. Optionen generieren
    
    # A) Mehrheits-Koalitionen (Historisch definiert)
    for opt in opts:
        coalition_name = opt['type']['name']
        seats = opt['seats']
        partners = opt['type']['partners']
        
        # Fall 1: Wir führen die Koalition an
        if opt['is_leader']:
            choices.append({
                "text": f"Accept Mandate: {coalition_name} ({seats} Seats)",
                "tooltip": "Form a majority government. High Stability.",
                "success": {
                    "msg": f"President Alcalá-Zamora entrusts you with forming the government. Negotiations begin.",
                    "effects": {
                        "set_coalition": partners,
                        "start_pm_nomination": True,
                        "coalition_stability": 20 # Start-Bonus
                    }
                }
            })
            
        # Fall 2: Wir sind Junior-Partner
        elif opt['majority']: 
             leader_id = opt['leader_id']
             leader_name = gd.PARTIES[leader_id]['name']
             choices.append({
                "text": f"Join Coalition led by {leader_name} ({seats} Seats)",
                "tooltip": "Join as a junior partner. You will have less influence over ministries.",
                "success": {
                    "msg": f"We have agreed to support the {leader_name}. The portfolio distribution begins.",
                    "effects": {
                        "set_coalition": partners,
                        "start_pm_nomination": True,
                        "modify_faction": {"tag": "radical", "amount": 10} # Radikale mögen es nicht, Junior zu sein
                    }
                }
            })
    
    # B) Minderheitsregierung (Falls wir die größte Partei sind, aber keine Koalition passt)
    player_seats = state.parliament['seats'].get(state.player_party, 0)
    largest_party_id = max(state.parliament['seats'], key=state.parliament['seats'].get)
    
    if state.player_party == largest_party_id and not any(o['is_leader'] for o in opts):
        choices.append({
            "text": "Attempt Minority Government",
            "tooltip": "Risky! You have no majority. Stability will start very low.",
            "success": {
                "msg": "The President reluctantly asks you to govern alone until a majority can be found.",
                "effects": {
                    "set_coalition": [state.player_party],
                    "start_negotiation": True, # Du verteilst Ministerien nur an dich selbst
                    "coalition_stability": -20 # Startet instabil!
                }
            }
        })

    # C) Opposition (Immer möglich)
    choices.append({
        "text": "Go into Opposition",
        "tooltip": "Refuse to govern. Reduces internal dissent as we can maintain ideological purity.",
        "success": {
            "msg": "We refuse to compromise our principles. Let others fail.",
            "effects": {
                "set_coalition": [state.player_party], # Formell bist du 'allein' in deiner Fraktion
                # KEIN start_negotiation -> Direkt zum Desk
                # Bonus: Parteiheilung
                "modify_faction": {"tag": "all", "amount": -15}, # Alle beruhigen sich
                "members": 5000 # Opposition zieht Mitglieder an
            }
        }
    })

    return {
        "id": "general_election",
        "title": "Post-Election Scenario",
        "text": intro_text,
        "choices": choices
    }