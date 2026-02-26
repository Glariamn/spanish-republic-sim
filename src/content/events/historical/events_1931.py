import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from content.base_event import GameEvent
import content.game_data as gd
import random

# --- 1. DER KLASSIKER (Wahl-Nacht) ---
class AprilElectionNightEvent(GameEvent):
    EVENT_ID = "1931_election_night"
    def should_trigger(self):
        # Dieses Event wird nur beim Spielstart durch die ID ausgelöst
        # und nicht im normalen monatlichen Tick geprüft.
        return False # Wird nie automatisch ausgelöst
    def get_data(self):
        return {
            "id": "1931_election_night",
            "title": "La Noche Electoral (Election Night)",
            "date_str": "12. April 1931",
            "text": """***Municipal Elections***

            Polling stations across Spain opened on April 12 for elections to 80,472 council seats, 
            conducted under the antiquated 1907 census suffrage law that disproportionately favored 
            rural property owners and landowners. 

            The republican-socialist Conjunción alliance, forged in the San Sebastián Pact of August 1930, 
            secured 9,385 seats nationwide against the monarchists' 16,673, reflecting a raw national 
            vote split of roughly 4.6 million for the opposition to 5.1 million for the government slate. 

            Yet the true drama unfolded in the cities: the Conjunción claimed majorities in 
            41 of Spain's 50 provincial capitals, with staggering margins like 50,962 votes in Madrid 
            (three times the monarchist one) and over 104,000 in Barcelona (a fourfold victory). 

            Low rural turnout preserved monarchist strongholds in the countryside, but urban crowds 
            by evening were already murmuring '¡Viva la República!' as results tallied, interpreting 
            the capital sweeps as a clear plebiscite against King Alfonso XIII. 

            Within the Pact, socialists like Indalecio Prieto urged immediate radical action, 
            straining ties with more cautious conservative republicans such as Niceto Alcalá-Zamora.
            """,
            "choices": [
                {
                    "text": "Mobilize the Streets! Demand abdication.",
                    "tooltip": "Risky. Might provoke the Army.",
                    "base_chance": 40,
                    "modifiers": {"public_order": 0.5, "army_loyalty": -0.8},
                    "success": {
                        "msg": "The sheer size of the crowds terrifies the Palace! The King packs his bags.",
                        "effects": {
                            "public_order": 10,
                            "army_loyalty": -10,
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {
                                    gd.PARTY_PSOE: 0.05,
                                }
                            },
                            "demographic_shift_2": { # Workaround
                                "group": "bourgeoisie",
                                "changes": { gd.PARTY_AR: 0.05 } 
                            }
                        }
                    },
                    "failure": {
                        "msg": "The Civil Guard opens fire! A bloodbath.",
                        "effects": {
                            "public_order": -20,
                            "army_loyalty": 5,
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": { gd.PARTY_PSOE: -0.05 }
                            }
                        }
                    }
                },
                {
                    "text": "Negotiate a peaceful transfer.",
                    "tooltip": "Safer, but slower.",
                    "base_chance": 70,
                    "modifiers": {"army_loyalty": 0.3},
                    "success": {
                        "msg": "Admiral Aznar admits defeat. The King leaves quietly.",
                        "effects": {
                            "army_loyalty": 5, 
                            "public_order": -5,
                            "demographic_shift": {
                                "group": "bourgeoisie",
                                "changes": {
                                    gd.PARTY_DLR: 0.05,
                                    gd.PARTY_PRR: 0.05,
                                    gd.PARTY_AR: -0.02 
                                }
                            }
                        } 
                    },
                    "failure": {
                        "msg": "The King delays his departure.",
                        "effects": {
                            "public_order": -15,
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": { gd.PARTY_PCE: 0.05, gd.PARTY_PSOE: 0.05 }
                            }
                        }
                    }
                }
            ]
        }
    
