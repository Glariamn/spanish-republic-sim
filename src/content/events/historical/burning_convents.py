import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from content.base_event import GameEvent
import content.game_data as gd

class BurningConventsEvent(GameEvent):
    def should_trigger(self):
        is_date = (self.state.date['year'] == 1931 and self.state.date['month'] == 5)
        is_angry = (self.state.metrics['public_order'] < 60)
        not_fired = "flag_burning_convents_fired" not in self.state.passed_laws
        return is_date and is_angry and not_fired

    def get_data(self):
        player_party = self.state.player_party
        coalition = self.state.government['coalition']

        interior = self.state.ministries.get('interior', {})
        war = self.state.ministries.get('war', {})

        cabinet_balance = 0
        cabinet_lines = []

        partners = [p for p in coalition if p != player_party]

        for p in partners:
            if p == gd.PARTY_DLR:
                cabinet_balance += 2
                cabinet_lines.append(f"{interior.get('holder','Maura')} (Interior) demands immediate action.")
            elif p == gd.PARTY_PRR:
                cabinet_lines.append("Lerroux (State) warns of international embarrassment.")
            elif p == gd.PARTY_AR:
                cabinet_balance -= 2
                cabinet_lines.append(f"{war.get('holder','Azaña')} (War) opposes violence against civilians.")
            elif p == gd.PARTY_PSOE:
                cabinet_balance -= 1
                cabinet_lines.append("The PSOE leadership fears a bloodbath that could trigger a general strike.")
            elif p == gd.PARTY_PRRS:
                cabinet_lines.append("The Radical Socialists sympathize with the rioters.")

        if cabinet_balance > 1:
            cabinet_mood = "The mood in the room is grim. The conservative wing pushes hard for a crackdown."
        elif cabinet_balance < -1:
            cabinet_mood = "The cabinet is paralyzed by fear of provoking a massacre. The left wing blocks any military action."
        else:
            cabinet_mood = "The government is deadlocked. Voices shout over each other."

        cabinet_text = " ".join(cabinet_lines)

        intro = f"""**La Quema de Conventos — the fires are spreading.**

On May 10, 1931, a monarchist provocation in Madrid — playing the former royal anthem \
*Marcha Real* from a window on Calle de Alcalá — ignited widespread anticlerical riots \
that spread rapidly to Sevilla, Málaga, Cádiz, and other cities over three days.

Crowds burned or damaged approximately 100 religious buildings. Priceless libraries, artworks, \
and archives were destroyed. No clergy were killed, but the episode alienated Catholic opinion \
profoundly, radicalized conservative resistance, and deepened calls for strict secular legislation.

Interior Minister Maura has declared martial law in affected provinces. War Minister Azaña \
reportedly said he would rather lose all Spain's convents than shed a single republican's blood.

*In the Council of Ministers, the atmosphere is electric.* {cabinet_mood} {cabinet_text}"""

        choices = []

        choices.append({
            "text": "Back Maura: 'Order is paramount.'",
            "success": {
                "msg": "The Interior Ministry deploys the Civil Guard. Order is restored at a political cost.",
                "effects": {
                    "add_law": "flag_burning_convents_fired",
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
                "msg": "The proposal to intervene is voted down. The convents burn. The Church is outraged.",
                "effects": {
                    "add_law": "flag_burning_convents_fired",
                    "public_order": -15,
                    "clergy": -30,
                    "aristocracy": -15,
                    "coalition_stability": -15,
                    "modify_relation": {"source": player_party, "target": gd.PARTY_DLR, "amount": -20},
                    "modify_relation_2": {"source": player_party, "target": gd.PARTY_AR, "amount": 10},
                    "demographic_shift": {
                        "group": "workers_urban",
                        "changes": {player_party: 0.02}
                    },
                    "demographic_shift_2": {
                        "group": "bourgeoisie",
                        "changes": {gd.PARTY_CEDA: 0.10}
                    }
                }
            }
        })

        if self.state.metrics["coalition_stability"] > 60:
            choices.append({
                "text": "Negotiate a delay. Deploy at nightfall to avoid bloodshed.",
                "tooltip": "Nobody is happy, but the worst is avoided.",
                "success": {
                    "msg": "A curfew is declared without bloodshed. The tension eases — but only slightly.",
                    "effects": {
                        "add_law": "flag_burning_convents_fired",
                        "public_order": -5,
                        "clergy": -15,
                        "coalition_stability": 5,
                        "budget_int": -1
                    }
                }
            })

        return {
            "id": "1931_burning_convents",
            "title": "La Quema de Conventos",
            "text": intro,
            "choices": choices
        }
