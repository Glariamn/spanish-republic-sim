import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
import content.game_data as gd

# Military reform initiative cards.
#
# These cards represent the sequential Azaña military reforms of 1931-1932.
# The dependency chain is:
#
#   [Event] Ley Azaña / voluntary retirement offer  (non-AR: event; AR: card below)
#       └─ flag_ley_azana
#           └─ [Card] Abolish Capitanías Generales
#               └─ flag_capitanias_abolished
#                   └─ [Card] Restructure into Divisions
#                       └─ flag_divisions_restructured
#                           └─ [Card] Close the Academia General Militar (Zaragoza)
#
#   [Card] Create Guardia de Asalto  (requires Interior Ministry + any reform progress)
#
# Cards are only available to the party holding the relevant ministry.
# AR gets the Ley Azaña card instead of the event.
# All other cards are available to whoever holds the War Ministry.

def _holds_war(state):
    return state.ministries.get("war", {}).get("party") == state.player_party

def _holds_interior(state):
    return state.ministries.get("interior", {}).get("party") == state.player_party

def _reform_progress(state):
    return state.military.get("army_peninsular", {}).get("reform_progress", 0)

def get_initiatives(state):
    cards = []
    laws = state.passed_laws
    player = state.player_party
    army = state.military.get("army_peninsular", {})

    # ─────────────────────────────────────────────────────────────────────────
    # 0. LEY AZAÑA — AR players only, fires instead of the event
    # ─────────────────────────────────────────────────────────────────────────
    if (player == gd.PARTY_AR
            and "flag_ley_azana" not in laws
            and "flag_ley_azana_delayed" not in laws
            and _holds_war(state)):

        officers = army.get("officers", 16000)
        retiring = int(officers * 0.40)

        cards.append({
            "id": "mil_ley_azana",
            "type": "initiative",
            "deck": "party",
            "category": "Military Reform",
            "title": "Ley Azaña: Voluntary Retirement Offer",
            "ministry_required": "war",
            "text": (
                "As War Minister, you have drafted the decree. Every officer of the Peninsular Army "
                "will be offered full-pay retirement — permanently. Those who accept leave the service. "
                "Those who refuse stay, knowing that further reforms are coming.\n\n"
                f"There are currently {officers:,} officers for {army.get('soldiers', 105000):,} soldiers — "
                "one officer for every six men. The army is a jobs programme for the monarchist gentry.\n\n"
                "The paradox is real: the moderates will retire; the hardliners will stay. "
                "The corps will be smaller, cheaper, and more hostile. "
                "But it will also be easier to monitor, and easier to reform further."
            ),
            "base_weight": 50,
            "options": [
                {
                    "text": "Issue the decree. Begin the reform.",
                    "tooltip": f"~{retiring:,} officers accept retirement. "
                               "Officer loyalty falls short-term. Reform chain begins. Costs 3 budget/month.",
                    "success": {
                        "msg": (
                            f"The decree is published. Retirement offers go out to {officers:,} officers. "
                            f"Roughly {retiring:,} accept — mostly the moderates. "
                            "Those who remain are a harder, more politicised corps. "
                            "But they are fewer, and the army's monthly cost has fallen."
                        ),
                        "effects": {
                            "add_law": "flag_ley_azana",
                            "army_officer_loyalty": -15,
                            "army_soldier_loyalty": 8,
                            "army_officers_retired": True,
                            "army_reform_progress": 25,
                            "budget_int": -3,
                            "modify_relation": {
                                "source": gd.PARTY_DLR,
                                "target": player,
                                "amount": -10
                            },
                            "modify_relation_2": {
                                "source": gd.PARTY_PRR,
                                "target": player,
                                "amount": -8
                            },
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {gd.PARTY_AR: 0.03, gd.PARTY_PSOE: 0.01}
                            }
                        }
                    }
                },
                {
                    "text": "Hold back for now. The political moment is not right.",
                    "tooltip": "Delay the reform. The card stays in hand. "
                               "Your left faction grows impatient.",
                    "success": {
                        "msg": "You decide the moment is not yet right. "
                               "The decree sits on your desk unsigned. "
                               "Your own left wing begins to mutter.",
                        "effects": {
                            "modify_faction": {"tag": "left", "amount": 8}
                        }
                    }
                }
            ]
        })

    # ─────────────────────────────────────────────────────────────────────────
    # 1. ABOLISH CAPITANÍAS GENERALES
    # ─────────────────────────────────────────────────────────────────────────
    if ("flag_ley_azana" in laws
            and "flag_capitanias_abolished" not in laws
            and _holds_war(state)):

        cards.append({
            "id": "mil_abolish_capitanias",
            "type": "initiative",
            "deck": "party",
            "category": "Military Reform",
            "title": "Abolish the Capitanías Generales",
            "ministry_required": "war",
            "text": (
                "The Capitanías Generales are Spain's eight regional military commands — "
                "a feudal inheritance that gives regional generals near-autonomous power and "
                "a platform for political interference. Sanjurjo runs one from Seville. "
                "They are the institutional spine of any potential coup.\n\n"
                "Abolishing them and replacing with direct divisional command under Madrid "
                "breaks that spine. It will also enrage every senior general in Spain."
            ),
            "base_weight": 30,
            "options": [
                {
                    "text": "Issue the abolition decree.",
                    "tooltip": "Major coup risk reduction long-term. "
                               "Heavy officer loyalty hit. Generals furious.",
                    "success": {
                        "msg": "The Capitanías are dissolved by decree. Regional commanders report "
                               "directly to the War Ministry henceforth. "
                               "The generals are furious. Two submit formal protests. "
                               "Sanjurjo is said to have thrown the gazette across his office.",
                        "effects": {
                            "add_law": "flag_capitanias_abolished",
                            "army_officer_loyalty": -18,
                            "army_reform_progress": 20,
                            "army_capitanias_abolished": True,
                            "modify_faction": {"tag": "moderate", "amount": 5},
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {gd.PARTY_AR: 0.02}
                            }
                        }
                    }
                },
                {
                    "text": "Not yet. Consolidate the voluntary retirement gains first.",
                    "tooltip": "Wait. The card remains available next month.",
                    "success": {
                        "msg": "You decide to consolidate before pushing further. "
                               "The Capitanías remain for now.",
                        "effects": {}
                    }
                }
            ]
        })

    # ─────────────────────────────────────────────────────────────────────────
    # 2. RESTRUCTURE INTO DIVISIONS
    # ─────────────────────────────────────────────────────────────────────────
    if ("flag_capitanias_abolished" in laws
            and "flag_divisions_restructured" not in laws
            and _holds_war(state)):

        cards.append({
            "id": "mil_restructure_divisions",
            "type": "initiative",
            "deck": "party",
            "category": "Military Reform",
            "title": "Restructure the Army into Divisions",
            "ministry_required": "war",
            "text": (
                "Spain's army has no coherent divisional structure — regiments and brigades exist "
                "in a tangle of competing jurisdictions inherited from the nineteenth century. "
                "Reorganising into eight proper infantry divisions under a unified command structure "
                "is a prerequisite for any modern military effectiveness.\n\n"
                "In the short term it creates chaos. Officers don't know their new roles. "
                "Units are shuffled across regions. Readiness drops temporarily. "
                "In the medium term, it creates an army the Republic can actually direct."
            ),
            "base_weight": 25,
            "options": [
                {
                    "text": "Issue the restructuring order.",
                    "tooltip": "Short-term readiness drop. Long-term efficiency and reform progress gain.",
                    "success": {
                        "msg": "The reorganisation order is issued. Eight divisions replace the old structure. "
                               "For the first three months the army is in administrative chaos — "
                               "officers reassigned, units redeployed, supply chains rerouted. "
                               "Gradually, a more coherent structure begins to emerge.",
                        "effects": {
                            "add_law": "flag_divisions_restructured",
                            "army_reform_progress": 25,
                            "army_readiness": -15,
                            "army_efficiency": 10,
                            "budget_int": -2,
                        }
                    }
                },
                {
                    "text": "Delay. Stability first.",
                    "tooltip": "Wait. The card remains.",
                    "success": {
                        "msg": "You postpone the restructuring. The old structure persists.",
                        "effects": {}
                    }
                }
            ]
        })

    # ─────────────────────────────────────────────────────────────────────────
    # 3. CLOSE THE ACADEMIA GENERAL MILITAR (ZARAGOZA)
    # ─────────────────────────────────────────────────────────────────────────
    if ("flag_divisions_restructured" in laws
            and "flag_zaragoza_closed" not in laws
            and _holds_war(state)):

        # Name the director — historically Francisco Franco
        zaragoza_director = "General Franco"

        cards.append({
            "id": "mil_close_zaragoza",
            "type": "initiative",
            "deck": "party",
            "category": "Military Reform",
            "title": "Close the Academia General Militar",
            "ministry_required": "war",
            "text": (
                f"The Academia General Militar in Zaragoza is directed by {zaragoza_director}. "
                "It trains officers in the traditions of the colonial campaigns — "
                "loyalty to the Army as an institution above loyalty to any elected government. "
                "Its graduates are the future officer corps.\n\n"
                "Closing it — folding officer training into a reformed academy under direct "
                "War Ministry control — severs the pipeline of the old culture. "
                f"{zaragoza_director} has already written two protest memos about the reform programme.\n\n"
                "This is the most politically explosive step yet. "
                "The right will treat it as a declaration of war on the officer class."
            ),
            "base_weight": 20,
            "options": [
                {
                    "text": "Close it. Officer training belongs to the Republic.",
                    "tooltip": "Maximum officer resentment. Franco is humiliated and will remember it. "
                               "Long-term coup risk falls significantly. Reform chain complete.",
                    "success": {
                        "msg": f"The closure decree is issued. {zaragoza_director} is relieved of his post "
                               "and assigned to a garrison command in the Canary Islands. "
                               "The right erupts in denunciation. The Republican press celebrates. "
                               "A new officer training programme under War Ministry supervision is established.",
                        "effects": {
                            "add_law": "flag_zaragoza_closed",
                            "army_officer_loyalty": -20,
                            "army_reform_progress": 30,
                            "army_zaragoza_closed": True,
                            "coalition_stability": -10,
                            "modify_relation": {
                                "source": gd.PARTY_DLR,
                                "target": gd.PARTY_AR,
                                "amount": -15
                            },
                            "modify_relation_2": {
                                "source": gd.PARTY_PRR,
                                "target": gd.PARTY_AR,
                                "amount": -12
                            },
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {gd.PARTY_AR: 0.04, gd.PARTY_PSOE: 0.02}
                            },
                            "demographic_shift_2": {
                                "group": "bourgeoisie",
                                "changes": {gd.PARTY_CEDA: 0.05, gd.PARTY_MON: 0.03}
                            }
                        }
                    }
                },
                {
                    "text": "Suspend intake instead. A softer step.",
                    "tooltip": "Halts new officer training in the old tradition without the full provocation. "
                               "Partial reform progress.",
                    "success": {
                        "msg": f"New intake is suspended. The Academia continues to function "
                               "but takes no new cadets. It will wither over several years "
                               "rather than be closed outright. The right protests, but less violently.",
                        "effects": {
                            "add_law": "flag_zaragoza_closed",
                            "army_officer_loyalty": -10,
                            "army_reform_progress": 15,
                            "coalition_stability": -5,
                        }
                    }
                }
            ]
        })

    # ─────────────────────────────────────────────────────────────────────────
    # 4. CREATE GUARDIA DE ASALTO (Interior Ministry, any reform progress)
    # ─────────────────────────────────────────────────────────────────────────
    if (_holds_interior(state)
            and "flag_guardia_asalto_created" not in laws
            and _reform_progress(state) >= 15):

        cards.append({
            "id": "mil_guardia_asalto",
            "type": "initiative",
            "deck": "party",
            "category": "Military Reform",
            "title": "Create the Guardia de Asalto",
            "ministry_required": "interior",
            "text": (
                "The Guardia Civil is not a republican institution. Its loyalty is to order "
                "as defined by the old regime, and its sympathies are openly conservative. "
                "The Republic needs its own paramilitary police — one recruited under the new "
                "government, loyal to republican institutions, and trained for urban crowd control "
                "rather than rural repression.\n\n"
                "The Guardia de Asalto: a force of 10,000, armed with modern equipment, "
                "recruited from the left and centre. It will change the balance on the streets."
            ),
            "base_weight": 30,
            "options": [
                {
                    "text": "Establish and fund the Guardia de Asalto.",
                    "tooltip": "Creates a pro-Republic paramilitary police. "
                               "Reduces Guardia Civil's relative power. Budget cost.",
                    "success": {
                        "msg": "The Guardia de Asalto is established by decree. "
                               "Recruiting begins immediately — targeting urban workers and veterans "
                               "with republican sympathies. Within months, units are deployed "
                               "in Madrid, Barcelona, Seville, and Valencia. "
                               "The Guardia Civil watches with deep suspicion.",
                        "effects": {
                            "add_law": "flag_guardia_asalto_created",
                            "assault_guard_created": True,
                            "budget_int": -2,
                            "public_order": 5,
                            "army_officer_loyalty": -5,
                            "modify_relation": {
                                "source": gd.PARTY_PSOE,
                                "target": gd.PARTY_AR,
                                "amount": 8
                            },
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {gd.PARTY_AR: 0.02, gd.PARTY_PSOE: 0.01}
                            }
                        }
                    }
                }
            ]
        })

    return cards
