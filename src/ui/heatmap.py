import pandas as pd
import altair as alt

def build_heatmap(regional_demographics):
    rows = []

    for region, groups in regional_demographics.items():
        # Aggregiere Parteipräferenzen über alle Klassen
        party_totals = {}

        for group, prefs in groups.items():
            for party, share in prefs.items():
                party_totals[party] = party_totals.get(party, 0) + share

        # Normalisieren (damit jede Region auf 1.0 kommt)
        total = sum(party_totals.values())
        for party in party_totals:
            party_totals[party] /= total

        # In Tabelle schreiben
        for party, value in party_totals.items():
            rows.append({
                "Region": region,
                "Partei": party,
                "Anteil": value
            })

    df = pd.DataFrame(rows)

    heatmap = (
        alt.Chart(df)
        .mark_rect()
        .encode(
            x=alt.X("Partei:N", sort=None),
            y=alt.Y("Region:N", sort=None),
            color=alt.Color("Anteil:Q", scale=alt.Scale(scheme="reds")),
            tooltip=["Region", "Partei", alt.Tooltip("Anteil:Q", format=".2f")]
        )
        .properties(width=800, height=600)
    )

    return heatmap