class ProclamationOfSecondRepublicEvent(GameEvent):
    EVENT_ID = "1931_proclamation_of_second_republic"
    def should_trigger(self):
        # Chained directly from MaciaDeclarationEvent via app.py — never fires via dynamic tick
        return False

    def get_data(self):
        player = self.state.player_party
        p_name = gd.PARTIES.get(player, {}).get("name", "our party")

        return {
            "id": "1931_proclamation_of_second_republic",
            "title": "¡Viva la República!",
            "date_str": "14 April 1931",
            "text": """The morning of April 14 unfolds with electric tension. At 12:30 PM, Alcalá-Zamora steps onto the balcony of the Interior Ministry and proclaims the Second Spanish Republic. The tricolor — red, yellow, and purple — rises over government buildings across Madrid. The crowds erupt.

            King Alfonso XIII, having lost the backing of the army, departs the Palacio Real by motorcar and boards a cruiser at Cartagena. He leaves no abdication — only a manifesto lamenting the "loss of the affection of the people."

            No shots are fired. General Sanjurjo stands neutral. The anarchists chant in the streets, though CNT militants eye the bourgeois pact with suspicion.

            The Republic is born. What happens next is up to you.""",
            "choices": [
                {
                    "text": "Mobilise our supporters. Be visible on the streets.",
                    "tooltip": "Your cadres and affiliated unions take to the streets. "
                               "Claim the moment for the left before the bourgeois republicans can frame it.",
                    "success": {
                        "msg": f"{p_name} cadres flood the streets of Madrid and the provincial capitals. "
                               "The Republic is proclaimed, but the left is already staking its claim "
                               "to what it means. Zamora and Lerroux watch with unease.",
                        "effects": {
                            "public_order": -5,
                            "workers_urban": 12,
                            "workers_rural": 5,
                            "coalition_stability": -10,
                            "modify_relation": {
                                "source": gd.PARTY_DLR,
                                "target": player,
                                "amount": -8
                            },
                            "modify_relation_2": {
                                "source": gd.PARTY_PRR,
                                "target": player,
                                "amount": -5
                            },
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {player: 0.03, gd.PARTY_PCE: -0.01}
                            }
                        }
                    }
                },
                {
                    "text": "Keep discipline. Back the Pact — this moment belongs to all of us.",
                    "tooltip": "Historical path for most parties. Let the proclamation be a broad republican moment. "
                               "You gain goodwill with the coalition centre. Your own base is less energised.",
                    "success": {
                        "msg": "Your party holds its cadres back from provocative displays. "
                               "Zamora steps onto the balcony. The transition is orderly. "
                               "The Pact holds its image of unity — for now.",
                        "effects": {
                            "public_order": 10,
                            "coalition_stability": 12,
                            "workers_urban": 3,
                            "modify_relation": {
                                "source": gd.PARTY_DLR,
                                "target": player,
                                "amount": 10
                            },
                            "modify_relation_2": {
                                "source": gd.PARTY_PRR,
                                "target": player,
                                "amount": 6
                            },
                            "demographic_shift": {
                                "group": "bourgeoisie",
                                "changes": {gd.PARTY_DLR: 0.03, gd.PARTY_AR: 0.02}
                            }
                        }
                    }
                }
            ]
        }

# --- 2. CATALAN DECLARATION (14. April 1931) ---

