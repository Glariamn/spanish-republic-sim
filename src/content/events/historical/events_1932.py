import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from content.base_event import GameEvent
import content.game_data as gd
import random


class SanjurjadaEvent(GameEvent):
    EVENT_ID = "1932_sanjurjada"
    """
    August 10, 1932: General José Sanjurjo launches a coup from Sevilla.
    It collapses within hours — the army stays loyal, the workers mobilise,
    and Sanjurjo is captured. Azaña emerges significantly stronger.

    The player must decide Sanjurjo's fate and whether to use the moment
    to push further military reforms.

    Fires once in August 1932. Does NOT require a flag_constitution_ratified
    check — the coup attempt happened regardless of constitutional politics.
    """

    def should_trigger(self):
        already_fired = "flag_sanjurjada" in self.state.passed_laws
        is_date = (self.state.date['year'] == 1932 and self.state.date['month'] == 8)
        return is_date and not already_fired

    def get_data(self):
        player = self.state.player_party
        war_holder = self.state.ministries.get("war", {}).get("holder", "Azaña")
        azana_in_war = self.state.ministries.get("war", {}).get("party") == gd.PARTY_AR

        # Azaña's actual response if he holds War
        azana_text = (
            f"{war_holder} moves immediately. Loyal units surround the rebel garrison. "
            f"Civil Guard commanders in Sevilla refuse to join. "
        ) if azana_in_war else (
            "The War Ministry mobilises loyal forces. "
        )

        # How close was it? Slightly random
        severity = random.choice(["contained", "contained", "moderate"])
        if severity == "moderate":
            severity_text = (
                "For six hours the outcome was genuinely uncertain — "
                "the rebels held the centre of Sevilla and cut telegraph lines north. "
            )
        else:
            severity_text = (
                "The rising collapses almost immediately outside Sevilla. "
                "In Madrid, a handful of officers are arrested before they can act. "
            )

        dlr_relation = self.state.government.get('relations', {}).get(
            (gd.PARTY_DLR, player), 50)
        zamora_text = (
            "President Zamora has already sent word to the cabinet: "
            "he will not sign a death warrant. *'The Republic must not begin with blood.'*"
        )

        return {
            "id": "1932_sanjurjada",
            "title": "The Sanjurjada",
            "date_str": "10 August 1932",
            "text": f"""
            **General José Sanjurjo has risen.**

            At dawn, rebel units seized the Captain-General's headquarters in Sevilla.
            A manifesto was broadcast demanding the government's resignation and the
            suspension of the Constitution. {severity_text}

            {azana_text}By midday Sanjurjo was retreating toward the Portuguese border.
            He was arrested at Huelva trying to cross. His companion: a suitcase
            full of women's clothes, apparently for disguise.

            The coup is over. The question now is what happens to Sanjurjo —
            and whether the Republic uses this moment.

            {zamora_text}
            """,
            "choices": [
                {
                    "text": "Demand the death penalty. The Republic must show it has teeth.",
                    "tooltip": "Historically Azaña wanted this. Zamora overruled him. "
                               "If you push it through: left loves it, right is radicalised, "
                               "Zamora's authority is damaged.",
                    "requires_party": [gd.PARTY_PSOE, gd.PARTY_AR, gd.PARTY_PRRS],
                    "success": {
                        "msg": "Sanjurjo is condemned and executed. "
                               "The message is received on both sides of the spectrum.",
                        "effects": {
                            "add_law": "flag_sanjurjada",
                            "add_law_2": "flag_sanjurjo_executed",
                            "public_order": 10,
                            "coalition_stability": 8,
                            "army_officer_loyalty": -20,
                            "modify_relation": {
                                "source": gd.PARTY_DLR,
                                "target": player,
                                "amount": -25
                            },
                            "modify_relation_2": {
                                "source": gd.PARTY_PSOE,
                                "target": player,
                                "amount": 15
                            },
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {player: 0.02}
                            },
                            "demographic_shift_2": {
                                "group": "bourgeoisie",
                                "changes": {gd.PARTY_CEDA: 0.05, gd.PARTY_MON: 0.03}
                            }
                        }
                    }
                },
                {
                    "text": "Accept commutation to life imprisonment. Let Zamora have his mercy.",
                    "tooltip": "Historical outcome. Sanjurjo is imprisoned, "
                               "later pardoned by the right in 1934. "
                               "Demonstrates republican rule of law.",
                    "success": {
                        "msg": "Sanjurjo is sentenced to life imprisonment at El Dueso. "
                               "Zamora is satisfied. The army breathes. "
                               "The left is disappointed — they wanted blood.",
                        "effects": {
                            "add_law": "flag_sanjurjada",
                            "add_law_2": "flag_sanjurjo_imprisoned",
                            "public_order": 5,
                            "coalition_stability": 5,
                            "army_officer_loyalty": -8,
                            "modify_relation": {
                                "source": gd.PARTY_DLR,
                                "target": player,
                                "amount": 10
                            },
                            "modify_relation_2": {
                                "source": gd.PARTY_PSOE,
                                "target": player,
                                "amount": -8
                            }
                        }
                    }
                },
                {
                    "text": "Use the moment. Push a second wave of military reform through the Cortes.",
                    "tooltip": "The coup gives political cover to purge further. "
                               "Sanjurjo is imprisoned AND you accelerate military reform. "
                               "Costly but transforms the army faster.",
                    "success": {
                        "msg": "The Cortes passes emergency military legislation. "
                               "Dozens of suspect officers are forcibly retired. "
                               "The coup accelerated what it was meant to stop.",
                        "effects": {
                            "add_law": "flag_sanjurjada",
                            "add_law_2": "flag_sanjurjo_imprisoned",
                            "add_law_2": "flag_military_reform_wave_2",
                            "public_order": 3,
                            "army_officer_loyalty": -25,
                            "army_soldier_loyalty": 10,
                            "army_reform_progress": 25,
                            "budget_int": -2,
                            "modify_relation": {
                                "source": gd.PARTY_DLR,
                                "target": player,
                                "amount": -15
                            },
                            "modify_relation_2": {
                                "source": gd.PARTY_PSOE,
                                "target": player,
                                "amount": 12
                            },
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {player: 0.01}
                            }
                        }
                    }
                }
            ]
        }
