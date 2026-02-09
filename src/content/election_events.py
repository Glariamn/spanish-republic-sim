import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import engine.mechanics as mech
import content.game_data as gd

def get_event_general_election(state):
    # Optionen berechnen
    opts = mech.get_coalition_options(state)
    
    text = "**Election Results.**\n\n"
    choices = []
    
    for opt in opts:
        coalition_name = opt['type']['name']
        seats = opt['seats']
        
        if opt['is_leader']:
            # DU BIST DER ANFÜHRER
            choices.append({
                "text": f"Form Government: {coalition_name} ({seats} Seats)",
                "success": {
                    "msg": "You invite the partners to the negotiation table.",
                    "effects": {
                        "set_coalition": opt['type']['partners'],
                        "start_negotiation": True # Neuer Trigger!
                    }
                }
            })
        elif opt['majority']: # Du bist Partner in einer Mehrheit
             leader_name = gd.PARTIES[opt['leader_id']]['name']
             choices.append({
                "text": f"Join {coalition_name} (Led by {leader_name})",
                "success": {
                    "msg": "You accept the invitation to negotiate.",
                    "effects": {
                        "set_coalition": opt['type']['partners'],
                        "start_negotiation": True
                    }
                }
            })
    
    # Opposition Option immer da
    choices.append({
        "text": "Go into Opposition",
        "success": {
            "msg": "We will watch them fail from the benches.",
            "effects": {
                "set_coalition": [state.player_party] # Allein
                # Keine Negotiation, direkt zurück zum Desk
            }
        }
    })

    return {
        "id": "general_election",
        "title": "Post-Election Scenario",
        "text": text,
        "choices": choices
    }