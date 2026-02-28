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


class CatalanStatuteEvent(GameEvent):
    EVENT_ID = "1932_catalan_statute"
    """
    September 1932: Estatut de Catalunya passes the Cortes.
    If the player promised autonomy to Macià (flag_catalan_autonomy_promised),
    ERC's reaction is acceptance. Without the promise, they feel doubly betrayed.
    """

    def should_trigger(self):
        already_fired = "flag_catalan_statute" in self.state.passed_laws
        constitution_done = "flag_constitution_ratified" in self.state.passed_laws
        is_date = (self.state.date['year'] == 1932 and self.state.date['month'] == 9)
        return is_date and constitution_done and not already_fired

    def get_data(self):
        player = self.state.player_party
        promised = "flag_catalan_autonomy_promised" in self.state.passed_laws

        if promised:
            erc_text = (
                "The ERC is satisfied — not triumphant, but satisfied. Macià had been promised "
                "autonomy in April 1931. What arrives is less than he asked for, but it is real. "
                "*'It is a beginning,'* Macià says."
            )
            erc_effect = {"source": gd.PARTY_ERC, "target": player, "amount": 15}
            stability_hit = -5
        else:
            erc_text = (
                "The ERC is furious — not at the statute itself, but at the humiliation of the process. "
                "No promise was made in April 1931. The Cortes debated Catalan autonomy as though it "
                "were a concession rather than a right. Macià accepts because he must. But the "
                "relationship with Madrid is poisoned."
            )
            erc_effect = {"source": gd.PARTY_ERC, "target": player, "amount": -10}
            stability_hit = -12

        return {
            "id": "1932_catalan_statute",
            "title": "The Statute of Catalonia",
            "date_str": "September 1932",
            "text": f"""
            **The Estatut de Catalunya passes the Cortes.**

            After nine months of debate and dilution, Catalonia receives its statute
            of autonomy. The Generalitat is restored with its own parliament, president,
            and limited competences over education, public order, and social policy.

            {erc_text}

            In the Cortes, the right votes against almost unanimously.
            General Mola, in the privacy of his study in Pamplona,
            adds another entry to a notebook he has been keeping since January.
            """,
            "choices": [
                {
                    "text": "Promulgate the statute.",
                    "success": {
                        "msg": "The Statute of Catalonia is promulgated. "
                               "The Generalitat receives official recognition.",
                        "effects": {
                            "add_law": "flag_catalan_statute",
                            "coalition_stability": stability_hit,
                            "catalans": 15,
                            "army_officer_loyalty": -5,
                            "modify_relation": erc_effect,
                            "demographic_shift": {
                                "group": "bourgeoisie",
                                "changes": {gd.PARTY_CEDA: 0.03, gd.PARTY_MON: 0.02,
                                            gd.PARTY_ERC: 0.01}
                            }
                        }
                    }
                }
            ]
        }


class AgrarianReformEvent(GameEvent):
    EVENT_ID = "1932_agrarian_reform"
    """
    September 1932: Ley de Reforma Agraria passes. Two versions available.
    """

    def should_trigger(self):
        already_fired = "flag_agrarian_reform" in self.state.passed_laws
        constitution_done = "flag_constitution_ratified" in self.state.passed_laws
        catalan_done = "flag_catalan_statute" in self.state.passed_laws
        is_date = (self.state.date['year'] == 1932 and self.state.date['month'] == 9)
        return is_date and constitution_done and catalan_done and not already_fired

    def get_data(self):
        player = self.state.player_party
        latifundios = self.state.land_ownership.get("latifundios", 65.0)

        return {
            "id": "1932_agrarian_reform",
            "title": "The Agrarian Reform Law",
            "date_str": "September 1932",
            "text": f"""
            **The Ley de Reforma Agraria passes the Cortes — barely.**

            Two years of committee work, landlord lobbying, and socialist pressure
            have produced something. The law creates the *Instituto de Reforma Agraria*
            and permits expropriation of large estates above legal size thresholds.

            Currently {latifundios:.0f}% of agricultural land is in latifundio holdings.
            The *jornaleros* who work these estates have waited since the Republic was
            proclaimed. They have been waiting over a year.

            The law is real. The implementation will be another matter — the IRA is
            underfunded, the legal system hostile to expropriation claims. The pace
            will disappoint everyone.
            """,
            "choices": [
                {
                    "text": "Accept the compromised law. Half a loaf is better than none.",
                    "tooltip": "Historical path. Passes with moderate support. "
                               "Peasants disappointed by the pace, but it is law.",
                    "success": {
                        "msg": "The Agrarian Reform Law passes. The IRA is established. "
                               "Expropriation begins — slowly.",
                        "effects": {
                            "add_law": "flag_agrarian_reform",
                            "add_law_2": "flag_agrarian_reform_moderate",
                            "coalition_stability": -5,
                            "budget_int": -3,
                            "demographic_shift": {
                                "group": "workers_rural",
                                "changes": {player: 0.02, gd.PARTY_PSOE: 0.02}
                            },
                            "demographic_shift_2": {
                                "group": "bourgeoisie",
                                "changes": {gd.PARTY_CEDA: 0.03, gd.PARTY_MON: 0.02,
                                            gd.PARTY_AR: -0.02}
                            },
                            "modify_relation": {
                                "source": gd.PARTY_PSOE, "target": player, "amount": 5
                            }
                        }
                    }
                },
                {
                    "text": "Push the bolder version. The peasants have waited long enough.",
                    "tooltip": "Higher impact but coalition costs. "
                               "Lerroux abstains or votes against. May fail.",
                    "requires_party": [gd.PARTY_PSOE, gd.PARTY_AR, gd.PARTY_PRRS],
                    "base_chance": 60,
                    "modifiers": {"coalition_stability": 0.3},
                    "success": {
                        "msg": "The bolder law passes. Faster timelines, lower compensation. "
                               "The Radicals storm out. The jornaleros celebrate in the plazas.",
                        "effects": {
                            "add_law": "flag_agrarian_reform",
                            "add_law_2": "flag_agrarian_reform_radical",
                            "coalition_stability": -15,
                            "budget_int": -5,
                            "demographic_shift": {
                                "group": "workers_rural",
                                "changes": {player: 0.05, gd.PARTY_PSOE: 0.04,
                                            gd.PARTY_PCE: 0.02}
                            },
                            "demographic_shift_2": {
                                "group": "bourgeoisie",
                                "changes": {gd.PARTY_CEDA: 0.06, gd.PARTY_MON: 0.04,
                                            gd.PARTY_AR: -0.04}
                            },
                            "modify_relation": {
                                "source": gd.PARTY_PRR, "target": player, "amount": -20
                            },
                            "modify_relation_2": {
                                "source": gd.PARTY_PSOE, "target": player, "amount": 15
                            }
                        }
                    },
                    "failure": {
                        "msg": "The bold version fails. Radicals abstain, right votes against. "
                               "The compromised version passes instead.",
                        "effects": {
                            "add_law": "flag_agrarian_reform",
                            "add_law_2": "flag_agrarian_reform_moderate",
                            "coalition_stability": -10,
                            "budget_int": -3,
                            "modify_relation": {
                                "source": gd.PARTY_PSOE, "target": player, "amount": -8
                            }
                        }
                    }
                }
            ]
        }
