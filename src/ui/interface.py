import sys
import os
import math
import streamlit as st
import pandas as pd
import altair as alt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import content.game_data as gd
from .heatmap import build_heatmap
from .map import render_map_page, draw_spain_map, strongest_party_per_province, political_intensity_per_province, draw_intensity_map

# --- HELPER FUNCTIONS ---
def get_status_label(value):
    if value <= 20: return "Critical"
    elif value <= 40: return "Unstable"
    elif value <= 60: return "Tense"
    elif value <= 80: return "Stable"
    else: return "Secure"

def get_loyalty_label(val):
    if val <= 20: return "Disloyal"
    if val <= 40: return "Untrustworthy"
    if val <= 60: return "Uncertain"
    if val <= 80: return "Reliable"
    return "Loyal"

def get_relation_label(val):
    if val <= 20: return "Cold"
    if val <= 40: return "Cool"
    if val <= 60: return "Neutral"
    if val <= 80: return "Warm"
    return "Friendly"

def get_approval_label(val):
    if val <= 20: return "Discontent"
    if val <= 40: return "Disapproving"
    if val <= 60: return "Ambivalent"
    if val <= 80: return "Content"
    return "Sympathetic"

def format_money(amount_int):
    inflation = st.session_state.economy['inflation']
    base_value = st.session_state.economy['peseta_value']
    real_value = amount_int * base_value * inflation
    return f"{real_value:,.0f} ₧"

# --- RENDER FUNCTIONS ---

import pandas as pd
import altair as alt
import math
import streamlit as st
import content.game_data as gd

