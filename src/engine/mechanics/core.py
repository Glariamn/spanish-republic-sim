import sys
import os
import random
import content.game_data as gd

# Imports aus anderen Mechanics
from .elections import update_voter_sentiment
from .government import get_coalition_seats
from .factions import modify_faction_dissent

# Events Import
from content.initiatives.politics.coalition_crisis import CoalitionCrisisEvent
from content.initiatives.party.faction_schism import FactionSchismEvent
from content.events.historical.burning_convents import BurningConventsEvent
from content.events.system.confidence_vote import ConfidenceVoteEvent
from content.events.historical.events_1931 import MaciaDeclarationEvent, CardinalSeguraEvent, JuneElectionsEvent, LerrouxExitEvent, Constitution26Event

def calculate_outcome(base_chance, modifiers, game_state):
    current_chance = base_chance
    metrics = game_state.metrics
    breakdown = [f"Base: {base_chance}%"]
    
    for stat_key, weight in modifiers.items():
        if stat_key in metrics:
            val = metrics[stat_key]
            deviation = val - 50
            effect = int(deviation * weight)
            if effect != 0:
                current_chance += effect
                breakdown.append(f"{stat_key}: {effect:+}%")

    final_chance = max(5, min(95, current_chance))
    roll = random.randint(1, 100)
    return (roll <= final_chance), roll, final_chance, breakdown

def apply_entropy(state):
    if random.randint(1, 100) <= 30: 
        modify_faction_dissent(state, {"tag": "all", "amount": 2})
        
    if state.metrics['public_order'] > 60:
        state.metrics['public_order'] -= 1
        
    if state.economy['global_economy_state'] == "Great Depression" and random.randint(1, 100) <= 10:
        state.economy['unemployment'] += 0.5
        return "📉 Global markets worsen."
    return None

def process_monthly_tick(state):
    state.date['month'] += 1
    if state.date['month'] > 12:
        state.date['month'] = 1
        state.date['year'] += 1
    
    expenses = state.economy.get('monthly_expenses_int', 4)
    state.economy['budget_int'] += (state.economy['tax_revenue_int'] - expenses)
    
    entropy_msg = apply_entropy(state)

    # 1. Historical Event Check
    historical_id = None
    y, m = state.date['year'], state.date['month']
    if y == 1931:
        if m == 4: historical_id = "1931_macia_declaration"
        elif m == 5: historical_id = "1931_cardinal_segura"
        elif m == 6: historical_id = "1931_june_elections"
        elif m == 10: historical_id = "1931_lerroux_exit"
            
    if historical_id:
        return "Historical Event Imminent.", None, historical_id
    
    # 2. Mechanics
    update_voter_sentiment(state)
    
    # 3. Election Check
    next_el = state.government['next_election_date']
    if state.date['year'] == next_el['year'] and state.date['month'] == next_el['month']:
        return "Term limit reached.", None, "auto_election_trigger"

    # 4. Crisis Check
    triggered_crisis = None
    
    # Minority Check
    total_seats = sum(state.parliament['seats'].values())
    if total_seats > 0:
        gov_seats = get_coalition_seats(state)
        if gov_seats <= (total_seats // 2) and not state.government.get('is_minority', False):
             triggered_crisis = {"type": "minority_government", "msg": "Warning: Minority Government."}
             return "Month processed.", triggered_crisis, None

    # Dynamic Events Check
    possible_events = [
        FactionSchismEvent(state),
        BurningConventsEvent(state),
        CoalitionCrisisEvent(state),
        # Hier auch noch mal die Klassen, falls sie nicht durch History Trigger kommen:
        JuneElectionsEvent(state),
        MaciaDeclarationEvent(state),
        CardinalSeguraEvent(state),
        LerrouxExitEvent(state),
        Constitution26Event(state),
        ConfidenceVoteEvent(state)
    ]
    
    for event in possible_events:
        if event.should_trigger():
            data = event.get_data()
            if data.get('id') == "1931_june_elections":
                 return "Historical Event.", None, "1931_june_elections"
            triggered_crisis = {"type": "event_trigger", "event_data": data}
            break

    msg = "Month processed."
    if entropy_msg: msg += f" {entropy_msg}"
    
    return msg, triggered_crisis, None