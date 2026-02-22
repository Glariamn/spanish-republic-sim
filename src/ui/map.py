import os
import json
import pandas as pd
import altair as alt
import streamlit as st

# Hilfsfunktion: findet mapdata/ relativ zu dieser Datei
def load_geojson(filename):
    # Ordner, in dem map.py liegt
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # mapdata/ relativ zu map.py
    path = os.path.join(base_dir, "mapdata", filename)

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------
# 1. Mapping deiner Wahlkreisnamen → offizielle Provinznamen
# ---------------------------------------------------------

PROVINCE_MAPPING = {
    "La Coruña": "A Coruña",
    "Orense": "Ourense",
    "Pontevedra": "Pontevedra",
    "Lugo": "Lugo",

    "Vizcaya provincia": "Bizkaia",
    "Bilbao (Vizcaya cap.)": "Bizkaia",
    "Guipúzcoa": "Gipuzkoa",
    "Álava": "Araba/Álava",
    "Navarra": "Navarra",

    "Barcelona (capital)": "Barcelona",
    "Barcelona provincia": "Barcelona",
    "Girona": "Girona",
    "Lleida": "Lleida",
    "Tarragona": "Tarragona",

    "Zaragoza (capital)": "Zaragoza",
    "Zaragoza provincia": "Zaragoza",
    "Huesca": "Huesca",
    "Teruel": "Teruel",

    "Castellón": "Castellón/Castelló",
    "Valencia (capital)": "Valencia/València",
    "Valencia provincia": "Valencia/València",
    "Alicante": "Alacant/Alicante",

    "Murcia (capital)": "Murcia",
    "Cartagena": "Murcia",

    "Badajoz": "Badajoz",
    "Cáceres": "Cáceres",

    "Sevilla (capital)": "Sevilla",
    "Sevilla provincia": "Sevilla",
    "Córdoba": "Córdoba",
    "Jaén": "Jaén",
    "Granada (capital)": "Granada",
    "Granada provincia": "Granada",
    "Málaga (capital)": "Málaga",
    "Málaga provincia": "Málaga",
    "Cádiz": "Cádiz",
    "Huelva": "Huelva",
    "Almería": "Almería",

    "Las Palmas": "Las Palmas",
    "Santa Cruz de Tenerife": "Santa Cruz de Tenerife",
    "Melilla": "Melilla",
    "Ceuta": "Ceuta",

    "La Rioja (Logroño)": "La Rioja",

    "Oviedo": "Asturias",
    "Santander": "Cantabria",

    "León": "León",
    "Zamora": "Zamora",
    "Salamanca": "Salamanca",
    "Ávila": "Ávila",
    "Segovia": "Segovia",
    "Soria": "Soria",
    "Valladolid": "Valladolid",
    "Palencia": "Palencia",
    "Burgos": "Burgos",

    "Albacete": "Albacete",
    "Ciudad Real": "Ciudad Real",
    "Toledo": "Toledo",
    "Cuenca": "Cuenca",
    "Guadalajara": "Guadalajara",

    "Madrid (capital)": "Madrid",
    "Madrid provincia": "Madrid"
}

# ---------------------------------------------------------
# 2. Stärkste Partei pro Provinz berechnen
# ---------------------------------------------------------

def strongest_party_per_province(state):
    province_to_region = {
        c["name"]: c["region"]
        for c in state["constituencies"]
    }

    rows = []

    for province, region in province_to_region.items():
        groups = state["regional_demographics"][region]

        party_totals = {}
        for group, prefs in groups.items():
            for party, share in prefs.items():
                party_totals[party] = party_totals.get(party, 0) + share

        strongest = max(party_totals, key=party_totals.get)

        rows.append({
            "province": PROVINCE_MAPPING.get(province, province),
            "party": strongest
        })

    return pd.DataFrame(rows)

# ---------------------------------------------------------
# 3. Karte zeichnen
# ---------------------------------------------------------
def draw_spain_map(df):
    geo = load_geojson("spain_provinces.geojson")

    chart = (
        alt.Chart(
            alt.Data(
                values=geo["features"],
                format={"type": "json"}
            )
        )
        .mark_geoshape(stroke="black", strokeWidth=0.2)
        .encode(
            color=alt.Color(
                "party:N",
                scale=alt.Scale(scheme="tableau20"),
                legend=alt.Legend(title="Stärkste Partei")
            ),
            tooltip=[
                alt.Tooltip("properties.name:N", title="Provinz"),
                alt.Tooltip("party:N", title="Stärkste Partei")
            ]
        )
        .transform_lookup(
            lookup="properties.name",
            from_=alt.LookupData(df, "province", ["party"])
        )
        .project("mercator")
        .properties(width=900, height=700)
    )

    return chart



# ---------------------------------------------------------
# 4. Streamlit UI
# ---------------------------------------------------------

def render_map_page():
    st.title("Karte: Stärkste Partei pro Provinz")

    df = strongest_party_per_province(st.session_state)
    chart = draw_spain_map(df)

    st.altair_chart(chart, use_container_width=True)

def political_intensity_per_province(state):
    province_to_region = {
        c["name"]: c["region"]
        for c in state["constituencies"]
    }

    rows = []

    for province, region in province_to_region.items():
        groups = state["regional_demographics"][region]

        total_intensity = 0
        for group, prefs in groups.items():
            total_intensity += sum(prefs.values())

        rows.append({
            "province": PROVINCE_MAPPING.get(province, province),
            "intensity": total_intensity
        })

    return pd.DataFrame(rows)


def draw_intensity_map(df):
    geo = load_geojson("spain_provinces.geojson")

    chart = (
        alt.Chart(
            alt.Data(
                values=geo["features"],
                format={"type": "json"}
            )
        )
        .mark_geoshape(stroke="black", strokeWidth=0.2)
        .encode(
            color=alt.Color(
                "intensity:Q",
                scale=alt.Scale(scheme="reds"),
                legend=alt.Legend(title="Politische Intensität")
            ),
            tooltip=[
                alt.Tooltip("properties.name:N", title="Provinz"),
                alt.Tooltip("intensity:Q", title="Intensität", format=".2f")
            ]
        )
        .transform_lookup(
            lookup="properties.name",
            from_=alt.LookupData(df, "province", ["intensity"])
        )
        .project("mercator")
        .properties(width=900, height=700)
    )

    return chart