class MaciaDeclarationEvent(GameEvent):
    EVENT_ID = "1931_macia_declaration"
    def should_trigger(self):
        is_date = self.state.date['year'] == 1931 and self.state.date['month'] == 4
        # Triggers as second event
        has_started = "1931_election_night" in self.state.get('event_history', [])
        return is_date and not has_started
    
    def get_data(self):
        player = self.state.player_party
        return {
            "id": "1931_macia_declaration",
            "title": "The Catalan Republic?",
            "date_str": "14. April 1931",
            "text": """
            Hours after Zamora's proclamation in Madrid, Francesc Macià steps onto the balcony of the Generalitat in Barcelona and declares a *República Catalana* within an Iberian Federation. The crowd below roars. The telegrams arriving in Madrid are less celebratory.

            The army generals are beside themselves — they see separatism, not autonomy. Lerroux and two other ministers are already boarding a train to Barcelona to negotiate. There is no question that Macià will have to retract the declaration. The question is what he gets in return, and whose idea it looks like.

            Your party needs to decide its position before Lerroux arrives.
            """,
            "choices": [
                {
                    "text": "Support the autonomy negotiation. Back Lerroux's mission.",
                    "tooltip": "Lerroux and two ministers are already on a train to Barcelona. "
                               "Your backing within cabinet strengthens their hand.",
                    "success": {
                        "msg": "Macià accepts the Generalitat as a provisional institution pending "
                               "a proper Statute of Autonomy. Your support for the deal is noted in Barcelona. "
                               "The Catalan left will remember who stood with them.",
                        "effects": {
                            "coalition_stability": 8,
                            "catalans": 18,
                            "army_officer_loyalty": -8,
                            "modify_relation": {
                                "source": gd.PARTY_ERC,
                                "target": player,
                                "amount": 15
                            },
                            "modify_relation_2": {
                                "source": gd.PARTY_PRR,
                                "target": player,
                                "amount": 8
                            },
                            "demographic_shift": {
                                "group": "bourgeoisie",
                                "changes": {gd.PARTY_ERC: 0.06, gd.PARTY_AR: 0.02}
                            }
                        }
                    },
                    "failure": {
                        "msg": "Macià refuses the initial terms. Negotiations drag on through the night. "
                               "A compromise is eventually reached, but it costs political capital.",
                        "effects": {
                            "coalition_stability": -5,
                            "catalans": 5
                        }
                    }
                },
                {
                    "text": "Stay out of it. Let Lerroux handle Barcelona.",
                    "tooltip": "Not your fight — or your constituency. "
                               "The Catalan question is for the centrists to solve.",
                    "success": {
                        "msg": "Your party makes no public statement. Lerroux secures the deal without you. "
                               "The Catalan left notes your absence.",
                        "effects": {
                            "coalition_stability": 5,
                            "catalans": 8,
                            "army_officer_loyalty": -5
                        }
                    }
                },
                {
                    "text": "Push back. Spain's territorial integrity is not negotiable.",
                    "tooltip": "Hardline position. You align with the army's view and lose Catalan goodwill permanently. "
                               "Only available if your coalition partner DLR or PRR holds this line too.",
                    "requires_party": [gd.PARTY_DLR, gd.PARTY_PRR],
                    "success": {
                        "msg": "Your hardline stance strengthens the negotiators' hand — Macià knows the deal "
                               "could collapse entirely. He accepts limited terms. "
                               "The Catalans feel the concession was forced, not given.",
                        "effects": {
                            "catalans": -20,
                            "army_officer_loyalty": 12,
                            "coalition_stability": -8,
                            "modify_relation": {
                                "source": gd.PARTY_ERC,
                                "target": player,
                                "amount": -20
                            },
                            "modify_relation_2": {
                                "source": gd.PARTY_DLR,
                                "target": player,
                                "amount": 8
                            },
                            "demographic_shift": {
                                "group": "bourgeoisie",
                                "changes": {gd.PARTY_LLIGA: 0.06, gd.PARTY_ERC: -0.04}
                            }
                        }
                    }
                }
            ]
        }
    
