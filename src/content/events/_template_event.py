import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from content.base_event import GameEvent
import content.game_data as gd
import random

class TemplateEvent(GameEvent):
    """
    Template für ein dynamisches, zustandsbasiertes Event.
    Wird jeden Monat im `process_monthly_tick` geprüft.
    """
    
    # --- Schritt 1: Trigger-Bedingungen definieren ---
    def should_trigger(self):
        """
        Gibt 'True' zurück, wenn dieses Event ausgelöst werden soll.
        Hier kommt die Logik rein, die entscheidet, OB das Event passiert.
        """
        
        # --- Beispiele für Bedingungen (wähle/kombiniere die passenden) ---
        
        # A) DATUM
        is_correct_year = self.state.date['year'] == 1932
        is_summer = self.state.date['month'] in [6, 7, 8]
        
        # B) SPIELER-AKTIONEN
        has_required_law = "law_agrarian_reform" in self.state.passed_laws
        
        # C) POLITISCHER ZUSTAND
        is_gov_unstable = self.state.metrics['coalition_stability'] < 30
        is_player_leading = self.state.ministries['president']['party'] == self.state.player_party
        
        # D) SOZIALER ZUSTAND
        are_workers_angry = self.state.society['workers_urban'] < 40
        
        # E) ZUFALLSFAKTOR (um Events nicht bei jeder Erfüllung zu triggern)
        chance_roll = random.randint(1, 100) <= 20 # 20% Chance pro Monat, wenn Bedingungen stimmen
        
        # Beispiel-Kombination:
        # Feuert nur, wenn die Arbeiter wütend sind UND der Spieler die Regierung führt UND mit 20% Wahrscheinlichkeit
        if are_workers_angry and is_player_leading and chance_roll:
            return True
            
        return False

    # --- Schritt 2: Event-Daten & Optionen definieren ---
    def get_data(self):
        """
        Gibt das Dictionary zurück, das app.py zum Anzeigen des Events braucht.
        Hier kommt der Inhalt rein: Text, Buttons, Effekte.
        """
        
        # --- Dynamische Textelemente vorbereiten (Optional) ---
        # Du kannst hier Werte aus dem State holen, um den Text anzupassen.
        unemployment_rate = self.state.economy['unemployment']
        angry_faction_name = "The Left Wing" # Fallback
        if 'psoe_caballeristas' in self.state.my_factions:
            angry_faction_name = self.state.my_factions['psoe_caballeristas']['name']

        
        # --- Grundstruktur des Events ---
        event_data = {
            "id": "template_dynamic_event_001", # Eindeutige ID
            "title": "Eine Krise braut sich zusammen",
            "text": f"""
                Die Arbeitslosigkeit liegt bei {unemployment_rate}%. 
                {angry_faction_name} Ihrer Partei fordert radikale Maßnahmen.
                """,
            "choices": []
        }
        
        # --- Optionen hinzufügen ---
        
        # --- Option A: Bedingte Option (nur für bestimmte Partei) ---
        if self.state.player_party == gd.PARTY_AR:
            event_data['choices'].append({
                "text": "Als Reformer handeln...",
                "success": { "msg": "...", "effects": { "public_order": 5 } }
            })

        # --- Option B: Option mit dynamischen Effekten ---
        # Berechne den Effekt-Wert basierend auf dem State
        stability_hit = -20 if self.state.government['is_minority'] else -10

        event_data['choices'].append({
            "text": "Einen Kompromiss eingehen.",
            "tooltip": f"Wird die Koalitionsstabilität um {stability_hit} senken.",
            "success": {
                "msg": "Ein fauler Kompromiss wurde gefunden.",
                "effects": {
                    "coalition_stability": stability_hit # Die berechnete Variable
                }
            }
        })
        
        # --- Option C: Option mit Zufall ---
        event_data['choices'].append({
            "text": "Eine riskante Rede halten.",
            "base_chance": 50,
            "modifiers": {"public_order": 0.5},
            "success": {
                "msg": "Die Rede hat die Massen begeistert!",
                "effects": {
                    "demographic_shift": {"group": "workers_urban", "changes": {self.state.player_party: 0.05}}
                }
            },
            "failure": {
                "msg": "Die Rede hat die Situation verschlimmert.",
                "effects": {"public_order": -10}
            }
        })
        
        return event_data