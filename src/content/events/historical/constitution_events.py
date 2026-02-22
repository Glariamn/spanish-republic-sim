import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from content.base_event import GameEvent
import content.game_data as gd
import random

class LerrouxExitEvent(GameEvent):
    def should_trigger(self):
        is_date = self.state.date['year'] == 1931 and self.state.date['month'] == 10
        is_in_gov = gd.PARTY_PRR in self.state.government['coalition']
        return is_date and is_in_gov

    def get_data(self):
        return {
            "id": "1931_lerroux_exit",
            "title": "The Radical Rupture",
            "date_str": "October 1931",
            "text": """
            **The Coalition is fracturing.**

            Alejandro Lerroux and his Radical Republican Party (PRR) can no longer support the government.
            They cite the "excessive influence of the Socialists" and the aggressively anticlerical
            direction of the new Constitution.

            Lerroux demands that the Socialists leave the government -- or he will.
            """,
            "choices": [
                {
                    "text": "Let Lerroux go. Keep the Socialists.",
                    "tooltip": "Historical Choice. Maintains the left coalition but loses the Centre.",
                    "success": {
                        "msg": "Lerroux resigns. The Radicals join the opposition.",
                        "effects": {
                            "remove_party": gd.PARTY_PRR,
                            "coalition_stability": -15,
                            "modify_faction": {"tag": "left", "amount": -10},
                            "demographic_shift": {
                                "group": "bourgeoisie",
                                "changes": {gd.PARTY_PRR: 0.05, self.state.player_party: -0.05}
                            }
                        }
                    }
                },
                {
                    "text": "Dump the Socialists to keep Lerroux.",
                    "tooltip": "A massive betrayal. Will inflame the labour movement.",
                    "requires_party": [gd.PARTY_AR, gd.PARTY_DLR],
                    "success": {
                        "msg": "You break ties with the PSOE. Lerroux stays, but the streets are on fire.",
                        "effects": {
                            "remove_party": gd.PARTY_PSOE,
                            "coalition_stability": 10,
                            "public_order": -30,
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {gd.PARTY_PSOE: 0.10, self.state.player_party: -0.10}
                            }
                        }
                    }
                }
            ]
        }