class ProvisionalGovernmentEvent(GameEvent):
    EVENT_ID = "1931_provisional_government"
    def should_trigger(self):
        # Chained directly from ProclamationOfSecondRepublicEvent via app.py CHAIN dict
        return False

    def get_data(self):
        player = self.state.player_party

        return {
            "id": "1931_provisional_government",
            "title": "The First Decrees",
            "date_str": "15 April — May 1931",
            "text": """The provisional government's first week produces three decrees: amnesty for the 30,000 political prisoners of the Primo de Rivera years; the tricolor replaces the royal flag; Constituent Cortes elections are set for June 28 under proportional representation.

The cabinet is already fractious. Azaña has opened talks with the senior generals about a voluntary retirement scheme. Caballero is drafting a labor arbitration bill. Zamora is urging everyone to wait until after the elections before changing anything structural.

Your party has limited time and political capital in these first weeks. The decisions you make now about where to spend it will shape what the coalition looks like going into June.""",
            "choices": [
                {
                    "text": "Champion amnesty and free press. Make rights the headline.",
                    "tooltip": "Push to make the amnesty decree and press freedoms the public face "
                               "of the new Republic. Your party gets credit. Less tangible than reform, "
                               "but builds legitimacy across the left and liberal centre.",
                    "success": {
                        "msg": "The amnesty decree passes — 30,000 political prisoners walk free. "
                               "Your party is seen championing it publicly. "
                               "The Republic's first image is one of justice, not class war.",
                        "effects": {
                            "public_order": 8,
                            "coalition_stability": 8,
                            "workers_urban": 6,
                            "workers_rural": 4,
                            "modify_relation": {
                                "source": gd.PARTY_DLR,
                                "target": player,
                                "amount": 6
                            },
                            "modify_relation_2": {
                                "source": gd.PARTY_PRR,
                                "target": player,
                                "amount": 5
                            },
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {player: 0.02}
                            }
                        }
                    }
                },
                {
                    "text": "Press for rapid elections. The sooner we have a real mandate, the better.",
                    "tooltip": "Push cabinet to set June 28 as the earliest feasible election date. "
                               "Your party signals confidence in the ballot box. "
                               "The right grumbles — they need more time to organise.",
                    "success": {
                        "msg": "The June 28 date is confirmed. Your party is identified with "
                               "democratic urgency. The right is still scrambling to organise.",
                        "effects": {
                            "coalition_stability": 5,
                            "public_order": 3,
                            "modify_faction": {"tag": "moderate", "amount": -8},
                            "demographic_shift": {
                                "group": "bourgeoisie",
                                "changes": {gd.PARTY_DLR: 0.02, player: 0.01}
                            }
                        }
                    }
                },
                {
                    "text": "Keep a low profile. Let the government govern.",
                    "tooltip": "Your party takes no loud positions in the first weeks. "
                               "Conserve political capital for what comes next.",
                    "success": {
                        "msg": "The provisional government's decrees pass without drama. "
                               "Your party watches, conserves, and waits.",
                        "effects": {
                            "coalition_stability": 12,
                            "modify_faction": {"tag": "left", "amount": 5}
                        }
                    }
                }
            ]
        }

