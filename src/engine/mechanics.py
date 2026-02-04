import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import random
import content.game_data as gd

def calculate_outcome(base_chance, modifiers, game_state):
    """
    Berechnet die Wahrscheinlichkeit und würfelt.
    
    Args:
        base_chance (int): Grundchance (0-100).
        modifiers (dict): Welche Stats beeinflussen das? 
                          z.B. {'public_order': 0.5} (Order hilft halb stark)
                          z.B. {'army_loyalty': -1.0} (Loyalty schadet voll)
        game_state (session_state): Damit wir auf die aktuellen Werte zugreifen können.
        
    Returns:
        success (bool): Hat es geklappt?
        roll (int): Was wurde gewürfelt?
        final_chance (int): Wie hoch war die Chance am Ende?
        breakdown (list): Text-Erklärung für den Tooltip (Warum war die Chance so?)
    """
    current_chance = base_chance
    breakdown = [f"Base Probability: {base_chance}%"]
    
    # Get the game metrics
    metrics = game_state.metrics
    
    for stat_key, weight in modifiers.items():
        if stat_key in metrics:
            val = metrics[stat_key]
            # 50 as the neutral point
            # > 50 helps, < 50 hurts
            deviation = val - 50
            effect = int(deviation * weight)
            
            if effect != 0:
                current_chance += effect
                sign = "+" if effect > 0 else ""
                breakdown.append(f"{sign}{effect}% due to {stat_key.replace('_', ' ').title()}")

    # Limitation: Immer min 5% Chance, max 95%
    final_chance = max(5, min(95, current_chance))
    
    # Dice roll
    roll = random.randint(1, 100)
    success = roll <= final_chance
    
    return success, roll, final_chance, breakdown

def calculate_election_results(game_state):
    """
    Simuliert die Wahl basierend auf den aktuellen Demographien.
    """
    # 1. Bevölkerungsgewichtung (Wie viele Menschen sind in dieser Gruppe?)
    # Aristokratie ist klein (1), Bauern sind riesig (15).
    CLASS_WEIGHTS = {
        "aristocracy": 1,
        "clergy": 2,
        "bourgeoisie": 5,
        "workers_urban": 10,
        "workers_rural": 15,
        "soldiers": 3,
        "catalans": 4,  # Regionale Blöcke
        "basques": 2
    }
    
    demographics = game_state.election_demographics
    votes = {}

    # 2. Stimmen auszählen
    for group_name, weight in CLASS_WEIGHTS.items():
        # Hole die Parteipräferenzen dieser Gruppe (z.B. {PSOE: 0.6, DLR: 0.4})
        if group_name in demographics:
            preferences = demographics[group_name]
            
            for party_id, percentage in preferences.items():
                # Berechnung: Gewicht der Gruppe * Prozentanteil
                vote_share = weight * percentage
                
                # Zur Partei addieren
                if party_id not in votes:
                    votes[party_id] = 0
                votes[party_id] += vote_share

    # 3. Sitze verteilen (Proportional auf 470 Sitze)
    total_vote_points = sum(votes.values())
    total_parliament_seats = 470
    
    new_seats = {}
    
    # Debug Info
    print("--- ELECTION DEBUG ---")
    
    current_seat_sum = 0
    
    for party_id, score in votes.items():
        if total_vote_points > 0:
            share = score / total_vote_points
            seats = int(share * total_parliament_seats)
            new_seats[party_id] = seats
            current_seat_sum += seats
            print(f"{party_id}: {share:.2%} -> {seats} Seats")
    
    # 4. Rest-Sitze (Rundungsdifferenzen) an die Sieger verteilen oder "Others"
    remainder = total_parliament_seats - current_seat_sum
    if remainder > 0:
        if "others" not in new_seats:
            new_seats["others"] = 0
        new_seats["others"] += remainder
        
    return new_seats

def shift_voter_preference(game_state, class_name, party_id, change_amount):
    """
    Ändert die Beliebtheit einer Partei in einer Klasse und gleicht die anderen aus.
    
    Args:
        class_name: z.B. "workers_urban"
        party_id: z.B. "psoe"
        change_amount: z.B. 0.05 (für +5%) oder -0.02
    """
    # 1. Daten laden
    demo_data = gd.STATE_START['election_demographics'] # Changes the Global Data!
    # Besser: Es sollten ins session_state kopiert werden, wenn es veränderbar sein soll.
    # Für jetzt nehmen wir an, es liegt im session_state (siehe unten).
    
    preferences = game_state.election_demographics[class_name]
    
    # 2. Den neuen Wert setzen
    old_value = preferences.get(party_id, 0.0)
    new_value = max(0.0, min(1.0, old_value + change_amount))
    
    # Die Differenz, die wir ausgleichen müssen
    actual_change = new_value - old_value
    
    if actual_change == 0:
        return

    # 3. Den neuen Wert speichern
    preferences[party_id] = new_value
    
    # 4. Normalisierung (Ausgleich)
    # 'actual_change' wird den ANDEREN Parteien abzgezogen/draufgeschlagen.
    
    # Summe der anderen Parteien berechnen
    other_parties = [p for p in preferences if p != party_id]
    total_others = sum(preferences[p] for p in other_parties)
    
    if total_others > 0:
        for p in other_parties:
            # Anteil berechnen: Wer viel hat, gibt viel ab.
            share = preferences[p] / total_others
            # Den Ausgleich anwenden (Gegenteil von actual_change)
            reduction = actual_change * share
            
            preferences[p] -= reduction
            # Sicherstellen, dass nichts negativ wird
            preferences[p] = max(0.0, preferences[p])
            
    # 5. Letzter Safety Check (Rundungsfehler)
    # Alles summieren und auf 1.0 zwingen
    total_sum = sum(preferences.values())
    if total_sum != 0:
        for p in preferences:
            preferences[p] /= total_sum