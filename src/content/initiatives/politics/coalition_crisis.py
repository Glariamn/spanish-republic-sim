import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from content.base_event import GameEvent
import content.game_data as gd
import random

class CoalitionCrisisEvent(GameEvent):
    
    def should_trigger(self):
        stability = self.state.metrics["coalition_stability"]
        
        # Trigger nur wenn instabil (< 30) und 20% Chance
        if stability < 30 and random.randint(1, 100) <= 20:
            # Wir speichern die problematische Partei direkt hier, 
            # damit wir sie bei get_data wiederfinden
            partners = [p for p in self.state.government["coalition"] if p != self.state.player_party]
            if not partners: return False
            
            self.angry_party_id = random.choice(partners)
            self.state.crisis_party_id = self.angry_party_id # Für Global State access
            return True
            
        return False

    def get_data(self):
        party_id = getattr(self, 'angry_party_id', self.state.get("crisis_party_id"))
        party_data = gd.PARTIES.get(party_id, gd.PARTIES["others"])
        party_name = party_data['name']
        ideology = party_data.get('ideology_index', 5)

        choices = []
        
        # --- OPTION 1: MINISTRY ---
        choices.append({
            "text": f"Offer a Ministry portfolio.",
            "tooltip": "Lose a ministry, gain massive stability.",
            "success": {
                "msg": f"The {party_name} accepts the responsibility.",
                "effects": {
                    "transfer_ministry": party_id, 
                    "coalition_stability": 25,
                    "modify_faction": {"tag": "not_left", "amount": 5} # Parteibasis (Beispiel)
                }
            }
        })

        # --- OPTION 2: POLICY (Austerity/Reform) ---
        if ideology >= 3: # Rechts/Zentrum
            choices.append({
                "text": "Commit to Austerity Measures.",
                "success": {
                    "msg": "Budget balanced, workers angry.",
                    "effects": {
                        "budget_int": 10,
                        "coalition_stability": 15,
                        "modify_faction": {"tag": "left", "amount": 20} 
                    }
                }
            })
        else: # Links
            choices.append({
                "text": "Accelerate Reforms.",
                "success": {
                    "msg": "Reforms promised, elites angry.",
                    "effects": {
                        "budget_int": -10,
                        "coalition_stability": 15,
                        "modify_faction": {"tag": "not_left", "amount": 15} 
                    }
                }
            })

        # --- OPTION 3: LEAVE ---
        choices.append({
            "text": "Refuse demands (Let them leave).",
            "success": {
                "msg": f"The {party_name} has left the coalition.",
                "effects": {
                    "remove_party": party_id,
                    "coalition_stability": -10
                }
            }
        })

        return {
            "id": "coalition_crisis",
            "title": "Coalition Fracture",
            "text": f"The **{party_name}** threatens to leave due to instability.",
            "choices": choices
        }