# --- 3. DER HIRTENBRIEF (Mai 1931) ---
class CardinalSeguraEvent(GameEvent):
    EVENT_ID = "1931_cardinal_segura"
    def should_trigger(self):
        is_date = self.state.date['year'] == 1931 and self.state.date['month'] == 5
        return is_date

    def get_data(self):
        return {
            "id": "1931_cardinal_segura",
            "title": "The Primate's Pastoral Letter",
            "date_str": "1. Mai 1931",
            "text": """
            **Cardinal Segura** has urged Catholics to vote against the 'enemies of Jesus'.

            On May 1, 1931, Cardinal Pedro Segura y Sáenz, Archbishop of Toledo and Primate 
            of Spain, signed a lengthy pastoral letter addressed to the faithful of his 
            archdiocese, published in the Boletín Eclesiástico del Arzobispado de Toledo on 
            May 2 and widely disseminated in the press by May 6-7.

            The document, written amid the shock of the Republic's proclamation, combined a 
            formal call for obedience to constituted authorities with a fervent defense of 
            the monarchy and the Church's historical role in Spain. Segura praised Alfonso XIII 
            for his 'love of religion' and 'services to the patria,' lamenting the sudden 
            change while urging Catholics not to remain passive: 'when the enemies of the 
            reign of Jesus Christ advance resolutely, no Catholic can remain inactive, 
            retired in his honor or dedicated solely to private affairs.'

            He emphasized the Church's duty to defend its rights against perceived threats 
            like secular education, civil marriage, and separation of Church and State, 
            implicitly encouraging mobilization of the faithful without directly calling 
            for rebellion. The tone reflected Segura's rigid intransigence and deep 
            attachment to the old regime, contrasting sharply with more conciliatory 
            voices like Cardinal Vidal i Barraquer of Tarragona, who advocated respect for 
            the new order per Vatican guidance.

            The pastoral provoked immediate outrage among republicans, who viewed it as a 
            veiled incitement against the Republic and a glorification of the fallen 
            monarchy. It contributed to heightened anticlerical tensions, preceding the 
            church burnings of May 10-13 by days, and led the provisional government to 
            request Segura's removal from Spain on May 7. The Vatican, while not endorsing 
            the letter's tone, eventually acquiesced to his exile in June 1931 to ease 
            relations.

            Segura's action deepened the rift between militant Catholicism and the Republic, 
            alienating moderates and reinforcing perceptions of the Church as an irreconcilable 
            opponent of the new regime.

            Republicans demand his expulsion.
            """,
            "choices": [
                {
                    "text": "Expel Cardinal Segura from Spain.",
                    "tooltip": "Enrages the Church, confirms the fears of the wealthy and traditionalists.",
                    "requires_party": [gd.PARTY_PSOE, gd.PARTY_AR, gd.PARTY_PRRS, gd.PARTY_PRR],
                    "success": {
                        "msg": "Segura is exiled. The Vatican is furious.",
                        "effects": {
                            "clergy": -20,
                            "diplomacy_vatican": -40,
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": { gd.PARTY_PRRS: 0.05, gd.PARTY_PSOE: 0.02 }
                            },
                            "tax_revenue_int": -1,
                            "demographic_shift_2": { # Workaround key
                                "group": "bourgeoisie",
                                "changes": {
                                    gd.PARTY_CEDA: 0.05, 
                                    gd.PARTY_DLR: -0.05  
                                }
                            },
                            "modify_faction": {"tag": "center", "amount": 10}
                        }
                    }
                },
                {
                    "text": "Issue a formal protest only.",
                    "tooltip": "Weak response.",
                    "success": {
                        "msg": "We lodge a complaint. The Left is furious at our weakness.",
                        "effects": {
                            "public_order": -15,
                            "clergy": -5,
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {
                                    gd.PARTY_PSOE: -0.03, 
                                    gd.PARTY_PCE: 0.02, # Kommunisten profitieren
                                    gd.PARTY_CNT: 0.01
                                }
                            },
                            "modify_faction": {"tag": "left", "amount": 5}
                        }
                    }
                }
            ]
        }

# --- 4. WAHLEN (Juni 1931) ---
class JuneElectionsEvent(GameEvent):
    EVENT_ID = "1931_june_elections"
    def should_trigger(self):
        # Trigger über das Wahldatum
        next_el = self.state.government.get('next_election_date', {})
        return self.state.date.get('year') == next_el.get('year') and self.state.date.get('month') == next_el.get('month')
    
    def get_data(self):
        return {
            "id": "1931_june_elections",
            "title": "Las Elecciones Constituyentes",
            "date_str": "28. Juni 1931",
            "text": """
            **Spain goes to the polls.**
            For the first time, the Spanish people will freely elect a parliament to draft a new Constitution.
            """,
            "choices": [
                {
                    "text": "Await the Results",
                    "success": {
                        "msg": "The new Cortes Generales have assembled.",
                        "effects": {
                            "trigger_election": True, 
                            "public_order": 5 
                        }
                    }
                }
            ]
        }