import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from content.base_event import GameEvent
import content.game_data as gd
import random


class LeyAzanaEvent(GameEvent):
    """
    Azaña's military reform decree — April/May 1931.

    Fires when:
      - The war ministry is held by AR (historically Azaña)
      - The reform has not yet happened (flag_ley_azana not in passed_laws)
      - Parliament has formed (June+ 1931)
      - Player is NOT AR (AR players get the initiative card instead)

    Non-AR players respond in cabinet to Azaña's proposal.
    Three positions: support, abstain, or try to slow him down.
    Historically Azaña was determined and pushed it through regardless —
    the 'slow him down' path delays the reform by one month but doesn't stop it.
    """

    def should_trigger(self):
        if "flag_ley_azana" in self.state.passed_laws:
            return False
        if "flag_ley_azana_delayed" in self.state.passed_laws:
            # Delayed version fires next month
            return True
        # AR players handle this as an initiative card, not an event
        if self.state.player_party == gd.PARTY_AR:
            return False
        # Azaña must hold the War Ministry
        war_min = self.state.ministries.get("war", {})
        azana_in_charge = war_min.get("party") == gd.PARTY_AR
        # Fires from May 1931 onwards, once parliament has formed
        parliament_formed = sum(self.state.parliament["seats"].values()) > 0
        return azana_in_charge and parliament_formed

    def get_data(self):
        player = self.state.player_party
        war_holder = self.state.ministries.get("war", {}).get("holder", "Azaña")
        delayed = "flag_ley_azana_delayed" in self.state.passed_laws

        if delayed:
            opening = (
                f"**{war_holder} is back.** Last month's objections have not deterred him. "
                "The voluntary retirement offer is back on the table — and this time "
                "he has the President's backing."
            )
        else:
            opening = (
                f"**{war_holder}** has placed a decree on the cabinet table. "
                "All officers of the Peninsular Army will be offered voluntary retirement "
                "on full pay. Those who accept will leave the service permanently. "
                "Those who refuse will remain — but Azaña intends to follow with further reforms "
                "that will make the service uncomfortable for monarchist hardliners."
            )

        return {
            "id": "1931_ley_azana",
            "title": "The Officer Question",
            "date_str": "May 1931",
            "text": f"""{opening}

The numbers are stark: Spain has one officer for every six enlisted men — \
a grotesque ratio inherited from the colonial wars. The army is top-heavy, \
politicised, and deeply monarchist in its senior ranks.

Azaña's argument: the Republic cannot survive a coup plotted by its own \
officer corps. Better to pay them off now, while the army is still too \
disorganised to resist.

The counter-argument: the officers who accept retirement will be the moderates \
willing to serve any government. Those who stay will be the hardliners — \
concentrated and embittered. The reform may create exactly the enemy it \
means to neutralise.

Both arguments are probably right.""",
            "choices": [
                {
                    "text": "Support the decree. The Republic needs a loyal army.",
                    "tooltip": "Back Azaña openly in cabinet. Officer loyalty takes a short-term hit, "
                               "but reform progress begins. AR relations improve.",
                    "success": {
                        "msg": f"Your public support strengthens Azaña's hand in cabinet. "
                               f"The decree passes. Retirement offers go out to 16,000 officers. "
                               f"Roughly 40% accept. Those who remain are a harder, angrier corps.",
                        "effects": {
                            "add_law": "flag_ley_azana",
                            "army_officer_loyalty": -12,
                            "army_soldier_loyalty": 6,
                            "army_officers_retired": True,
                            "army_reform_progress": 20,
                            "budget_int": -3,
                            "modify_relation": {
                                "source": gd.PARTY_AR,
                                "target": player,
                                "amount": 12
                            },
                            "modify_relation_2": {
                                "source": gd.PARTY_DLR,
                                "target": player,
                                "amount": -8
                            },
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {player: 0.01, gd.PARTY_AR: 0.02}
                            }
                        }
                    }
                },
                {
                    "text": "Stay out of it. This is Azaña's fight, not ours.",
                    "tooltip": "No position taken. Azaña pushes it through anyway. "
                               "You neither gain nor lose — but you signal caution to the right.",
                    "success": {
                        "msg": "Your party abstains from the cabinet debate. "
                               "Azaña pushes the decree through regardless. "
                               "The reform happens — you simply weren't part of it.",
                        "effects": {
                            "add_law": "flag_ley_azana",
                            "army_officer_loyalty": -12,
                            "army_soldier_loyalty": 6,
                            "army_officers_retired": True,
                            "army_reform_progress": 20,
                            "budget_int": -3,
                            "modify_relation": {
                                "source": gd.PARTY_DLR,
                                "target": player,
                                "amount": -3
                            }
                        }
                    }
                },
                {
                    "text": "Raise objections. The timing is wrong — wait until after the elections.",
                    "tooltip": "Azaña will push it through next month anyway, but you buy time "
                               "and signal restraint to Zamora and the right. "
                               "Small goodwill gain with DLR/PRR, small loss with AR.",
                    "success": {
                        "msg": "You voice concerns about the timing. Azaña is impatient but agrees "
                               "to wait one month. Zamora appreciates the caution. "
                               "The reform will happen — just not today.",
                        "effects": {
                            "add_law": "flag_ley_azana_delayed",
                            "modify_relation": {
                                "source": gd.PARTY_AR,
                                "target": player,
                                "amount": -8
                            },
                            "modify_relation_2": {
                                "source": gd.PARTY_DLR,
                                "target": player,
                                "amount": 8
                            }
                        }
                    }
                }
            ]
        }
