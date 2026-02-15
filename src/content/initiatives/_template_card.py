import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
import content.game_data as gd
import random # Nützlich für dynamische Effekte

def get_initiatives(state):
    cards = []
    
    # ==============================================================================
    # --- KARTEN-TEMPLATE: VOLLSTÄNDIGES BEISPIEL ---
    # ==============================================================================
    
    # --- Schritt 1: Bedingungen für die gesamte Karte (Optional) ---
    # Wann soll diese Karte überhaupt im Deck auftauchen?
    
    # A) DATUMS-BEDINGUNGEN
    is_after_1932 = state.date['year'] >= 1932
    is_winter = state.date['month'] in [12, 1, 2]
    
    # B) STAT-BEDINGUNGEN (Metriken)
    is_unstable = state.metrics['coalition_stability'] < 40
    is_disorder = state.metrics['public_order'] < 50
    
    # C) GESETZES-BEDINGUNGEN (Was wurde schon verabschiedet?)
    has_land_reform = "law_agrarian_reform" in state.passed_laws
    
    # D) REGIERUNGS-BEDINGUNGEN
    is_minority_gov = state.government['is_minority']
    is_psoe_in_coalition = gd.PARTY_PSOE in state.government['coalition']
    
    # E) PARTEI-BEDINGUNGEN (Wer ist der Spieler?)
    is_player_socialist = state.player_party == gd.PARTY_PSOE
    
    # F) WIRTSCHAFTS-BEDINGUNGEN
    is_depression = state.economy['global_economy_state'] == "Great Depression"
    has_high_unemployment = state.economy['unemployment'] > 20.0
    
    # G) MILITÄR-BEDINGUNGEN
    has_disloyal_officers = state.military['army_peninsular']['officer_loyalty'] < 25

    # Beispiel-Kombination:
    if is_disorder and has_land_reform and not is_winter:
        
        # --- Schritt 2: Karten-Grundstruktur ---
        card = {
            # -- Metadaten --
            "id": "template_advanced_001",
            "type": "initiative", 
            "deck": "state",
            "category": "Template",
            "title": "Universal-Template",
            "text": "Dieses Template zeigt alle Möglichkeiten.",
            "base_weight": 10,
            "options": []
        }

        # --- Schritt 3: Optionen hinzufügen (können eigene Bedingungen haben) ---
        
        # --- Option A: Komplexe Option ---
        # Bedingung für die Option: Nur wenn Budget über 20
        if state.economy['budget_int'] > 20:
            card['options'].append({
                "text": "Komplexe Aktion (mit Zufall)",
                "tooltip": "Diese Option nutzt alle möglichen Effekte.",
                "base_chance": 70,
                "modifiers": {"public_order": 0.5},
                
                "success": {
                    "msg": "Erfolg! Es passierten viele Dinge.",
                    "effects": {
                        # --- ALLE MÖGLICHEN EFFEKTE (STATISCH) ---
                        
                        # -- STATS (Metrics, Society, Economy) --
                        "public_order": 10,
                        "coalition_stability": 5,
                        "workers_urban": 10,
                        "clergy": -5,
                        "budget_int": -2,
                        "unemployment": -0.5,
                        
                        # -- WAHLEN & DEMOGRAPHIE --
                        "demographic_shift": {"group": "workers_urban", "changes": {gd.PARTY_PSOE: 0.05, gd.PARTY_CEDA: -0.02}},
                        "trigger_election": True,
                        
                        # -- PARTEI & REGIERUNG --
                        "modify_faction": {"tag": "left", "amount": -15},
                        "modify_relation": {"source": gd.PARTY_PSOE, "target": gd.PARTY_AR, "amount": 10},
                        "remove_party": gd.PARTY_DLR,
                        "transfer_ministry": gd.PARTY_AR,
                        "set_coalition": [gd.PARTY_PSOE, gd.PARTY_AR],
                        "start_negotiation": True,
                        "trigger_schism": "revolutionary", # Faction Key
                        "trigger_confidence_vote": True,
                        
                        # -- GESETZE & SPIELFORTSCHRITT --
                        "add_law": "law_my_special_law",
                        "game_over": "You have been overthrown in a coup!" # Zeigt Game Over Screen
                    }
                },
                "failure": { "msg": "Gescheitert.", "effects": {"public_order": -10} }
            })

        # --- Option B: Option mit DYNAMISCHEN Effekten ---
        
        # HIER DIE FORMEL:
        # Wir berechnen den Effekt-Wert, bevor wir die Option definieren.
        # Beispiel: Bonus für Public Order ist höher, wenn das Budget voll ist.
        budget_bonus = 0
        if state.economy['budget_int'] > 50:
            budget_bonus = 10 # Bonus von 10, wenn wir reich sind
        
        # Beispiel: Arbeitslosigkeit senken, kostet mehr bei hoher Arbeitslosigkeit
        cost_for_jobs = int(state.economy['unemployment'] / 5) # z.B. 4 Budget bei 20% Arbeitslosigkeit
        
        card['options'].append({
            "text": "Dynamische Aktion (Formel-basiert)",
            "tooltip": f"Kostet {cost_for_jobs} Budget. Gibt +{5 + budget_bonus} Public Order.",
            "success": {
                "msg": "Die Effekte wurden basierend auf dem aktuellen Zustand berechnet.",
                "effects": {
                    # HIER WERDEN DIE VARIABLEN EINGESETZT:
                    "public_order": 5 + budget_bonus,
                    "budget_int": -cost_for_jobs,
                    
                    # Ternary Operator für bedingte Effekte:
                    "demographic_shift": {
                        "group": "bourgeoisie",
                        "changes": {gd.PARTY_CEDA: 0.05}
                    } if state.society['bourgeoisie'] < 50 else {
                        "group": "bourgeoisie",
                        "changes": {gd.PARTY_PRR: 0.05}
                    }
                }
            }
        })
        
        cards.append(card)
        
    return cards