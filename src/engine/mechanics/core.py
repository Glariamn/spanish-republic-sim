import sys
import os
import random
import content.game_data as gd

# Imports aus anderen Mechanics
from .elections import update_voter_sentiment
from .government import get_coalition_seats
from .factions import modify_faction_dissent

# Events Import
from content.events.system.coalition_crisis import CoalitionCrisisEvent
from content.events.system.faction_schism import FactionSchismEvent
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
from content.events.historical.events_1932 import (
    SanjurjadaEvent, CatalanStatuteEvent, AgrarianReformEvent
)
from content.events.system.party_rename import AccionPopularRenameEvent, CEDAFoundedEvent
from content.events.historical.security_transfer import GCToInteriorEvent, CarabinerosToInteriorEvent

def _clamp(val, lo=0, hi=100):
    return max(lo, min(hi, val))


def tick_army_factions(state):
    """
    Monthly drift of officer faction distribution.
    Two forces:
      - Entropy: slow drift toward anti_republican over time (reflects
        institutional culture, seniority, Catholic education of officer class)
      - Event shocks are applied elsewhere (Ley Azaña, Sanjurjada, etc.)
      - Counterweight: reform_progress and republican metrics slow the drift

    Only affects army_peninsular and army_africa for now.
    Factions always sum to 100 — gaining in one means losing in others.
    """
    for unit_key in ("army_peninsular", "army_africa"):
        unit = state.military.get(unit_key, {})
        f = unit.get("factions")
        if not f:
            continue

        # Base entropy: anti-republican faction grows slightly each month
        # Slower if reform progress is high or public order is stable
        reform_mod = unit.get("reform_progress", 0) / 200   # max -0.5 modifier
        order_mod  = (state.metrics["public_order"] - 50) / 400  # -ve if order < 50

        # Base drift: +0.3 to anti_republican per month, taken from loyalist/republican
        drift = max(0.1, 0.3 - reform_mod + order_mod)
        drift *= random.uniform(0.6, 1.4)

        # Anti-republican grows, loyalist absorbs most of the loss
        gain = min(drift, 100 - f["anti_republican"] - 1)
        lose_loyalist = gain * 0.6
        lose_republican = gain * 0.4

        f["anti_republican"] = _clamp(f["anti_republican"] + gain)
        f["loyalist"]        = _clamp(f["loyalist"] - lose_loyalist)
        f["republican"]      = _clamp(f["republican"] - lose_republican)

        # Renormalize to 100
        total = sum(f.values())
        if total > 0:
            for k in f:
                f[k] = round(f[k] / total * 100, 1)


def tick_security_loyalty(state):
    """
    Security force loyalty drifts toward an equilibrium each month.
    Equilibrium is NOT simply the controlling ministry's party ideology —
    it's a composite of:
      - The demographic composition of the force (Guardia Civil: rural, Catholic)
      - The state of the country (public order, polarization)
      - Specific actions taken by ministers (applied as shocks elsewhere)

    Each force has a hard floor and ceiling reflecting its nature.
    The pull toward equilibrium is gentle — loyalty moves maybe 0.5-1.5 pts/month
    passively. Big moves come from events and actions.
    """
    # Equilibria: where each force "wants" to be given country state
    # Base equilibrium per force
    BASE_EQUILIBRIUM = {
        "guardia_civil": 32,    # Structurally conservative — equilibrium is low
        "assault_guard":  85,   # Created for loyalty — floor is high
        "carabineros":    52,
    }

    # Adjust equilibrium based on country state
    order = state.metrics.get("public_order", 50)
    stability = state.metrics.get("coalition_stability", 50)
    # Polarization proxy: low order + low stability = worse equilibrium for GC
    polarization_drag = max(0, (100 - order) / 100 + (100 - stability) / 200)

    for force_key, force in state.security.items():
        base_eq = BASE_EQUILIBRIUM.get(force_key, 50)
        # GC equilibrium falls faster under polarization
        if force_key == "guardia_civil":
            equilibrium = _clamp(base_eq - polarization_drag * 10)
        elif force_key == "assault_guard":
            equilibrium = _clamp(base_eq - polarization_drag * 3)
        else:
            equilibrium = _clamp(base_eq - polarization_drag * 5)

        current = force.get("loyalty_republic", 50)
        # Gentle pull: 0.3-0.8 per month toward equilibrium
        pull = random.uniform(0.3, 0.8)
        if current < equilibrium:
            new_val = min(current + pull, equilibrium)
        elif current > equilibrium:
            new_val = max(current - pull, equilibrium)
        else:
            new_val = current

        force["loyalty_republic"] = round(_clamp(new_val), 1)
        force["loyalty"] = force["loyalty_republic"]  # keep legacy field in sync


