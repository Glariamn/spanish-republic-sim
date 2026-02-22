import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from content.base_event import GameEvent
import content.game_data as gd
import random

# --- 1. DER KLASSIKER (Wahl-Nacht) ---
class AprilElectionNightEvent(GameEvent):
    def should_trigger(self):
        # Dieses Event wird nur beim Spielstart durch die ID ausgelöst
        # und nicht im normalen monatlichen Tick geprüft.
        return False # Wird nie automatisch ausgelöst
    def get_data(self):
        return {
            "id": "1931_election_night",
            "title": "La Noche Electoral (Election Night)",
            "date_str": "12. April 1931",
            "text": """
            
            In the rural countryside, the Monarchist candidates have won, backed by the 'Caciques'.
            But in the provincial capitals - Madrid, Barcelona, Valencia - the Republican coalition has swept the vote!
            
            Crowds are gathering at the Puerta del Sol. The King's advisors are panicked.
            **What is your strategy for the transition?**
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

# --- 2. CATALAN DECLARATION (14. April 1931) ---

class MaciaDeclarationEvent(GameEvent):
    def should_trigger(self):
        is_date = self.state.date['year'] == 1931 and self.state.date['month'] == 4
        # Triggers as second event
        has_started = "1931_election_night" in self.state.get('event_history', [])
        return is_date and not has_started
    
    def get_data(self):
        return {
            "id": "1931_macia_declaration",
            "title": "The Catalan Republic?",
            "date_str": "14. April 1931",
            "text": """
            **Crisis in Barcelona!**
            
            **Francesc Macià** has proclaimed the 'Catalan Republic' from the balcony of the Generalitat.
            The Army is furious at this threat to unity.
            """,
            "choices": [
                {
                    "text": "Send Ministers to negotiate (Promise Autonomy).",
                    "tooltip": "Secure the Catalan vote, but anger the Centralists.",
                    "base_chance": 80,
                    "modifiers": {"diplomacy": 0.5},
                    "success": {
                        "msg": "Macià accepts the 'Generalitat'. The Catalan Left (ERC) backs the government.",
                        "effects": {
                            "coalition_stability": 10,
                            "catalans": 20,
                            "army_officer_loyalty": -10,
                            "industrial_output": 2, 
                            "demographic_shift": {
                                "group": "bourgeoisie",
                                "changes": { gd.PARTY_ERC: 0.10, gd.PARTY_AR: 0.03 }
                            },
                            "demographic_shift_2": {
                                "group": "workers_urban",
                                "changes": { gd.PARTY_ERC: 0.05 }
                            },
                            "modify_relation": {
                                "source": gd.PARTY_ERC, 
                                "target": gd.PARTY_AR, 
                                "amount": 20 
                            }
                        }
                    },
                    "failure": {
                        "msg": "He refuses. Tensions rise.",
                        "effects": {"coalition_stability": -10}
                    }
                },
                {
                    "text": "Denounce him as a traitor!",
                    "tooltip": "Pleases the Right/Army. Alienates Catalans.",
                    "success": {
                        "msg": "Macià backs down, but the Catalans feel betrayed.",
                        "effects": {
                            "catalans": -30,
                            "army_officer_loyalty": 15,
                            "modify_faction": {"tag": "left", "amount": 10},
                            "demographic_shift": {
                                "group": "bourgeoisie",
                                "changes": { gd.PARTY_LLIGA: 0.10, gd.PARTY_ERC: -0.05 }
                            }
                        }
                    }
                }
            ]
        }

# --- 3. NEU: DER HIRTENBRIEF (Mai 1931) ---
class CardinalSeguraEvent(GameEvent):
    def should_trigger(self):
        is_date = self.state.date['year'] == 1931 and self.state.date['month'] == 5
        return is_date

    def get_data(self):
        return {
            "id": "1931_cardinal_segura",
            "title": "The Primate's Fire",
            "date_str": "1. Mai 1931",
            "text": """
            **Cardinal Segura** has urged Catholics to vote against the 'enemies of Jesus'.
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