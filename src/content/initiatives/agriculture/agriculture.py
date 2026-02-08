import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
import content.game_data as gd

def get_initiatives(state):
    cards = []
    passed = state.passed_laws

    # --- 1. INITIATIVE: Municipal Boundaries ---
    if "law_municipal" not in passed:
        cards.append({
            "id": "agri_reform_municipal",
            "type": "initiative", 
            "category": "state",
            "title": "Initiative: Municipal Boundaries",
            "text": "Draft a bill to force landowners to hire local workers first.",
            "base_weight": 10,
            "options": [
                {
                    "text": "Push the Bill to Vote",
                    "type": "Legislative",
                    "vote_config": {
                        "ideology_target": 3, 
                        "author_party": state.player_party
                    },
                    "success": {
                        "msg": "Passed! Rural workers rally to us.",
                        "add_law": "law_municipal",
                        "effects": {
                            "workers_rural": 10, 
                            "aristocracy": -5,
                            "demographic_shift": {
                                "group": "workers_rural",
                                "changes": {state.player_party: 0.05}
                            }
                        }
                    }
                }
            ]
        })

    # --- 2. REAKTIV: Rural Strike ---
    if state.society['workers_rural'] < 50:
        cards.append({
            "id": "agri_strike_andalusia",
            "type": "reactive",
            "category": "state",
            "title": "Strike in Andalusia",
            "text": "CNT agitators have paralyzed the harvest. Landowners demand the Civil Guard.",
            "base_weight": 30, 
            "options": [
                {
                    "text": "Send Guardia Civil (Restore Order)",
                    "success": {
                        "msg": "Order restored at gunpoint.",
                        "effects": {"public_order": 5, "workers_rural": -10, "aristocracy": 5}
                    }
                },
                {
                    "text": "Negotiate (Send Minister of Labor)",
                    "success": {
                        "msg": "A compromise is reached.",
                        "effects": {"budget_int": -2, "workers_rural": 5, "aristocracy": -5}
                    }
                }
            ],
            # DAS PASSIERT BEIM IGNORIEREN:
            "timeout_effect": {
                "msg": "IGNORED: The strike turned into a riot. Estates burned.",
                "effects": {
                    "public_order": -10,
                    "aristocracy": -10,
                    "demographic_shift": {
                        "group": "bourgeoisie",
                        "changes": {gd.PARTY_CEDA: 0.05}
                    }
                }
            }
        })
        
    return cards