def tick_conspiracy(state):
    """
    Monthly conspiracy tick. Only runs if conspiracy.active == True.
    
    Momentum growth:
      - Base: +1.5/month (it builds regardless)
      - Modified by: army anti_republican %, public order, economy, polarization
      - Reduced by: assault guard strength, high officer loyalty institutional score
    
    Defection:
      - Logarithmic growth from the anti_republican officer pool
      - Soldiers follow at ~55% of officer defection rate
    """
    import math
    c = state.conspiracy
    if not c["active"]:
        return

    c["months_active"] += 1
    army = state.military["army_peninsular"]
    africa = state.military["army_africa"]

    # --- Momentum growth ---
    anti_rep_pct = (
        army["factions"]["anti_republican"] * 0.6 +
        africa["factions"]["anti_republican"] * 0.4
    )
    order_factor    = (100 - state.metrics["public_order"]) / 100   # 0-1
    economy_factor  = max(0, (50 - state.economy.get("budget_int", 0)) / 100)
    stability_factor = (100 - state.metrics["coalition_stability"]) / 200

    # Counterweights
    ag = state.security.get("assault_guard", {})
    ag_factor = (ag.get("manpower", 0) / 20000) * (ag.get("loyalty_republic", 80) / 100)
    institutional_loyalty = army["officer_loyalty"] / 200  # small dampener

    momentum_gain = (
        1.5
        + anti_rep_pct / 25
        + order_factor * 3
        + economy_factor * 2
        + stability_factor * 2
        - ag_factor * 2
        - institutional_loyalty
        + random.uniform(-0.5, 1.0)   # noise — tends slightly positive
    )
    c["momentum"] = _clamp(c["momentum"] + momentum_gain)

    # --- Defection (logarithmic) ---
    # Pool: anti_republican officers across both armies
    total_officers = army["officers"] + africa["officers"]
    anti_rep_officers = int(total_officers * (
        army["factions"]["anti_republican"] * army["officers"] +
        africa["factions"]["anti_republican"] * africa["officers"]
    ) / (100 * total_officers))

    already_defected = c["defected_officers"]
    remaining_pool = max(0, anti_rep_officers - already_defected)

    if remaining_pool > 0 and c["momentum"] > 5:
        # Logarithmic: fast early gains, slows as pool saturates
        monthly_recruit = remaining_pool * (
            math.log(1 + c["momentum"]) / math.log(101)
        ) * random.uniform(0.05, 0.15)
        monthly_recruit = min(monthly_recruit, remaining_pool)
        c["defected_officers"] += int(monthly_recruit)

        # Soldiers: follow their officers at ~55% rate
        total_soldiers = army["soldiers"] + africa["soldiers"]
        soldier_ratio = total_soldiers / total_officers
        c["defected_soldiers"] += int(monthly_recruit * soldier_ratio * 0.55)



