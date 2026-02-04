import streamlit as st
import content.game_data as gd  
import engine.mechanics as mech
import content.events_1931 as ev31
import ui.interface as ui       

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="La Segunda República", 
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. STATE INITIALIZATION ---
def init_game_state(player_party_id):
    st.session_state.player_party = player_party_id
    # Deep Copies for complex dicts/lists
    import copy
    st.session_state.date = copy.deepcopy(gd.STATE_START['date'])
    st.session_state.economy = copy.deepcopy(gd.STATE_START['economy'])
    st.session_state.metrics = copy.deepcopy(gd.STATE_START['metrics'])
    st.session_state.security = copy.deepcopy(gd.STATE_START['security'])
    st.session_state.military = copy.deepcopy(gd.STATE_START['military'])
    st.session_state.society = copy.deepcopy(gd.STATE_START['society'])
    st.session_state.diplomacy = copy.deepcopy(gd.STATE_START['diplomacy'])
    st.session_state.demographics = copy.deepcopy(gd.STATE_START['demographics'])
    st.session_state.parliament = copy.deepcopy(gd.STATE_START['parliament'])
    st.session_state.election_demographics = copy.deepcopy(gd.STATE_START['election_demographics'])
    st.session_state.ministries = copy.deepcopy(gd.MINISTRIES)
    
    st.session_state.game_active = True
    st.session_state.current_event_id = "1931_election_night"
    st.session_state.last_outcome_text = None 

if 'initialized' not in st.session_state:
    st.session_state.game_active = False
    st.session_state.initialized = True

# --- 3. MAIN LOOP ---

# A. START MENU
if not st.session_state.game_active:
    st.title("La Segunda República")
    st.markdown("### Choose your Political Path (April 1931)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.subheader("🚩 PSOE")
        st.caption("Socialists")
        if st.button("Play as PSOE"):
            init_game_state(gd.PARTY_PSOE)
            st.rerun()
    with col2:
        st.subheader("⚖️ Acción Republicana")
        st.caption("Reformists")
        if st.button("Play as Action"):
            init_game_state(gd.PARTY_AR)
            st.rerun()
    with col3:
        st.subheader("✝️ DLR")
        st.caption("Conservatives")
        if st.button("Play as Conservatives"):
            init_game_state(gd.PARTY_DLR)
            st.rerun()

# B. GAME DASHBOARD
else:
    # 1. Sidebar (from ui.interface)
    ui.render_sidebar()

    # 2. Feedback Screen
    if st.session_state.get('last_outcome_text'):
        st.markdown(f"### {st.session_state.date['month']} {st.session_state.date['year']}")
        st.write(st.session_state.last_outcome_text)
        st.write("---")
        if st.button("Continue"):
            st.session_state.last_outcome_text = None
            if st.session_state.current_event_id == "1931_election_night":
                st.session_state.current_event_id = "end_demo"
            st.rerun()
            
    # 3. Decision Screen
    else:
        # Event Logic
        current_id = st.session_state.current_event_id
        if current_id == "1931_election_night":
            event_data = ev31.get_event_election_night(st.session_state)
        elif current_id == "1931_june_elections":
            event_data = ev31.get_event_june_elections(st.session_state)
        elif current_id == "end_demo":
            st.info("End of Prototype.")
            if st.button("Restart"):
                st.session_state.clear()
                st.rerun()
            st.stop()
        else:
            st.error(f"Unknown Event: {current_id}")
            st.stop()

        # Title and Text
        st.markdown(f"### {event_data['title']}")
        st.markdown(f"**{event_data['date_str']}**")
        st.markdown(event_data['text'])
        
        st.divider()
        
        # Parliament (from ui.interface)
        ui.render_parliament_chart()
        
        st.divider()
        
        # Buttons
        for choice in event_data['choices']:
            allowed = choice.get('requires_party', [])
            my_party = st.session_state.player_party
            
            if not allowed or my_party in allowed:
                tooltip = choice.get('tooltip', '')
                if st.button(choice['text'], help=tooltip):
                    
                    # Roll outcome
                    base = choice.get('base_chance', 100)
                    mods = choice.get('modifiers', {})
                    success, _, _, _ = mech.calculate_outcome(base, mods, st.session_state)
                    
                    # Retrieve result
                    result_data = choice['success'] if success else choice['failure']
                    
                    # 1. Special: Elections
                    if result_data.get('effects', {}).get('trigger_election'):
                        new_seats = mech.calculate_election_results(st.session_state)
                        st.session_state.parliament['seats'] = new_seats
                        result_data['msg'] += " The seats have been allocated."

                    # 2. Applying the stats
                    for stat, val in result_data.get('effects', {}).items():
                        if stat == "trigger_election": continue
                        
                        if stat in st.session_state.metrics:
                            st.session_state.metrics[stat] = max(0, min(100, st.session_state.metrics[stat] + val))
                        elif stat == "budget_int":
                            st.session_state.economy['budget_int'] += val
                    
                    st.session_state.last_outcome_text = result_data['msg']
                    st.rerun()