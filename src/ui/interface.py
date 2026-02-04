import streamlit as st
import pandas as pd
import altair as alt
import content.game_data as gd

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

def render_parliament_chart():
    """Zeigt die Sitzverteilung."""
    seats = st.session_state.parliament['seats']
    
    if sum(seats.values()) == 0:
        st.info("Cortes Constituyentes: No elected parliament yet.")
        st.caption("The Provisional Government rules by decree until the June elections.")
        return

    data = []
    for party_id, count in seats.items():
        if count > 0: 
            p_data = gd.PARTIES.get(party_id, gd.PARTIES["others"])
            data.append({
                "Party": p_data['name'],
                "Seats": count,
                "Color": p_data['color'],
                "Order": p_data.get('ideology_index', 5)
            })

    if not data: return

    df = pd.DataFrame(data).sort_values("Order")

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Seats', stack='normalize', axis=None),
        order=alt.Order('Order', sort='ascending'),
        color=alt.Color('Party', 
                        scale=alt.Scale(domain=df['Party'].tolist(), range=df['Color'].tolist()), 
                        legend=alt.Legend(title=None, orient="bottom", columns=6)), 
        tooltip=['Party', 'Seats']
    ).properties(height=200)
    
    st.markdown("**Cortes Generales (470 Escaños)**")
    st.altair_chart(chart, use_container_width=True)
    
    st.caption("Verteilung der Macht")
    cols = st.columns(3)
    sorted_by_size = sorted(data, key=lambda x: x['Seats'], reverse=True)[:3]
    for i, item in enumerate(sorted_by_size):
        cols[i].metric(item['Party'], item['Seats'])

def render_sidebar():
    """Die Seitenleiste."""
    st.sidebar.markdown(f"## {st.session_state.date['month']}/{st.session_state.date['year']}")
    
    party = gd.PARTIES[st.session_state.player_party]
    st.sidebar.caption("Gobierno (Head of Govt.)")
    st.sidebar.markdown(f'<h3 style="color: {party["color"]}; margin-top: -15px;">{party["name"]}</h3>', unsafe_allow_html=True)
    
    st.sidebar.write("---")
    
    tab_eco, tab_soc, tab_sec, tab_mil, tab_wor = st.sidebar.tabs(["Eco", "Soc", "Sec", "Mil", "World"])
    
    with tab_eco:
        eco = st.session_state.economy
        st.metric("Hacienda (Treasury)", format_money(eco['budget_int']))
        st.caption(f"Ingresos: +{format_money(eco['tax_revenue_int'])}/mo")
        st.metric("Precio Pan (Bread)", f"{eco['bread_price'] * eco['inflation']:.2f} ₧")
        col1, col2 = st.columns(2)
        col1.metric("Paro (Unempl.)", f"{eco['unemployment']}%")
        col2.metric("Alfabetismo", f"{st.session_state.demographics['literacy']}%")
        
        # CENSUS
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
        st.caption(f"Hombres: {pen['manpower']:,}")
        st.caption(f"Oficiales: {get_loyalty_label(pen['officer_loyalty'])}")
        st.caption(f"Soldados:  {get_loyalty_label(pen['soldier_loyalty'])}")
        st.divider()
        afr = mil['army_africa']
        st.markdown("**Ejército de África**")
        st.caption(f"Hombres: {afr['manpower']:,}")
        st.caption(f"Oficiales: {get_loyalty_label(afr['officer_loyalty'])}")
        st.caption(f"Regulares: {get_loyalty_label(afr['soldier_loyalty'])}")
        st.divider()
        nav = mil['navy']
        st.markdown("**La Armada**")
        st.caption(f"Buques: {nav['ships_heavy']} Pes. / {nav['ships_light']} Lig.")
        st.caption(f"Oficiales: {get_loyalty_label(nav['officer_loyalty'])}")
        st.caption(f"Marineros: {get_loyalty_label(nav['sailor_loyalty'])}")

    with tab_wor:
        diplo = st.session_state.diplomacy
        st.markdown("**Potencias**")
        st.text(f"🇬🇧 UK:     {get_relation_label(diplo['uk'])}")
        st.text(f"🇫🇷 France: {get_relation_label(diplo['france'])}")
        st.text(f"🇺🇸 USA:    {get_relation_label(diplo['usa'])}")
        st.text(f"🇩🇪 Ger:    {get_relation_label(diplo['germany'])}")
        st.text(f"🇮🇹 Italy:  {get_relation_label(diplo['italy'])}")
        st.text(f"☭ USSR:    {get_relation_label(diplo['ussr'])}")
        st.text(f"🇻🇦 Vatican:{get_relation_label(diplo['vatican'])}")
    
    st.sidebar.divider()
    
    with st.sidebar.expander("Gabinete (Cabinet)", expanded=False):
        for key, ministry in st.session_state.ministries.items():
            holder = ministry['holder'].split()[-1]
            party_code = gd.PARTIES[ministry['party']]['name']
            st.markdown(f"<small>{ministry['name'].split()[0]}: {holder} ({party_code})</small>", unsafe_allow_html=True)
    
    # DEBUG BUTTONS
    st.sidebar.divider()
    with st.sidebar.expander("🛠️ Developer Tools"):
        if st.button("JUMP TO: June Elections"):
            st.session_state.current_event_id = "1931_june_elections"
            st.session_state.last_outcome_text = None
            st.rerun()