def tick_political_drift(state):
    """
    Monthly slow bleed of election_demographics away from coalition parties.

    Sources of drift (each tiny, cumulative over months):
      incumbency_fatigue  -- being in government always costs something
      minority_penalty    -- minority gov loses faster, can't deliver
      unemployment        -- above baseline bleeds workers
      budget_deficit      -- negative budget hurts bourgeoisie confidence
      order_decay         -- below 60 (start value) bleeds all groups
      casas_viejas        -- if that flag exists: extra workers_urban bleed

    Each source bleeds FROM coalition parties proportionally to their
    current share in that group, INTO the natural opposition party for
    that group. Non-coalition parties are not bled.

    Net per-month shift is ~0.001-0.005 per group per source -- small but
    compounds meaningfully over 24 months.
    """
    from .elections import apply_demographic_vector

    coalition = set(state.government.get("coalition", []))
    if not coalition:
        return

    economy = state.economy
    metrics = state.metrics
    passed = state.passed_laws

    incumbency    = 0.0008

    minority_pen  = 0.0015 if state.government.get("is_minority", False) else 0.0

    unemployment  = economy.get("unemployment", 12.5)
    unemp_factor  = max(0, (unemployment - 12.5) / 100)

    budget        = economy.get("budget_int", 0)
    deficit_factor = max(0, -budget / 200)

    order         = metrics.get("public_order", 60)
    order_factor  = max(0, (60 - order) / 300)

    casas_factor  = 0.003 if "flag_casas_viejas" in passed else 0.0

    OPPOSITION_TARGET = {
        "aristocracy":   gd.PARTY_MON,
        "clergy":        gd.PARTY_CEDA,
        "bourgeoisie":   gd.PARTY_CEDA,
        "workers_urban": gd.PARTY_PCE,
        "workers_rural": gd.PARTY_PCE,
        "soldiers":      gd.PARTY_PRR,
    }

    drift_sources = [
        (incumbency,     ["aristocracy", "clergy", "bourgeoisie",
                          "workers_urban", "workers_rural"]),
        (minority_pen,   ["bourgeoisie", "workers_urban", "workers_rural"]),
        (unemp_factor,   ["workers_urban", "workers_rural"]),
        (deficit_factor, ["bourgeoisie", "aristocracy"]),
        (order_factor,   ["workers_urban", "workers_rural", "bourgeoisie"]),
        (casas_factor,   ["workers_urban"]),
    ]

    demos = state.election_demographics
    for magnitude, groups in drift_sources:
        if magnitude <= 0:
            continue
        for group in groups:
            if group not in demos:
                continue
            prefs = demos[group]
            target = OPPOSITION_TARGET.get(group)
            if not target:
                continue
            coalition_share = sum(prefs.get(p, 0) for p in coalition)
            if coalition_share <= 0:
                continue
            bleed_total = magnitude * coalition_share
            changes = {target: bleed_total}
            for p in coalition:
                if p in prefs and prefs[p] > 0:
                    share_of_coalition = prefs[p] / coalition_share
                    changes[p] = changes.get(p, 0) - bleed_total * share_of_coalition
            apply_demographic_vector(state, group, changes)


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
    tick_army_factions(state)
    tick_security_loyalty(state)
    tick_conspiracy(state)
    tick_political_drift(state)

    # 1. Historical Event Check
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
    elif y == 1932:
        if m == 8 and "1932_sanjurjada" not in history:
            historical_id = "1932_sanjurjada"
        elif m == 9:
            # Statute and reform both fire in September — statute has priority
            if "flag_catalan_statute" not in state.passed_laws:
                historical_id = "1932_catalan_statute"
            elif "flag_agrarian_reform" not in state.passed_laws:
                historical_id = "1932_agrarian_reform"

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
        # 1931
        JuneElectionsEvent(state),
        LeyAzanaEvent(state),
        MaciaDeclarationEvent(state),
        CardinalSeguraEvent(state),
        LerrouxExitEvent(state),
        Constitution26CrisisEvent(state),
        ConstitutionCrisis27Event(state),
        ConstitutionCrisis44Event(state),
        ConstitutionRatifiedEvent(state),
        # 1932
        SanjurjadaEvent(state),
        CatalanStatuteEvent(state),
        AgrarianReformEvent(state),
        AccionPopularRenameEvent(state),
        # 1933
        CEDAFoundedEvent(state),
        # Security transfers (fire when conditions met, any year)
        GCToInteriorEvent(state),
        CarabinerosToInteriorEvent(state),
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