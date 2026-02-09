import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from content.base_event import GameEvent
import content.game_data as gd

class BurningConventsEvent(GameEvent):
    def should_trigger(self):
        # Bedingung 1: Datum (Mai 1931)
        is_date = (self.state.date['year'] == 1931 and self.state.date['month'] == 5)
        
        # Bedingung 2: Stimmung ist aufgeheizt
        # Wenn Public Order < 50 ODER wir Segura nur "verwarnt" haben (Flag checken, noch nicht implementiert)
        is_angry = (self.state.metrics['public_order'] < 60)
        
        return is_date and is_angry

    def get_data(self):
        player_party = self.state.player_party
        coalition = self.state.government['coalition']

        interior = self.state.ministries.get('interior')
        war = self.state.ministries.get('war')

        cabinet_balance = 0
        cabinet_text = []

        partners = [p for p in coalition if p != player_party]

        for p in partners:
            if p == gd.PARTY_DLR: # Maura (Interior)
                cabinet_balance += 2
                cabinet_text.append(f"{interior['holder']} (Interior) demands action.")
            elif p == gd.PARTY_PRR: # Lerroux (Foreign)
                cabinet_balance += 0
                cabinet_text.append("Lerroux (State) warns of international embarrassment.")
            elif p == gd.PARTY_AR: # Azaña (War)
                cabinet_balance -= 2
                cabinet_text.append(f"{war['holder']} (War) opposes violence against civilians.")
            elif p == gd.PARTY_PSOE: # Caballero/Prieto
                cabinet_balance -= 1
                cabinet_text.append("The PSOE leadership is wary of a bloodbath that could trigger a general strike.")
            elif p == gd.PARTY_PRRS: # Radical Socialists
                cabinet_balance += 0
                cabinet_text.append("The Radical Socialists sympathize with the rioters.")

        intro_text = f"""
        **The 'La Quema de Conventos' has reached a boiling point.** 
        Smoke rises from the Jesuit residence in Calle de la Flor. The mob is growing.
        
        In the Council of Ministers, the atmosphere is electric.
        {" ".join(cabinet_text)}
        """

        if cabinet_balance > 1:
            intro += "The mood in the room is grim. The conservative wing is pushing hard for a crackdown. "
        elif cabinet_balance < -1:
            intro += "The cabinet is paralyzed by fear of provoking a massacre. The left wing blocks any military action. "

        else:
            intro += " The government is deadlocked. Voices shout over each other. "
        
        intro += " ".join(cabinet_text)
        
        choices = []

        choices.append({
            "text": "Back Maura: 'Order is paramount.'",
            "success": {
                "msg": "After some heated handwrangling, the Interior Ministry deploys the Civil Guard.",
                "effects": {
                    "public_order": 5,
                    "clergy": -5,
                    "coalition_stability": -10,
                    "modify_relation": {"source": player_party, "target": gd.PARTY_DLR, "amount": 15},
                    "modify_relation_2": {"source": player_party, "target": gd.PARTY_AR, "amount": -10},
                    "demographic_shift": {
                        "group": "workers_urban",
                        "changes": {player_party: -0.05, gd.PARTY_PCE: 0.03}
                    },
                    "demographic_shift_2": {
                        "group": "bourgeoisie",
                        "changes": {player_party: 0.03}
                    }
                }
            }
        })
        
        choices.append({
            "text": "Back Azaña: 'Do not provoke the people.'",
            "success": {
                "msg": "The proposal to intervene is voted down. The convents burn.",
                "effects": {
                    "public_order": -15,
                    "society": {"clergy": -30, "aristocracy": -15},
                    "coalition_stability": -15,
                    "modify_relation": {"source": player_party, "target": gd.PARTY_DLR, "amount": -20},
                    "modify_relation_2": {"source": player_party, "target": gd.PARTY_AR, "amount": 10},
                    "demographic_shift": {
                        "group": "clergy",
                        "changes": {gd.PARTY_CEDA: 0.10},
                        "group": "workers_urban",
                        "changes": { player_party: 0.02 }
                    }
                }
            }
        })

        if self.state.metrics["coalition_stability"] > 60:
            choices.append({
                "text": "Agree to sending the Guardia Civil, but try to broker a delay until evening.'",
                "tooltip": "Noone becomes happy.",
                "success": {
                    "msg": "You manage to calm the ministers. A curfew is declared without bloodshed.",
                    "effects": {
                        "public_order": -5,
                        "society_clergy": -15,
                        "coalition_stability": 5,
                        "budget_int": -1 
                    }
                }
            })

        return {
            "id": "1931_burning_convents",
            "title": "La Quema de Conventos",
            "text": intro_text,
            "choices": choices
        }