class Constitution26CrisisEvent(GameEvent):
    """
    Fires after the radical version of Art. 26 passes a parliamentary vote.
    This is NOT a re-vote on the article -- that is done. This is the political
    fallout: Zamora and Maura's reaction, and how the government survives it.

    Three paths depending on DLR relations:
      >= 50: Zamora threatens, player can offer concessions to keep DLR
      30-49: Zamora threatens, concessions are harder to make stick
      < 30:  Zamora has already submitted his resignation -- no negotiation
    """
    def should_trigger(self):
        radical_passed = "const_art_26_radical" in self.state.passed_laws
        dlr_in_gov = gd.PARTY_DLR in self.state.government['coalition']
        not_fired = "flag_26_crisis_fired" not in self.state.passed_laws
        return radical_passed and dlr_in_gov and not_fired

    def get_data(self):
        dlr_rel = self.state.parties.get(gd.PARTY_DLR, {}).get(
            "relations", {}).get(self.state.player_party, 50)
        stability = self.state.metrics.get("coalition_stability", 50)

        # --- Build contextual text based on DLR relations ---
        if dlr_rel >= 50:
            situation = (
                "Despite his anger, Alcala-Zamora has not yet resigned. He is waiting "
                "to see whether the government will offer him any assurances. "
                "There is still room to negotiate."
            )
        elif dlr_rel >= 30:
            situation = (
                "Alcala-Zamora is furious. He has summoned the cabinet and delivered an ultimatum: "
                "either the government walks back its most extreme implications, or he and Maura walk out. "
                "His patience is nearly exhausted."
            )
        else:
            situation = (
                "Alcala-Zamora has submitted his resignation. So has Miguel Maura. "
                "There is no path back -- the DLR is leaving the coalition. "
                "The only question is who leads the government next."
            )

        choices = []

        # --- Concession paths (only available if DLR relations are not already broken) ---
        if dlr_rel >= 30:
            choices.append({
                "text": "Offer to moderate Article 27 as a gesture of good faith.",
                "tooltip": "Promise softer language on the conscience clause. DLR may accept if relations are high enough.",
                "success": {
                    "msg": "You pledge to moderate Article 27. Zamora accepts the gesture -- grudgingly. "
                           "The DLR remains in government, but their trust in you is damaged.",
                    "effects": {
                        "add_law": "flag_26_crisis_fired",
                        "add_law_2": "flag_art27_softened",  # initiatives/constitution.py will read this
                        "coalition_stability": 5,
                        "modify_relation": {
                            "source": gd.PARTY_DLR,
                            "target": self.state.player_party,
                            "amount": -10
                        },
                        "modify_relation_2": {
                            "source": gd.PARTY_PSOE,
                            "target": self.state.player_party,
                            "amount": -8
                        }
                    }
                },
                "failure": {
                    "msg": "You pledge to moderate Article 27, but Zamora no longer trusts you. He resigns anyway.",
                    "effects": {
                        "add_law": "flag_26_crisis_fired",
                        "remove_party": gd.PARTY_DLR,
                        "coalition_stability": -20,
                        "modify_relation": {
                            "source": gd.PARTY_DLR,
                            "target": self.state.player_party,
                            "amount": -25
                        }
                    }
                },
                # High DLR relations = success, low = failure
                "base_chance": min(90, max(20, dlr_rel + 10)),
                "modifiers": {}
            })

            choices.append({
                "text": "Transfer Interior Ministry to DLR as a permanent guarantee.",
                "tooltip": "Give Maura's portfolio as a coalition anchor. Costly but effective if relations hold.",
                "success": {
                    "msg": "You give the DLR a permanent stake in the government. "
                           "Zamora accepts. Maura keeps Interior. The coalition holds -- barely.",
                    "effects": {
                        "add_law": "flag_26_crisis_fired",
                        "coalition_stability": -10,
                        "modify_relation": {
                            "source": gd.PARTY_DLR,
                            "target": self.state.player_party,
                            "amount": 8
                        },
                        "modify_relation_2": {
                            "source": gd.PARTY_PSOE,
                            "target": self.state.player_party,
                            "amount": -15
                        }
                    }
                },
                "failure": {
                    "msg": "Even the ministry offer is not enough. Zamora resigns.",
                    "effects": {
                        "add_law": "flag_26_crisis_fired",
                        "remove_party": gd.PARTY_DLR,
                        "coalition_stability": -15
                    }
                },
                "base_chance": min(85, max(15, dlr_rel)),
                "modifiers": {}
            })

        # --- Let them go / forced resignation ---
        if dlr_rel >= 30:
            resign_text = "Accept their resignation. Azana takes the helm."
            resign_tooltip = "Historical path. DLR leaves, Azana becomes Prime Minister."
        else:
            resign_text = "Accept the inevitable. Zamora and Maura are gone."
            resign_tooltip = "With DLR relations this low, there was never a path back."

        choices.append({
            "text": resign_text,
            "tooltip": resign_tooltip,
            "success": {
                "msg": "Alcala-Zamora and Maura resign. The DLR enters opposition. "
                       "Manuel Azana steps forward to lead the government. "
                       "In December, Zamora will be elected President of the Republic.",
                "effects": {
                    "add_law": "flag_26_crisis_fired",
                    "add_law_2": "flag_zamora_resigned_pm",
                    "remove_party": gd.PARTY_DLR,
                    "coalition_stability": -20,
                    "clergy": -30,
                    "aristocracy": -15,
                    "workers_urban": 15,
                    "modify_relation": {
                        "source": gd.PARTY_DLR,
                        "target": self.state.player_party,
                        "amount": -30
                    },
                    "modify_relation_2": {
                        "source": gd.PARTY_PRR,
                        "target": self.state.player_party,
                        "amount": -15
                    },
                    # Azana takes PM -- start pm nomination with Azana pre-favoured
                    "start_pm_nomination": True
                }
            }
        })

        return {
            "id": "1931_constitution_26_crisis",
            "title": "The Religious Crisis",
            "date_str": "October 1931",
            "text": f"""
            **Article 26 has passed. The Republic has declared itself secular.**

            In the Council of Ministers, Prime Minister Alcala-Zamora is pale with fury.
            He and Miguel Maura (Interior) have made clear that they cannot remain in a
            government that has, in his words, "declared war on the conscience of Catholic Spain."

            {situation}
            """,
            "choices": choices
        }


