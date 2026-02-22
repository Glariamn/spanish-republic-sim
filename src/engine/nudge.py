import pandas as pd
import content.game_data as gd

def compute_nudge_matrix(state, target_seats):
    """Vergleicht Ist- und Soll-Wahlergebnisse und berechnet Nudges pro Partei."""

    current = state.parliament['seats']
    parties = state.parties

    rows = []
    for p_id, target in target_seats.items():
        actual = current.get(p_id, 0)
        delta = actual - target

        rows.append({
            "party_id": p_id,
            "party": parties.get(p_id, {}).get("name", p_id),
            "actual_seats": actual,
            "target_seats": target,
            "delta": delta
        })

    df = pd.DataFrame(rows)
    return df.sort_values("delta", ascending=False)

def compute_class_contributions(state):
    rows = []
    demos = state.election_demographics
    parties = state.parties

    for group, prefs in demos.items():
        for p_id, val in prefs.items():
            rows.append({
                "class": group,
                "party": parties.get(p_id, {}).get("name", p_id),
                "support": val
            })

    return pd.DataFrame(rows)

CLASS_WEIGHTS = {
    "aristocracy": 1, "clergy": 2, "bourgeoisie": 5,
    "workers_urban": 10, "workers_rural": 15, "soldiers": 3
}

def compute_class_support(state):
    rows = []
    demos = state.election_demographics
    parties = state.parties

    for group, prefs in demos.items():
        weight = CLASS_WEIGHTS.get(group, 1)
        for p_id, share in prefs.items():
            rows.append({
                "class": group,
                "party_id": p_id,
                "party": parties.get(p_id, gd.PARTIES.get(p_id, {})).get("name", p_id),
                "weighted_support": share * weight
            })
    return pd.DataFrame(rows)

def compute_nudge_recommendations(state, target_seats):
    current = state.parliament['seats']
    df_support = compute_class_support(state)

    recs = []

    for p_id, target in target_seats.items():
        actual = current.get(p_id, 0)
        delta = actual - target
        if delta == 0:
            continue

        p_name = state.parties.get(p_id, gd.PARTIES.get(p_id, {})).get("name", p_id)

        # Welche Klassen tragen am meisten zu dieser Partei bei?
        sub = df_support[df_support["party_id"] == p_id]
        if sub.empty:
            continue

        sub = sub.copy()
        sub["share"] = sub["weighted_support"] / sub["weighted_support"].sum()

        # Wir verteilen das Sitz-Delta proportional auf die Klassen
        for _, row in sub.iterrows():
            class_name = row["class"]
            class_share = row["share"]
            # Heuristik: 1 Sitz ~ 0.5 Prozentpunkte Gesamtstimmen
            pct_shift = -delta * 0.005 * class_share
            if abs(pct_shift) < 0.002:
                continue

            recs.append({
                "party": p_name,
                "party_id": p_id,
                "class": class_name,
                "pct_shift": pct_shift
            })

    return pd.DataFrame(recs)

def compute_nudge_recommendations_detailed(state, target_seats):
    current = state.parliament['seats']
    df_class = compute_class_support(state)
    df_region = compute_region_support(state)

    recs = []

    for p_id, target in target_seats.items():
        actual = current.get(p_id, 0)
        delta = actual - target
        if delta == 0:
            continue

        p_name = state.parties.get(p_id, {}).get("name", p_id)

        # Klassenbeiträge
        sub_class = df_class[df_class["party_id"] == p_id]
        sub_class["class_share"] = sub_class["weighted_support"] / sub_class["weighted_support"].sum()

        # Regionenbeiträge
        sub_region = df_region[df_region["party_id"] == p_id]
        sub_region["region_share"] = sub_region["weighted_support"] / sub_region["weighted_support"].sum()

        # Heuristik: 1 Sitz ≈ 0.5% Gesamtstimmen
        for _, c_row in sub_class.iterrows():
            for _, r_row in sub_region.iterrows():
                pct_shift = -delta * 0.005 * c_row["class_share"] * r_row["region_share"]
                if abs(pct_shift) < 0.002:
                    continue

                recs.append({
                    "party": p_name,
                    "party_id": p_id,
                    "class": c_row["class"],
                    "region": r_row["region"],
                    "pct_shift": pct_shift
                })

    return pd.DataFrame(recs)

def compute_region_support(state):
    rows = []
    parties = state.parties

    for region, classes in state.REGIONAL_DEMOGRAPHICS.items():
        for class_name, prefs in classes.items():
            weight = CLASS_WEIGHTS.get(class_name, 1)
            for p_id, share in prefs.items():
                rows.append({
                    "region": region,
                    "class": class_name,
                    "party_id": p_id,
                    "party": parties.get(p_id, {}).get("name", p_id),
                    "weighted_support": share * weight
                })
    return pd.DataFrame(rows)

def compute_votes_by_region(state):
    """Berechnet die gewichteten Stimmen pro Region und Partei."""
    regions = state.REGIONAL_DEMOGRAPHICS
    parties = state.parties

    CLASS_WEIGHTS = {
        "aristocracy": 1, "clergy": 2, "bourgeoisie": 5,
        "workers_urban": 10, "workers_rural": 15, "soldiers": 3
    }

    rows = []

    for region, classes in regions.items():
        for class_name, prefs in classes.items():
            weight = CLASS_WEIGHTS.get(class_name, 1)
            for p_id, share in prefs.items():
                rows.append({
                    "region": region,
                    "party_id": p_id,
                    "party": parties.get(p_id, {}).get("name", p_id),
                    "vote_points": share * weight
                })

    df = pd.DataFrame(rows)

    # Aggregieren pro Region und Partei
    df = df.groupby(["region", "party", "party_id"], as_index=False)["vote_points"].sum()

    # Normalisieren pro Region (optional)
    df["region_total"] = df.groupby("region")["vote_points"].transform("sum")
    df["share"] = df["vote_points"] / df["region_total"]

    return df

def compute_seats_by_region(state, df_votes):
    """Verteilt Sitze pro Region proportional zu den Vote-Points."""
    constituencies = state.CONSTITUENCIES_1931

    rows = []

    for c in constituencies:
        region = c["region"]
        seats = c["seats"]

        sub = df_votes[df_votes["region"] == region]
        if sub.empty:
            continue

        total = sub["vote_points"].sum()
        sub = sub.copy()
        sub["seat_share"] = sub["vote_points"] / total
        sub["seats"] = (sub["seat_share"] * seats).round().astype(int)

        rows.extend(sub.to_dict("records"))

    return pd.DataFrame(rows)