def render_top_overview(state):
    """
    Realistic Spanish Congreso hemicycle with correct ideological ordering,
    parchment background, decree header, drop shadow, majority threshold arc,
    fade‑in animation, and Gobierno/Oposición layout.
    """

    # --- Parliament existence ---
    seats = state.parliament.get('seats', {})
    total_seats = sum(seats.values())

    if total_seats == 0:
        st.info("Cortes Constituyentes: No elected parliament yet.")
        st.caption("The Provisional Government rules by decree until the June elections.")
        return

    # --- Build party data ---
    data = []
    for party_id, count in seats.items():
        if count <= 0:
            continue

        p_data = gd.PARTIES.get(party_id, gd.PARTIES.get("others", {}))
        order = p_data.get("ideology_index", 5)

        if party_id == "others":
            order = 100
        elif party_id == "monarchists" or p_data.get("name") == "Monarchists":
            order = 99

        data.append({
            "id": party_id,
            "name": p_data.get("name", party_id),
            "seats": count,
            "color": p_data.get("color", "#888888"),
            "order": order
        })

    data.sort(key=lambda x: x["order"])

    # --- Hemicycle geometry ---
    def get_spanish_hemicycle_df(party_data, total):
        rows = 9
        radii = [1.0 + i * 0.22 for i in range(rows)]
        angle_start = math.radians(200)
        angle_end = math.radians(-20)

        expanded = []
        for p in party_data:
            expanded += [p] * p["seats"]

        angles = [
            angle_start + i * (angle_end - angle_start) / (total - 1)
            for i in range(total)
        ]

        points = []
        for idx, angle in enumerate(angles):
            row = idx % rows
            r = radii[row]

            x = r * math.cos(angle)
            y = r * math.sin(angle) * 0.55

            p = expanded[idx]

            points.append({
                "x": x,
                "y": y,
                "Party": p["name"],
                "Color": p["color"],
                "Seats": p["seats"]
            })

        # Majority threshold line
        majority = total // 2 + 1
        majority_angle = angles[majority - 1]

        threshold = pd.DataFrame([{
            "x1": radii[0] * math.cos(majority_angle),
            "y1": radii[0] * math.sin(majority_angle) * 0.55,
            "x2": radii[-1] * math.cos(majority_angle),
            "y2": radii[-1] * math.sin(majority_angle) * 0.55,
        }])

        return pd.DataFrame(points), threshold

    df, threshold = get_spanish_hemicycle_df(data, total_seats)

    # --- CSS: parchment, fade‑in, shadow ---
    st.markdown("""
        <style>
            .parchment {
                background:
                    radial-gradient(circle at 30% 30%, rgba(255,255,255,0.4), rgba(0,0,0,0) 70%),
                    radial-gradient(circle at 70% 70%, rgba(255,255,255,0.3), rgba(0,0,0,0) 80%),
                    #f2e9d8;
                padding: 25px;
                border-radius: 14px;
                border: 1px solid #d8c9b3;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
            }
            .fadein {
                animation: fadein 0.8s ease-in-out;
            }
            @keyframes fadein {
                from { opacity: 0; transform: translateY(10px); }
                to   { opacity: 1; transform: translateY(0); }
            }
        </style>
    """, unsafe_allow_html=True)

    # --- Decree header ---
    st.markdown("""
        <div style="
            background-color: #d8c9b3;
            padding: 8px 15px;
            border-radius: 8px;
            font-weight: bold;
            font-size: 18px;
            text-align: center;
            border: 1px solid #b8a894;
            margin-bottom: 10px;
        ">
            Cortes Generales — Legislatura I
        </div>
    """, unsafe_allow_html=True)

    # --- Hemicycle panel ---
    st.markdown(f"### Cortes Constituyentes ({total_seats} Escaños)")

    if not df.empty:
        max_r = max(abs(df["x"]).max(), abs(df["y"]).max())
        domain = [-max_r, max_r]

        chart = alt.Chart(df).mark_circle(size=55).encode(
            x=alt.X("x:Q", axis=None, scale=alt.Scale(domain=domain)),
            y=alt.Y("y:Q", axis=None, scale=alt.Scale(domain=domain)),
            color=alt.Color("Color:N", scale=None),
            tooltip=["Party", "Seats"]
        ).properties(height=300)

        line = alt.Chart(threshold).mark_rule(
            color="#444",
            strokeWidth=2,
            strokeDash=[4, 4]
        ).encode(
            x='x1:Q', x2='x2:Q',
            y='y1:Q', y2='y2:Q'
        )

        st.altair_chart(chart + line, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # --- Gobierno & Oposición ---
    coalition_ids = state.government.get("coalition", [])

    gov_data = [d for d in data if d["id"] in coalition_ids]
    opp_data = [d for d in data if d["id"] not in coalition_ids]

    gov_data.sort(key=lambda x: x["order"])
    opp_data.sort(key=lambda x: x["order"])

    gov_total = sum(d["seats"] for d in gov_data)
    opp_total = sum(d["seats"] for d in opp_data)
    majority = total_seats // 2 + 1

    col_gov, col_opp = st.columns(2)

    with col_gov:
        with st.container(border=True):
            st.markdown(f"🏛️ **Gobierno (Coalición) — {gov_total} Sitze**")
            for d in gov_data:
                st.markdown(
                    f"<span style='color:{d['color']}'>■</span> "
                    f"**{d['name']}** {d['seats']}",
                    unsafe_allow_html=True
                )

    with col_opp:
        with st.container(border=True):
            st.markdown(f"⚖️ **Oposición — {opp_total} Sitze**")
            for d in opp_data:
                st.markdown(
                    f"<span style='color:{d['color']}'>■</span> "
                    f"{d['name']} {d['seats']}",
                    unsafe_allow_html=True
                )

    st.markdown(
        f"**Mehrheitsschwelle:** {majority} Sitze — "
        f"{'✔️ erreicht' if gov_total >= majority else '❌ nicht erreicht'}"
    )

def render_election_comparison():
    """Zeigt den Unterschied zur letzten Wahl."""
    if 'history' not in st.session_state or 'last_election_seats' not in st.session_state.history:
        return

    old_seats = st.session_state.history['last_election_seats']
    new_seats = st.session_state.parliament['seats']
    
    if not old_seats: return 

    st.markdown("### 🗳️ Election Results Breakdown")
    
    # Tabelle
    rows = []
    for p_id, current in new_seats.items():
        if current == 0 and old_seats.get(p_id, 0) == 0: continue
        
        old = old_seats.get(p_id, 0)
        diff = current - old
        p_name = gd.PARTIES.get(p_id, gd.PARTIES['others'])['name']
        
        rows.append({
            "Party": p_name,
            "Seats": current,
            "Change": diff
        })
    
    # Sortieren nach Gewinnen/Verlusten
    rows.sort(key=lambda x: x['Seats'], reverse=True)
    
    # Anzeige als Metriken in Reihen
    cols = st.columns(4)
    for i, row in enumerate(rows):
        with cols[i % 4]:
            st.metric(
                label=row['Party'], 
                value=row['Seats'], 
                delta=row['Change'] if row['Change'] != 0 else None
            )
    st.divider()

    # --- Heatmap ---
    st.subheader("Heatmap: Parteistärke pro Region")
    heatmap = build_heatmap(st.session_state.regional_demographics)
    st.altair_chart(heatmap, use_container_width=True)

    st.divider()

    with st.expander("📊 Breakdown by Region"):
        render_region_vote_table(st.session_state)
        render_region_summary(st.session_state)

    # DEBUG STUFF
    if not st.session_state.get("disable_nudge", False):
        with st.expander("📊 Election Diagnostics & Nudge Matrix"):
            from content.game_data import TARGET_1931
            render_nudge_visualization(st.session_state, TARGET_1931)

        with st.expander("📊 Nudge-Matrix & Empfehlungen"):
            render_nudge_recommendations(st.session_state)

        with st.expander("📊 Nudge Empfehlungen pro Provinz"):
            render_nudge_recommendations_detailed(st.session_state)

    st.divider()

    # --- Map ---
    if not st.session_state.get("disable_maps", False):
        st.subheader("Karte: Stärkste Partei pro Provinz")
        df = strongest_party_per_province(st.session_state)
        chart = draw_spain_map(df)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Maps disabled (Developer Tools)")

    # --- Political Intensity ---
    if not st.session_state.get("disable_maps", False):
        st.subheader("Karte: Politische Intensität")
        df = political_intensity_per_province(st.session_state)
        chart = draw_intensity_map(df)
        st.altair_chart(chart, use_container_width=True)

    # --- Constituency Breakdown ---
    st.markdown("### 🗳️ Constituency Results")

    br = st.session_state.history.get('last_election_breakdown', [])

    with st.expander("Constituency Results Details"):
        if not br:
            st.caption("No constituency data available.")
        else:
            for c in br:
                st.markdown(f"#### {c['name']} ({c['region']}) — {c['seats_total']} seats")

                # Sitzverteilung sortiert
                seat_list = sorted(
                    c['seats_by_party'].items(),
                    key=lambda x: -x[1]
                )

                for p_id, s in seat_list:
                    pname = gd.PARTIES.get(p_id, gd.PARTIES['others'])['name']
                    st.text(f"  {pname}: {s} seat(s)")

                # Rohstimmen optional
                with st.expander("Raw vote points"):
                    vote_list = sorted(
                        c['votes_raw'].items(),
                        key=lambda x: -x[1]
                    )
                    for p_id, v in vote_list:
                        pname = gd.PARTIES.get(p_id, gd.PARTIES['others'])['name']
                        st.text(f"  {pname}: {v:.4f}")

                st.write("---")
    st.divider()

# Map of player party -> affiliated orgs for the Par tab
_PARTY_ORGS = {
    gd.PARTY_PSOE:  [("ugt", "UGT"), ("js_psoe", "Juv. Socialistas")],
    gd.PARTY_AR:    [("ateneos", "Ateneos Rep.")],
    gd.PARTY_PRR:   [("ateneos", "Ateneos Rep.")],
    gd.PARTY_PRRS:  [("ugt", "UGT"), ("ateneos", "Ateneos Rep.")],
    gd.PARTY_CNT:   [("cnt", "CNT"), ("fai", "FAI"), ("juv_lib", "Juv. Libertarias")],
}

def render_sidebar():
    """Die Seitenleiste."""
    state = st.session_state  # Replace st.session_state with this if needed (isn't needed for now)

    stability = st.session_state.metrics.get("coalition_stability", 50)
    stab_dot = "🟢" if stability >= 60 else ("🟡" if stability >= 35 else "🔴")
    
    party = gd.PARTIES[st.session_state.player_party]

    # --- Header ---
    col1, col2 = st.sidebar.columns([3, 2])
    col1.markdown(f"## {st.session_state.date['month']}/{st.session_state.date['year']}")
    col2.markdown(f"<div style='text-align:right; padding-top:12px'>{stab_dot} {st.session_state.metrics.get('coalition_stability')}</div>",
                  unsafe_allow_html=True)
    st.sidebar.markdown(
        f'<span style="color:{party["color"]}; font-weight:bold; font-size:1.1em">{party["name"]}</span> ' 
        f'<span style="color:#888; font-size:0.85em">— Gobierno</span>',
        unsafe_allow_html=True)
    
    tab_eco, tab_soc, tab_sec, tab_mil, tab_pol, tab_par, tab_wor = st.sidebar.tabs(
        ["Eco", "Soc", "Sec", "Mil", "Pol", "Par", "World"])
    
    with tab_eco:
        eco = st.session_state.economy
        tax = eco.get('taxation', {})
        breakdown = eco.get('_tax_breakdown', {})

        # Treasury and revenue
        st.metric("Hacienda", format_money(eco['budget_int']))
        total_rev = breakdown.get('total', eco.get('tax_revenue_int', 0))
        st.caption(f"Ingresos: +{format_money(total_rev)}/mo")

        col1, col2 = st.columns(2)
        col1.metric("Pan", f"{eco['bread_price'] * eco['inflation']:.2f} ₧")
        col2.metric("Inflación", f"{eco['inflation']}%")
        col1.metric("Paro", f"{eco['unemployment']}%")
        col2.metric("Letras", f"{st.session_state.demographics['literacy']}%")

        st.divider()
        st.caption("Economía")
        col1, col2 = st.columns(2)
        col1.text(f"Industria: {eco['industrial_output']}%")
        col2.text(f"Tierra: {eco['arable_land']}M ha")
        col1.text(f"Comercio: {eco['trade_balance']:+}")
        col2.text(f"Global: {eco['global_economy_state'][:8]}")

        if tax:
            st.divider()
            st.caption("Tipos impositivos")
            col1, col2 = st.columns(2)
            col1.text(f"Consumo:  {tax.get('consumption_tax_rate', 8)}%")
            col2.text(f"Renta:    {tax.get('income_tax_rate', 3)}%")
            col1.text(f"Tierra:   {tax.get('land_tax_rate', 5)}%")
            col2.text(f"Aduanas:  {tax.get('customs_rate', 15)}%")

            st.divider()
            st.caption("Estructura fiscal")
            cad = tax.get('cadastre_coverage', 28)
            eff = tax.get('collection_efficiency', 45)
            adm = tax.get('tax_admin_capacity', 35)
            cad_bar = "█" * (cad // 10) + "░" * (10 - cad // 10)
            eff_bar = "█" * (eff // 10) + "░" * (10 - eff // 10)
            adm_bar = "█" * (adm // 10) + "░" * (10 - adm // 10)
            st.caption(f"Catastro:    {cad_bar} {cad}%")
            st.caption(f"Recaudación: {eff_bar} {eff}%")
            st.caption(f"Capacidad:   {adm_bar} {adm}%")
            exemptions = []
            if tax.get('church_exempt', True):         exemptions.append("Iglesia")
            if tax.get('latifundio_undervalued', True): exemptions.append("Latifundios")
            if exemptions:
                st.caption(f"⚠️ Exentos: {', '.join(exemptions)}")

            if breakdown:
                st.divider()
                st.caption("Desglose ingresos")
                col1, col2 = st.columns(2)
                col1.caption(f"Consumo:  {format_money(breakdown.get('consumption', 0))}")
                col2.caption(f"Tierra:   {format_money(breakdown.get('land', 0))}")
                col1.caption(f"Renta:    {format_money(breakdown.get('income', 0))}")
                col2.caption(f"Aduanas:  {format_money(breakdown.get('customs', 0))}")
                st.caption(f"Monopolios: {format_money(breakdown.get('monopolies', 0))}")

        st.divider()
        st.caption("Demografía")
        st.text(f"Censo 1930: {st.session_state.demographics['census_1930']:,}")

    with tab_soc:
        soc = st.session_state.society
        st.caption("Aprobación Social")
        st.markdown("**Las Fuerzas Vivas**")
        st.text(f"Latifundistas: {get_approval_label(soc['aristocracy'])}")
        st.text(f"Iglesia:       {get_approval_label(soc['clergy'])}")
        st.text(f"Burguesía:     {get_approval_label(soc['bourgeoisie'])}")
        st.divider()
        st.markdown("**El Pueblo**")
        st.text(f"Proletariado:  {get_approval_label(soc['workers_urban'])}")
        st.text(f"Campesinos:    {get_approval_label(soc['workers_rural'])}")
        st.text(f"La Tropa:      {get_approval_label(soc['soldiers'])}")
        st.divider()
        st.markdown("**Regionalismos**")
        st.text(f"Catalunya:     {get_approval_label(soc['catalans'])}")
        st.text(f"Euskadi:       {get_approval_label(soc['basques'])}")

    with tab_sec:
        sec = st.session_state.security
        st.markdown(f"**Orden Público:** {get_status_label(st.session_state.metrics['public_order'])}")
        st.text(f"Jueces (Judges): {get_loyalty_label(st.session_state.metrics['judicial_loyalty'])}")
        st.divider()
        gc = sec['guardia_civil']
        st.markdown(f"**Guardia Civil**")
        st.caption(f"{gc['manpower']:,} | {get_loyalty_label(gc['loyalty'])}")
        ga = sec['assault_guard']
        st.markdown(f"**Guardia de Asalto**")
        if ga['manpower'] > 0:
            st.caption(f"{ga['manpower']:,} | {get_loyalty_label(ga['loyalty'])}")
        else:
            st.caption("No formada")

    with tab_mil:
        mil = st.session_state.military
        pen = mil['army_peninsular']
        st.markdown("**Ejército Peninsular**")
        st.caption(f"Oficiales: {pen['officers']:,}")
        st.caption(f"Hombres: {pen['soldiers']:,}")
        st.caption(f"Oficiales: {get_loyalty_label(pen['officer_loyalty'])}")
        st.caption(f"Soldados:  {get_loyalty_label(pen['soldier_loyalty'])}")
        st.divider()
        afr = mil['army_africa']
        st.markdown("**Ejército de África**")
        st.caption(f"Oficiales: {pen['officers']:,}")
        st.caption(f"Hombres: {afr['soldiers']:,}")
        st.caption(f"Oficiales: {get_loyalty_label(afr['officer_loyalty'])}")
        st.caption(f"Regulares: {get_loyalty_label(afr['soldier_loyalty'])}")
        st.divider()
        nav = mil['navy']
        st.markdown("**La Armada**")
        st.caption(f"Buques: {nav['ships_heavy']} Pes. / {nav['ships_light']} Lig.")
        st.caption(f"Oficiales: {nav['officers']:,}")
        st.caption(f"Marineros: {nav['sailors']:,}")
        st.caption(f"Oficiales: {get_loyalty_label(nav['officer_loyalty'])}")
        st.caption(f"Marineros: {get_loyalty_label(nav['sailor_loyalty'])}")

    # ── POL — Parliamentary Politics ─────────────────────────────────────────
    with tab_pol:
        player_id = st.session_state.player_party
        player_data = st.session_state.parties.get(player_id, {})
        coalition = st.session_state.government['coalition']
        all_seats = st.session_state.parliament['seats']

        # Coalition partners
        st.caption("**Coalición**")
        for p_id in coalition:
            if p_id == player_id:
                continue
            p_data = gd.PARTIES.get(p_id, gd.PARTIES['others'])
            rel = st.session_state.parties.get(p_id, {}).get("relations", {}).get(player_id, 50)
            seats = all_seats.get(p_id, 0)
            c1, c2, c3 = st.columns([4, 2, 2])
            c1.markdown(f"<span style='color:{p_data['color']}'>{p_data['name']}</span>",
                        unsafe_allow_html=True)
            c2.caption(f"{seats}s")
            c3.caption(f"{_rel_dot(rel)} {rel}")

        st.divider()

        # Opposition
        st.caption("**Oposición**")
        for p_id, seats in sorted(all_seats.items(), key=lambda x: -x[1]):
            if seats == 0 or p_id in coalition:
                continue
            p_data = gd.PARTIES.get(p_id, gd.PARTIES['others'])
            rel = player_data.get("relations", {}).get(p_id, 50)
            c1, c2, c3 = st.columns([4, 2, 2])
            c1.markdown(f"<span style='color:{p_data['color']}'>{p_data['name']}</span>",
                        unsafe_allow_html=True)
            c2.caption(f"{seats}s")
            c3.caption(f"{_rel_dot(rel)} {rel}")

        st.divider()

        # Organisations
        st.caption("**Organizations**")
        for org_id, org in st.session_state.organizations.items():
            rep_rel = org.get("republic_relation", 50)
            mob = org.get("mobilization", 0)
            c1, c2, c3 = st.columns([4, 2, 2])
            c1.caption(org['name'].split("(")[0].strip()[:18])
            c2.caption(f"Mob {mob}")
            c3.caption(f"{_rel_dot(rep_rel)}")

        st.divider()

        # Passed laws / constitution
        laws = st.session_state.passed_laws
        if laws:
            st.caption("**Passed Laws**")
            law_labels = {
                "const_suffrage":       "✅ Art.36 Sufragio Universal",
                "const_suffrage_limited":"⚠️ Art.36 Sufragio Limitado",
                "const_art_26_radical": "✅ Art.26 Laicismo Radical",
                "const_art_26_moderate":"⚠️ Art.26 Laicismo Moderado",
                "const_art_27_strict":  "✅ Art.27 Laicismo Pleno",
                "const_art_27_moderate":"⚠️ Art.27 Conciencia Libre",
                "const_art_43":         "✅ Art.43 Divorcio Civil",
                "const_art_43_restricted":"⚠️ Art.43 Matrimonio Civil",
                "const_art_44_social":  "✅ Art.44 Expropiación Social",
                "const_art_44_liberal": "⚠️ Art.44 Propiedad Privada",
                "const_art_48_secular": "✅ Art.48 Educación Secular",
                "const_art_48_mixed":   "⚠️ Art.48 Ed. Mixta",
                "constitution_active":  "📜 Constitución Activa",
            }
            for law_id, label in law_labels.items():
                if law_id in laws:
                    st.caption(label)

    # ── PAR — Party Politics ─────────────────────────────────────────────────
    with tab_par:
        player_id = st.session_state.player_party
        player_data = st.session_state.parties.get(player_id, {})
        p_meta = gd.PARTIES.get(player_id, {})

        st.markdown(
            f'<span style="color:{p_meta.get("color","#fff")}; font-weight:bold">' +
            p_meta.get("full_name", p_meta.get("name","")) +
            '</span>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.caption(f"Members: {p_meta.get('members',0):,}")
        c2.caption(f"Inst.: {p_meta.get('institutionalization',0)}/100")

        # Factions
        st.divider()
        st.caption("**Factions**")
        factions = player_data.get("factions", {})
        for f_id, fdata in factions.items():
            name = fdata.get("name", f_id)
            strength = fdata.get("strength", 0)
            dissent = fdata.get("dissent", 0)
            # Obfuscate strength into rough label
            if strength >= 70:   str_label = "Dominant"
            elif strength >= 50: str_label = "Strong"
            elif strength >= 30: str_label = "Divided"
            else:                str_label = "Marginal"
            st.caption(f"**{name}**")
            st.caption(f"Strength: {str_label}")
            st.caption(f"Dissent:  {_dissent_bar(dissent)}")

        # Affiliated orgs
        st.divider()
        st.caption("**Affiliated Organizations**")
        affiliated = _PARTY_ORGS.get(player_id, [])
        if affiliated:
            for org_id, org_label in affiliated:
                org = st.session_state.organizations.get(org_id, {})
                members = org.get("members", 0)
                mob = org.get("mobilization", 0)
                mil_lvl = org.get("militarization", 0)
                c1, c2 = st.columns([3, 3])
                c1.caption(f"**{org_label}**")
                c2.caption(f"{members:,} mbrs")
                c1.caption(f"Mob: {mob} | Mil: {mil_lvl}")
        else:
            st.caption("—")

        # Relations to other parties (from player party's perspective)
        st.divider()
        st.caption("**Party Relations**")
        my_relations = player_data.get("relations", {})
        for p_id, rel_val in sorted(my_relations.items(), key=lambda x: -x[1]):
            if p_id in ("church", "army"):
                label = "Iglesia" if p_id == "church" else "Ejército"
                st.caption(f"{_rel_dot(rel_val)} {label}: {rel_val}")
            else:
                p_data = gd.PARTIES.get(p_id, {})
                if not p_data:
                    continue
                name = p_data.get("name", p_id)
                color = p_data.get("color", "#888")
                st.markdown(
                    f"<small>{_rel_dot(rel_val)} <span style='color:{color}'>{name}</span>: {rel_val}</small>",
                    unsafe_allow_html=True)
    
    with tab_wor:
        diplo = st.session_state.diplomacy

        def _rdot(v):
            dot = "🟢" if v >= 65 else ("🟡" if v >= 35 else "🔴")
            return f"{dot} {get_relation_label(v)}"

        st.caption("Grandes Potencias")
        col1, col2 = st.columns(2)
        col1.text(f"🇬🇧 UK:      {_rdot(diplo.get('uk', 50))}")
        col2.text(f"🇫🇷 France:  {_rdot(diplo.get('france', 60))}")
        col1.text(f"🇺🇸 USA:     {_rdot(diplo.get('usa', 50))}")
        col2.text(f"🇩🇪 Germany: {_rdot(diplo.get('germany', 45))}")
        col1.text(f"🇮🇹 Italy:   {_rdot(diplo.get('italy', 30))}")
        col2.text(f"☭  USSR:    {_rdot(diplo.get('ussr', 20))}")
        col1.text(f"🇻🇦 Vatican: {_rdot(diplo.get('vatican', 10))}")
        st.divider()
        st.caption("Vecinos y Aliados")
        col1, col2 = st.columns(2)
        col1.text(f"🇵🇹 Portugal:{_rdot(diplo.get('portugal', 35))}")
        col2.text(f"🇲🇽 México:  {_rdot(diplo.get('mexico', 85))}")
        st.text(f"🌐 Liga:     {_rdot(diplo.get('league_of_nations', 65))}")
    
    st.sidebar.divider()
    
    with st.sidebar.expander("Gabinete (Cabinet)", expanded=False):
        for key, ministry in st.session_state.ministries.items():
            if ministry['party'] is None:
                continue
            name_parts = [w for w in ministry['holder'].split() if not w.startswith('(')]
            holder = name_parts[-1] if name_parts else ministry['holder']
            party_code = gd.PARTIES.get(ministry['party'], gd.PARTIES['others'])['name']
            st.markdown(f"<small>{ministry['name']}: {holder} ({party_code})</small>", unsafe_allow_html=True)
    
    # DEBUG BUTTONS
    st.sidebar.divider()
    with st.sidebar.expander("🛠️ Developer Tools"):
        st.session_state.disable_maps = st.checkbox("Disable Maps (Developer)", value=True)
        st.session_state.disable_nudge = st.checkbox("Disable Nudge Statistics (Developer)", value=True)
        if st.button("JUMP TO: June Elections"):
            st.session_state.current_event_id = "1931_june_elections"
            st.session_state.last_outcome_text = None
            st.rerun()
        if st.button("JUMP TO: Presidential Election"):
            import engine.mechanics as mech
            st.session_state.presidential_election = mech.init_presidential_election(st.session_state)
            st.session_state.presidential_election_active = True
            st.session_state.current_event_id = None
            st.session_state.last_outcome_text = None
            st.rerun()
        if st.button("JUMP TO: Constitution Ratified"):
            st.session_state.current_event_id = "1931_constitution_ratified"
            st.session_state.last_outcome_text = None
            st.rerun()
        st.caption(f"passed_laws: {st.session_state.passed_laws}")

def render_government_actions(state):
    """Zeigt Aktionen an, die die Regierung direkt ausführen kann."""
    with st.sidebar.expander("🏛️ Government Actions"):
        
        # --- Aktion 1: Parlament auflösen ---
        can_dissolve = False
        reason = ""
        
        # Bedingungen prüfen:
        if sum(state.parliament['seats'].values()) == 0:
            reason = "No parliament to dissolve."
        elif state.metrics['coalition_stability'] > 40:
            reason = "Coalition is too stable."
        else:
            can_dissolve = True

        if st.button("Dissolve Cortes & Call Snap Election", disabled=not can_dissolve, help=reason):
            # Wenn geklickt, setzen wir einen Flag für den Haupt-Loop
            st.session_state.action_confirmation = "dissolve_parliament"
            st.rerun()

def render_vote_result(vote_data):
    """Zeigt das Ergebnis einer Abstimmung an."""
    yes = vote_data['votes']['yes']
    no = vote_data['votes']['no']
    abst = vote_data['votes']['abstain']
    total = yes + no + abst
    threshold = total // 2 + 1
    
    st.markdown("### 🗳️ Parliamentary Vote Result")

    yes_w  = max(1, yes)
    abst_w = max(1, abst)
    no_w   = max(1, no)
    
    # Visueller Balken
    if abst > 0:
        c1, c2, c3 = st.columns([3, 1, 1])
    else:
        c1, c3 = st.columns([3, 1])
    c1.success(f"YES: {yes}")
    if abst > 0: c2.warning(f"ABS: {abst}")
    c3.error(f"NO: {no}")
    
    if yes >= threshold:
        st.success(f"**BILL PASSED** ({yes} vs {no})")
    else:
        st.error(f"**BILL FAILED** ({yes} vs {no})")
        
    # Details (Wer hat wie gestimmt?)
    with st.expander("📜 Diario de Sesiones", expanded=True):
        for entry in vote_data['details']:
            st.markdown( f"<span style='color:{entry['color']}'>■</span> " f"**{entry['party']}** — {entry['text']}", unsafe_allow_html=True )

def render_desk_layout(hand, time_units):
    """Zeigt Stapel oben und Hand unten."""
    st.markdown(f"### 🕰️ Time Remaining: {time_units} Weeks")
    
    # ZONE 1: STACKS
    col1, col2 = st.columns(2)
    hand_full = len(hand) >= 5
    action = None
    
    with col1:
        st.info("**🏛️ State Affairs**\n\nLegislation, Ministries")
        if not hand_full:
            if st.button("Draw State Card", key="draw_s", use_container_width=True): action = ("draw", "state")
        else: st.button("Hand Full", disabled=True, key="dis_s", use_container_width=True)

    with col2:
        st.warning("**🚩 Party & Society**\n\nUnions, Factions")
        if not hand_full:
            if st.button("Draw Party Card", key="draw_p", use_container_width=True): action = ("draw", "party")
        else: st.button("Hand Full", disabled=True, key="dis_p", use_container_width=True)

    if action: return action

    st.divider()

    # ZONE 2: HAND
    st.markdown("#### 📂 Active Dossiers")
    if not hand: st.caption("Empty.")
    
    cols = st.columns(len(hand)) if hand else [st.container()]
    
    for i, card in enumerate(hand):
        with cols[i]:
            c_type = card.get('type', 'initiative')
            icon = "⚡" if c_type == 'reactive' else "📜"
            
            with st.container(border=True):
                st.markdown(f"**{icon} {card['title']}**")
                st.caption(f"{card['category']}")
                if time_units > 0:
                    if st.button("Open", key=f"op_{card['id']}"): return ("play", card)
                else: st.caption("No Time")
    return None

def render_card_detail(card):
    st.markdown(f"### 📂 {card['title']}")
    st.markdown(card['text'])
    st.divider()
    
    decision = None
    for opt in card['options']:
        if st.button(opt['text']): decision = opt
            
    if st.button("Cancel"): return "CANCEL"
    return decision

from engine.nudge import compute_nudge_matrix, compute_class_contributions
def render_nudge_visualization(state, target_seats):
    import altair as alt
    import pandas as pd
    from engine.nudge import compute_nudge_matrix

    df = compute_nudge_matrix(state, target_seats)

    st.markdown("### 🎯 Nudge-Matrix: Abweichungen vom Ziel")

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("delta:Q", title="Über-/Unterperformance (Sitze)"),
            y=alt.Y("party:N", sort="-x", title="Partei"),
            color=alt.Color("delta:Q", scale=alt.Scale(scheme="redblue"), legend=None),
            tooltip=["party", "actual_seats", "target_seats", "delta"]
        )
        .properties(height=300)
    )

    st.altair_chart(chart, use_container_width=True)

    st.dataframe(df)

from engine.nudge import compute_nudge_recommendations
from content.game_data import TARGET_1931

def render_nudge_recommendations(state):
    import altair as alt

    df = compute_nudge_recommendations(state, TARGET_1931)
    if df.empty:
        st.info("No nudge recommendations — results match targets closely.")
        return

    st.markdown("### 🎯 Nudge-Empfehlungen nach Klasse")

    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("pct_shift:Q", title="Empfohlene Verschiebung (Anteil)"),
            y=alt.Y("party:N", title="Partei"),
            color=alt.Color("class:N", title="Klasse"),
            tooltip=["party", "class", "pct_shift"]
        )
        .properties(height=300)
    )
    st.altair_chart(chart, use_container_width=True)

    st.markdown("#### Verbale Empfehlungen")
    for party in df["party"].unique():
        sub = df[df["party"] == party]
        parts = []
        for _, row in sub.iterrows():
            direction = "−" if row["pct_shift"] < 0 else "+"
            parts.append(f"{direction}{abs(row['pct_shift']*100):.1f}% in {row['class']}")
        st.write(f"**{party}:** " + ", ".join(parts))

def render_nudge_recommendations_detailed(state):
    from engine.nudge import compute_nudge_recommendations_detailed

    df = compute_nudge_recommendations_detailed(state, TARGET_1931)

    st.markdown("### 🎯 Automatische Nudge-Empfehlungen (Klasse + Region)")

    if df.empty:
        st.info("Keine Empfehlungen — Ergebnisse sind nah am Ziel.")
        return

    # Gruppiert nach Partei
    for party in df["party"].unique():
        st.markdown(f"#### {party}")
        sub = df[df["party"] == party]

        # Sortiere nach absolutem Effekt
        sub = sub.sort_values("pct_shift", key=lambda x: abs(x), ascending=False)

        for _, row in sub.iterrows():
            direction = "−" if row["pct_shift"] < 0 else "+"
            st.write(
                f"{direction}{abs(row['pct_shift']*100):.1f}% "
                f"in **{row['class']}** in **{row['region']}**"
            )

def render_region_vote_table(state):
    from engine.nudge import compute_votes_by_region, compute_seats_by_region

    df_votes = compute_votes_by_region(state)
    df_seats = compute_seats_by_region(state, df_votes)
    df_seats = df_seats.groupby(["region", "party"], as_index=False)["seats"].sum()

    st.markdown("### 🗳️ Stimmen & Sitze pro Region")

    # Kompakte Tabelle

    df_pivot = df_votes.pivot(index="region", columns="party", values="share")
    st.dataframe(df_pivot.style.format("{:.2%}"))

    st.markdown("### 🪑 Sitzverteilung pro Region")
    df_seat_pivot = df_seats.pivot(index="region", columns="party", values="seats")
    st.dataframe(df_seat_pivot.fillna(0).astype(int))

def render_region_summary(state):
    from engine.nudge import compute_votes_by_region
    df = compute_votes_by_region(state)

    st.markdown("### 📋 Kompakte Zusammenfassung pro Region")

    for region in df["region"].unique():
        sub = df[df["region"] == region].sort_values("share", ascending=False)
        parts = [
            f"{row['party']} {row['share']*100:.1f}%"
            for _, row in sub.iterrows()
        ]
        st.write(f"**{region}:** " + ", ".join(parts))

def _rel_dot(val):
    """Colored dot for relation values."""
    if val >= 70: return "🟢"
    if val >= 45: return "🟡"
    return "🔴"

def _loyalty_dot(val):
    if val >= 70: return "🟢"
    if val >= 40: return "🟡"
    return "🔴"

def _dissent_bar(dissent):
    """Mini ASCII dissent bar. High dissent = danger."""
    filled = round(dissent / 10)
    color = "🔴" if dissent >= 60 else ("🟡" if dissent >= 35 else "🟢")
    return f"{color} {'█' * filled}{'░' * (10 - filled)} {dissent}"

# Map of player party -> affiliated orgs for the Par tab
_PARTY_ORGS = {
    gd.PARTY_PSOE:  [("ugt", "UGT"), ("js_psoe", "Juv. Socialistas")],
    gd.PARTY_AR:    [("ateneos", "Ateneos Rep.")],
    gd.PARTY_PRR:   [("ateneos", "Ateneos Rep.")],
    gd.PARTY_PRRS:  [("ugt", "UGT"), ("ateneos", "Ateneos Rep.")],
    gd.PARTY_CNT:   [("cnt", "CNT"), ("fai", "FAI"), ("juv_lib", "Juv. Libertarias")],
}