class ConstitutionCrisis27Event(GameEvent):
    """
    Fires after Art. 27 (strict laicism) passes, IF:
    - Art. 26 was already radical (compounding effect)
    - DLR is still in the coalition
    - DLR relations < 50 (already damaged)
    This represents the straw that broke the camel's back.
    """
    def should_trigger(self):
        art27_strict = "const_art_27_strict" in self.state.passed_laws
        art26_radical = "const_art_26_radical" in self.state.passed_laws
        dlr_in_gov = gd.PARTY_DLR in self.state.government['coalition']
        dlr_rel = self.state.parties.get(gd.PARTY_DLR, {}).get(
            "relations", {}).get(self.state.player_party, 50)
        not_fired = "flag_27_crisis_fired" not in self.state.passed_laws
        # Only triggers if Art. 26 also radical AND DLR relations already damaged
        return art27_strict and art26_radical and dlr_in_gov and dlr_rel < 50 and not_fired

    def get_data(self):
        dlr_rel = self.state.parties.get(gd.PARTY_DLR, {}).get(
            "relations", {}).get(self.state.player_party, 50)

        return {
            "id": "1931_constitution_27_crisis",
            "title": "The Last Straw",
            "date_str": "November 1931",
            "text": """
            **Article 27 has passed. Spain is now formally a secular state in the fullest sense.**

            After the Jesuit dissolution under Article 26, this clause removes any remaining ambiguity.
            Alcala-Zamora, who had stayed on hoping for a gesture of moderation, has had enough.
            He tells the cabinet: *"I cannot lend my name to a government building a wall between
            the Republic and half of Spain."*

            He submits his resignation. Maura follows.
            """,
            "choices": [
                {
                    "text": "Accept. The Republic must be secular or it is nothing.",
                    "tooltip": "DLR leaves. Azana takes over. Coalition is now purely left-republican.",
                    "success": {
                        "msg": "Zamora and Maura resign. The left coalition governs alone. "
                               "Azana will lead. Zamora is a candidate for President of the Republic.",
                        "effects": {
                            "add_law": "flag_27_crisis_fired",
                            "add_law_2": "flag_zamora_resigned_pm",
                            "remove_party": gd.PARTY_DLR,
                            "coalition_stability": -25,
                            "clergy": -20,
                            "workers_urban": 10,
                            "modify_relation": {
                                "source": gd.PARTY_DLR,
                                "target": self.state.player_party,
                                "amount": -35
                            },
                            "start_pm_nomination": True
                        }
                    }
                }
            ]
        }


class ConstitutionCrisis44Event(GameEvent):
    """
    Fires after Art. 44 (social property clause) passes, IF coalition stability
    is already low AND DLR or PRR relations are strained.
    Represents the centre-right partners threatening to pull out over socialism.
    """
    def should_trigger(self):
        art44_social = "const_art_44_social" in self.state.passed_laws
        stability = self.state.metrics.get("coalition_stability", 50)
        dlr_rel = self.state.parties.get(gd.PARTY_DLR, {}).get(
            "relations", {}).get(self.state.player_party, 50)
        prr_rel = self.state.parties.get(gd.PARTY_PRR, {}).get(
            "relations", {}).get(self.state.player_party, 50)
        dlr_in_gov = gd.PARTY_DLR in self.state.government['coalition']
        prr_in_gov = gd.PARTY_PRR in self.state.government['coalition']
        not_fired = "flag_44_crisis_fired" not in self.state.passed_laws
        crisis_conditions = stability < 35 and (
            (dlr_in_gov and dlr_rel < 45) or
            (prr_in_gov and prr_rel < 45)
        )
        return art44_social and crisis_conditions and not_fired

    def get_data(self):
        dlr_in_gov = gd.PARTY_DLR in self.state.government['coalition']
        prr_in_gov = gd.PARTY_PRR in self.state.government['coalition']

        if dlr_in_gov:
            complainer = "Alcala-Zamora (DLR)"
            complainer_party = gd.PARTY_DLR
        else:
            complainer = "Lerroux (PRR)"
            complainer_party = gd.PARTY_PRR

        return {
            "id": "1931_constitution_44_crisis",
            "title": "The Property Crisis",
            "date_str": "November 1931",
            "text": f"""
            **Article 44 has passed. The state now has the legal right to expropriate property.**

            {complainer} has requested an emergency cabinet session. In the antechamber,
            he tells journalists: *"We did not come to this government to build socialism.
            We came to build a Republic."*

            Inside, he delivers an ultimatum: either the government commits to no land expropriations
            without full compensation, or his party withdraws its support.
            """,
            "choices": [
                {
                    "text": "Commit to full compensation for any expropriation.",
                    "tooltip": "Defuses the crisis. Weakens the practical force of Art. 44 but keeps the coalition.",
                    "success": {
                        "msg": "You offer the guarantee. The crisis passes -- for now. "
                               "But the PSOE is furious at the backpedal.",
                        "effects": {
                            "add_law": "flag_44_crisis_fired",
                            "add_law_2": "flag_art44_compensation_pledge",
                            "coalition_stability": 10,
                            "modify_relation": {
                                "source": complainer_party,
                                "target": self.state.player_party,
                                "amount": 12
                            },
                            "modify_relation_2": {
                                "source": gd.PARTY_PSOE,
                                "target": self.state.player_party,
                                "amount": -15
                            },
                            "modify_faction": {"tag": "left", "amount": 20}
                        }
                    }
                },
                {
                    "text": "Refuse. Article 44 stands as written.",
                    "tooltip": "The complainer may withdraw. Coalition stability takes a hit.",
                    "success": {
                        "msg": "You refuse to bind the government's hands. The coalition partner "
                               "withdraws, furious. The left is relieved.",
                        "effects": {
                            "add_law": "flag_44_crisis_fired",
                            "remove_party": complainer_party,
                            "coalition_stability": -20,
                            "modify_relation": {
                                "source": complainer_party,
                                "target": self.state.player_party,
                                "amount": -25
                            },
                            "workers_rural": 10
                        }
                    }
                }
            ]
        }


