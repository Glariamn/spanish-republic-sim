import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from content.base_event import GameEvent
import content.game_data as gd
import random

class LerrouxExitEvent(GameEvent):
    def should_trigger(self):
        is_date = self.state.date['year'] == 1931 and self.state.date['month'] == 10
        # Bedingung: Lerroux' Partei (PRR) muss überhaupt in der Regierung sein!
        is_in_gov = gd.PARTY_PRR in self.state.government['coalition']
        return is_date and is_in_gov
    
    def get_data(self):
        return {
            "id": "1931_lerroux_exit",
            "title": "The Radical Rupture",
            "date_str": "Oktober 1931",
            "text": """
            **The Coalition is fracturing.**
            
            Alejandro Lerroux and his Radical Republican Party (PRR) can no longer support the government. 
            They cite the "excessive influence of the Socialists" and the aggressive anti-clerical articles in the new Constitution (Article 26).
            
            Lerroux demands that the Socialists (PSOE) leave the government, or he will.
            """,
            "choices": [
                {
                    "text": "Let Lerroux go. Keep the Socialists.",
                    "tooltip": "Historical Choice. Maintains the Left-Wing coalition but loses the Center.",
                    "success": {
                        "msg": "Lerroux resigns. The Radicals move to the opposition, joining the right-wing obstruction.",
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
                    "tooltip": "A massive betrayal. Will cause a General Strike.",
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
class Constitution26Event(GameEvent):
    def should_trigger(self):
        # wurde gerade Artikel 26 verabschiedet?
        passed = "const_art_26_radical" in self.state.passed_laws \
            or "const_art_26_moderate" in self.state.passed_laws

        # PRR oder DLR müssen in der Regierung sein
        in_gov = gd.PARTY_PRR in self.state.government['coalition'] \
            or gd.PARTY_DLR in self.state.government['coalition']

        return passed and in_gov and not self.state.flags.get("event_26_fired")
    
    def get_data(self):
        return {
            "id": "1931_constitution_26",
            "title": "The Religious Question (Article 26)",
            "date_str": "Oktober 1931",
            "text": """
            **The Constitution is being drafted.**
            
            The debate has reached **Article 26**, which proposes:
            1. Complete separation of Church and State.
            2. Banning Jesuits.
            3. Ending state payment of priests.
            
            The Conservative Republicans (**DLR**) and Radicals (**PRR**) warn this is "political suicide". 
            The Socialists (**PSOE**) and the Left-Republicans (**AR**) demand a secular state now.
            
            Prime Minister Alcalá-Zamora (DLR) threatens to resign if this passes.
            """,
            "choices": [
                {
                    "text": "Push Article 26 fully! (Secular State)",
                    "tooltip": "Historic Path. Azaña's famous speech: 'Spain has ceased to be Catholic'.",
                    "success": {
                        "msg": "The Article passes! Alcalá-Zamora and Maura resign in protest. Azaña must lead.",
                        "effects": {
                            # DLR (Rechts-Republikaner) verlassen die Regierung
                            "remove_party": gd.PARTY_DLR,
                            
                            "modify_relation": {"source": gd.PARTY_DLR, "target": gd.PARTY_AR, "amount": -30},
                            "modify_relation_2": {"source": gd.PARTY_PRR, "target": gd.PARTY_AR, "amount": -15}, # Hack für 2. Relation
                            "coalition_stability": 10,
                            
                            "society": {"clergy": -40, "aristocracy": -20, "workers_urban": 15},
                            "modify_faction": {"tag": "left", "amount": -20}, 
                            
                            "transfer_ministry": gd.PARTY_DLR # Deren Ministerien werden frei/verteilt
                        }
                    }
                },
                {
                    "text": "Compromise to save the Coalition.",
                    "tooltip": "Water down the article. Keeps DLR, but enrages the Socialists.",
                    "success": {
                        "msg": "We dilute the text. The Church keeps some privileges. The Socialists feel betrayed.",
                        "effects": {
                            "coalition_stability": 5, 
                            "modify_relation": {"source": gd.PARTY_PSOE, "target": gd.PARTY_AR, "amount": -25},
                            "modify_faction": {"tag": "left", "amount": 30}, 
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {gd.PARTY_PSOE: -0.05, gd.PARTY_PCE: 0.03} 
                            }
                        }
                    }
                }
            ]
        }

class ConstitutionRatifiedEvent(GameEvent):
    def should_trigger(self):
        # Historisch: 9. Dezember 1931
        is_date = self.state.date['year'] == 1931 and self.state.date['month'] == 12
        return is_date

    def get_data(self):
        laws = self.state.passed_laws
        
        # --- Dynamischen Verfassungstext bauen ---
        const_summary = []
        
        # 1. Frauenwahlrecht
        if "const_suffrage" in laws:
            const_summary.append("• **Universal Suffrage:** Full voting rights for women were enshrined, despite fears from the left.")
        elif "const_suffrage_limited" in laws:
            const_summary.append("• **Limited Suffrage:** Women's voting rights were postponed, angering feminists but calming republican fears.")
        else:
            const_summary.append("• **Male Suffrage:** The traditional voting system remains unchanged.")
            
        # 2. Die Kirchenfrage
        if "const_art_26_radical" in laws:
            const_summary.append("• **Article 26 (Radical):** The state is strictly secular. Jesuits have to register with the government, effectively making them a secular organization. The Church is furious.")
        elif "const_art_26_moderate" in laws:
            const_summary.append("• **Article 26 (Moderate):** A compromise secularism. The Church loses state funding but keeps its schools.")
        else:
            const_summary.append("• **Religious Tolerance:** The Republic avoided a harsh break with the Vatican.")

        # 3. Eigentum
        if "const_art_44_social" in laws:
            const_summary.append("• **Article 44:** Property can be expropriated for social utility. Landowners are terrified.")
        elif "const_art_44_liberal" in laws:
            const_summary.append("• **Private Property:** Strict protections for private property remain, disappointing landless peasants.")

        summary_text = "\n".join(const_summary)

        return {
            "id": "1931_constitution_ratified",
            "title": "La Constitución de 1931",
            "date_str": "9. Dezember 1931",
            "text": f"""
            **The Cortes Constituyentes have finalized their work.**
            
            After months of grueling debate, the new Constitution of the Spanish Republic is ratified. It defines Spain as a "democratic republic of workers of all classes". 
            
            Here is the foundation of our new state:
            {summary_text}
            
            With the Constitution active, the Provisional Government must step down. **Niceto Alcalá-Zamora** has been proposed as the first President of the Republic (Head of State), leaving the role of Head of Government open.
            """,
            "choices": [
                {
                    "text": "Elect Alcalá-Zamora as President and form a new regular government.",
                    "tooltip": "Triggers a new coalition negotiation phase. Alcalá-Zamora vacates his ministry.",
                    "success": {
                        "msg": "Alcalá-Zamora moves to the Presidential Palace. The Republic is now fully constitutional!",
                        "effects": {
                            "public_order": 10,
                            "coalition_stability": 20,
                            # Alcalá-Zamora war meist im Innenministerium oder Präsident. Wir räumen sein Amt.
                            "vacate_ministry_if_dlr": True, # (Müssten wir ggf. in mechanics abfangen, oder wir triggern einfach Wahlen)
                            "trigger_election": False, # Keine Neuwahl des Parlaments, ABER...
                            "start_negotiation": True, # ...eine neue Regierungsbildung!
                            "add_law": "constitution_active"
                        }
                    }
                }
            ]
        }