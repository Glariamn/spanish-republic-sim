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
from content.events.historical.military_reform_event import LeyAzanaEvent
from content.events.historical.events_1931 import (
    MaciaDeclarationEvent, CardinalSeguraEvent, JuneElectionsEvent,
    ProclamationOfSecondRepublicEvent, ProvisionalGovernmentEvent
)
from content.events.historical.constitution_events import (
    LerrouxExitEvent, Constitution26CrisisEvent, ConstitutionCrisis27Event,
    ConstitutionCrisis44Event, ConstitutionRatifiedEvent
)

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
    
    # --- DYNAMISCHE WIRTSCHAFT ---
    # tax_revenue_actual = base_revenue * (industrial_output / 100 ) * (judicial_integrity_mod)
    # Industrieproduktion (0.5 bis 1.5 Modifikator)
    industry_mod = 0.5 + (state.economy['industrial_output'] / 100.0)

    # Justiz-Integrität (Korruptions-Malus)
    # Wenn Integrität < 40, verlierst du bis zu 30% Steuern
    integrity = state.metrics.get('judicial_integrity', 50)
    integrity_mod = 1.0 if integrity >= 40 else (0.7 + (integrity / 133.0))

    revenue_actual = state.economy['tax_revenue_int'] * industry_mod * integrity_mod

    # Militärkosten (Basierend auf Offizierszahl)
    # Jeder Offizier kostet 0.0005 Einheiten (16.000 Offiziere = 8.0 Ausgaben)
    military_costs = state.military['army_peninsular']['officers'] * 0.0005
    
    # Sicherheitskosten bei Unruhe
    order_penalty = 0
    if state.metrics['public_order'] < 40:
        order_penalty = (40 - state.metrics['public_order']) / 5.0 # Max +8.0

    expenses_actual = 4 + military_costs + order_penalty
    
    state.economy['budget_int'] += (revenue_actual - expenses_actual)
    
    entropy_msg = apply_entropy(state)

    # 1. Historical Event Check
    # Guards prevent re-firing if already in event_history
    historical_id = None
    y, m = state.date['year'], state.date['month']
    history = state.get('event_history', [])
    if y == 1931:
        if m == 4 and "1931_macia_declaration" not in history:
            historical_id = "1931_macia_declaration"
        elif m == 5 and "1931_cardinal_segura" not in history:
            historical_id = "1931_cardinal_segura"
        elif m == 10 and "1931_lerroux_exit" not in history:
            historical_id = "1931_lerroux_exit"

    if historical_id:
        return "Historical Event Imminent.", None, historical_id
    
    # 2. Mechanics
    update_voter_sentiment(state)
    
    # 3. Election Check
    next_el = state.government.get('next_election_date', {})
    if 'year' in next_el and 'month' in next_el and state.date['year'] == next_el['year'] and state.date['month'] == next_el['month']:
        if state.date['year'] == 1931:
            return "Elections imminent.", None, "1931_june_elections"
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
        ConfidenceVoteEvent(state),
        # Historical — fire dynamically (should_trigger guards them)
        JuneElectionsEvent(state),
        LeyAzanaEvent(state),
        LerrouxExitEvent(state),
        Constitution26CrisisEvent(state),
        ConstitutionCrisis27Event(state),
        ConstitutionCrisis44Event(state),
        ConstitutionRatifiedEvent(state),
    ]
    
    for event in possible_events:
        if event.should_trigger():
            data = event.get_data()
            #if data.get('id') == "1931_june_elections":
            #     return "Historical Event.", None, "1931_june_elections"
            triggered_crisis = {"type": "event_trigger", "event_data": data}
            break

    msg = "Month processed."
    if entropy_msg: msg += f" {entropy_msg}"
    
    return msg, triggered_crisis, None