class ConstitutionRatifiedEvent(GameEvent):
    def should_trigger(self):
        is_date = self.state.date['year'] == 1931 and self.state.date['month'] == 12
        not_fired = "flag_constitution_ratified" not in self.state.passed_laws
        return is_date and not_fired

    def get_data(self):
        laws = self.state.passed_laws

        # Build dynamic summary of what was passed
        const_summary = []

        if "const_suffrage" in laws:
            const_summary.append("- **Article 36:** Universal suffrage. Women vote for the first time.")
        elif "const_suffrage_limited" in laws:
            const_summary.append("- **Article 36:** Suffrage postponed. The feminist movement is bitterly disappointed.")
        else:
            const_summary.append("- **Article 36:** Only male suffrage. Women's rights not addressed.")

        if "const_art_26_radical" in laws:
            const_summary.append("- **Article 26:** Strict secularism. The Jesuits are dissolved. The Church is furious.")
        elif "const_art_26_moderate" in laws:
            const_summary.append("- **Article 26:** Moderate secularism. The Church loses state funding but keeps its schools.")
        else:
            const_summary.append("- **Article 26:** The religious question was left unresolved.")

        if "const_art_27_strict" in laws:
            const_summary.append("- **Article 27:** Full laicism. Spain has no official religion.")
        elif "const_art_27_moderate" in laws:
            const_summary.append("- **Article 27:** Freedom of worship guaranteed with state neutrality.")

        if "const_art_43" in laws:
            const_summary.append("- **Article 43:** Civil marriage and divorce are now legal.")
        elif "const_art_43_restricted" in laws:
            const_summary.append("- **Article 43:** Civil marriage enacted, but divorce was not included.")

        if "const_art_44_social" in laws:
            const_summary.append("- **Article 44:** Property is subordinate to national social interest. Land reform is now constitutional.")
        elif "const_art_44_liberal" in laws:
            const_summary.append("- **Article 44:** Private property strictly protected. The Agrarians breathe easy.")

        if "const_art_48_secular" in laws:
            const_summary.append("- **Article 48:** Fully secular public education. Religious orders removed from schools.")
        elif "const_art_48_mixed" in laws:
            const_summary.append("- **Article 48:** Mixed education system. State schools will expand alongside Church schools.")

        summary_text = "\n".join(const_summary)

        # Zamora's role depends on whether he resigned as PM or not
        zamora_resigned = "flag_zamora_resigned_pm" in laws
        if zamora_resigned:
            zamora_text = (
                "Alcala-Zamora, who resigned as Prime Minister over Article 26, "
                "is now the consensus choice for President of the Republic -- "
                "a largely ceremonial role that all sides can accept."
            )
        else:
            zamora_text = (
                "Alcala-Zamora steps down as Prime Minister to take the role of "
                "President of the Republic -- Head of State under the new Constitution. "
                "The position of Prime Minister is now open."
            )

        return {
            "id": "1931_constitution_ratified",
            "title": "La Constitucion de 1931",
            "date_str": "9 December 1931",
            "text": f"""
            **The Cortes Constituyentes have completed their work.**

            After months of grueling debate, the Constitution of the Spanish Republic is ratified.
            Spain is defined as "a democratic republic of workers of all classes."

            **What was decided:**
            {summary_text}

            {zamora_text}
            """,
            "choices": [
                {
                    "text": "Elect Alcala-Zamora as President. Form a constitutional government.",
                    "tooltip": "The provisional government ends. A new PM nomination begins.",
                    "success": {
                        "msg": "Alcala-Zamora moves to the Presidential Palace. "
                               "The Republic is now fully constitutional. A new government must be formed.",
                        "effects": {
                            "add_law": "flag_constitution_ratified",
                            "add_law_2": "constitution_active",
                            "public_order": 10,
                            "coalition_stability": 15,
                            "start_pm_nomination": True
                        }
                    }
                }
            ]
        }
