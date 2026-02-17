import content.game_data as gd

def calculate_election_results(state):
    """
    Bezirksbasierte Wahl:
    - Stimmen & Sitze pro Circunscripción
    - REGION_MODIFIERS + election_demographics
    - D’Hondt pro Bezirk
    - nationale Sitzsummen
    """

    import content.game_data as gd

    # Alte Ergebnisse speichern
    state.history['last_election_seats'] = state.parliament['seats'].copy()

    # --- 1. Wahlbeteiligung ---
    base_turnout = 0.70
    stability_mod = (50 - state.metrics['coalition_stability']) / 200
    order_mod = (50 - state.metrics['public_order']) / 200
    final_turnout = max(0.5, min(0.95, base_turnout + stability_mod + order_mod))

    # --- 2. Klassenbasis (national) ---
    CLASS_WEIGHTS = {
        "aristocracy": 1,
        "clergy": 2,
        "bourgeoisie": 5,
        "workers_urban": 10,
        "workers_rural": 15,
        "soldiers": 3
    }

    national_seats = {}
    breakdown = []  # NEU: Liste pro Bezirk

    # --- 3. Hauptschleife: Jede Circunscripción ---
    for c in gd.CONSTITUENCIES_1931:
        cid = c["id"]
        cname = c["name"]
        region = c["region"]
        seats = c["seats"]

        # 3a. effektive Klassenanteile
        eff_weights = {}
        for g, base_w in CLASS_WEIGHTS.items():
            region_mod = gd.REGION_MODIFIERS.get(region, {}).get(g, 1.0)
            eff_weights[g] = base_w * region_mod

        total_w = sum(eff_weights.values())
        for g in eff_weights:
            eff_weights[g] /= total_w

        # 3b. Stimmenpunkte pro Partei im Bezirk
        local_votes = {}
        for g, w in eff_weights.items():
            # --- REGIONAL DEMOGRAPHICS OVERRIDE ---
            regional = state.get("regional_demographics", {})
            if region in regional and g in regional[region]:
                prefs = regional[region][g]
            else:
                prefs = state.election_demographics.get(g, {})
            for party, share in prefs.items():
                party_data = state.parties.get(party, gd.PARTIES["others"])
                mobil = party_data.get("institutionalization", 50) / 100
                v = w * share * mobil * final_turnout
                local_votes[party] = local_votes.get(party, 0) + v

        # CNT raus
        if gd.PARTY_CNT in local_votes:
            del local_votes[gd.PARTY_CNT]

        # 3c. D’Hondt
        quotients = []
        for party, v in local_votes.items():
            for d in range(1, seats + 1):
                quotients.append((v / d, party))

        quotients.sort(reverse=True, key=lambda x: x[0])
        winners = quotients[:seats]

        # 3d. Sitzverteilung im Bezirk
        local_seats = {}
        for _, p in winners:
            local_seats[p] = local_seats.get(p, 0) + 1
            national_seats[p] = national_seats.get(p, 0) + 1

        breakdown.append({
            "id": cid,
            "name": cname,
            "region": region,
            "seats_total": seats,
            "seats_by_party": local_seats,
            "votes_raw": local_votes
        })

    # 4. Ergebnis speichern
    state.parliament['seats'] = national_seats
    state.history['last_election_breakdown'] = breakdown  # NEU

    # 5. Nächste Wahl
    term = state.government.get('term_length', 48)
    next_y = state.date['year'] + (term // 12)
    state.government['next_election_date'] = {
        "year": next_y,
        "month": state.date['month']
    }

    return national_seats



def call_new_election(state):
    """Führt Neuwahlen durch und setzt State zurück."""
    new_seats = calculate_election_results(state)
    state.parliament['seats'] = new_seats
    
    state.government['coalition'] = [] 
    state.government['is_minority'] = False
    
    for m in state.ministries.values():
        m['holder'] = f"Acting ({m['holder']})"

    current_year = state.date['year']
    current_month = state.date['month']
    future_year = current_year + 4
    
    state.government['next_election_date'] = {
        "year": future_year, 
        "month": current_month
    }
        
    return f"Election complete. Next election set for {current_month}/{future_year}."

def apply_demographic_vector(state, group_name, changes):
    """Wendet Wählerverschiebungen an und gleicht aus."""
    if 'election_demographics' not in state: return
    demos = state.election_demographics
    if group_name not in demos: return
    
    preferences = demos[group_name]
    net_change = 0.0
    active_parties = []
    logs = []

    for party_id, amount in changes.items():
        if party_id not in preferences: preferences[party_id] = 0.0
        old_val = preferences[party_id]
        new_val = max(0.0, old_val + amount)
        actual_diff = new_val - old_val
        
        preferences[party_id] = new_val
        net_change += actual_diff
        active_parties.append(party_id)
        
        p_name = gd.PARTIES.get(party_id, gd.PARTIES["others"])['name']
        if abs(actual_diff) > 0.001:
            logs.append(f"{p_name} {actual_diff*100:+.1f}%")

    # Ausgleich
    passive_parties = [p for p in preferences if p not in active_parties]
    passive_sum = sum(preferences[p] for p in passive_parties)
    
    if passive_parties and abs(net_change) > 0.0001:
        if net_change > 0: # Vergabe
            if passive_sum > 0:
                for p in passive_parties:
                    share = preferences[p] / passive_sum
                    deduction = net_change * share
                    preferences[p] = max(0.0, preferences[p] - deduction)
        elif net_change < 0: # Verteilung
            gain_total = abs(net_change)
            if passive_sum > 0:
                 for p in passive_parties:
                    share = preferences[p] / passive_sum
                    preferences[p] += gain_total * share
            elif "others" in preferences:
                 preferences["others"] += gain_total

    # Normalisierung
    total = sum(preferences.values())
    if total != 0:
        for p in preferences: preferences[p] /= total
        
    if logs: return f"Shift in {group_name}: " + ", ".join(logs)
    return None

def update_voter_sentiment(state):
    """Wählerwanderung durch Unzufriedenheit."""
    if 'society' not in state: return
    
    opposition_map = {
        "aristocracy": gd.PARTY_MON, "clergy": gd.PARTY_CEDA,
        "bourgeoisie": gd.PARTY_CEDA, "workers_urban": gd.PARTY_PCE, 
        "workers_rural": gd.PARTY_CNT, "soldiers": gd.PARTY_FAL
    }
    
    impact_reports = []
    for group, satisfaction in state.society.items():
        if group in state.election_demographics and satisfaction < 35:
            loss = (35 - satisfaction) / 1000
            target = opposition_map.get(group, gd.PARTY_MON)
            apply_demographic_vector(state, group, {target: loss})
            if loss > 0.005:
                impact_reports.append(f"{group.title()} unhappy.")

    return impact_reports