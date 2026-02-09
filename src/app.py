import streamlit as st
import content.game_data as gd  
import engine.mechanics as mech
import content.events.historical.events_1931 as ev31 
import ui.interface as ui       
import engine.deck_engine as deck_sys
import content.election_events as el_ev

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
    import copy
    
    # Core Stats
    st.session_state.date = copy.deepcopy(gd.STATE_START['date'])
    st.session_state.economy = copy.deepcopy(gd.STATE_START['economy'])
    st.session_state.metrics = copy.deepcopy(gd.STATE_START['metrics'])
    st.session_state.society = copy.deepcopy(gd.STATE_START['society'])
    st.session_state.parliament = copy.deepcopy(gd.STATE_START['parliament'])
    st.session_state.election_demographics = copy.deepcopy(gd.STATE_START['election_demographics'])
    st.session_state.ministries = copy.deepcopy(gd.MINISTRIES)
    st.session_state.government = copy.deepcopy(gd.STATE_START['government'])
    
    # Factions (from Party Data)
    st.session_state.parties = copy.deepcopy(gd.PARTIES)
    st.session_state.my_factions = copy.deepcopy(gd.PARTIES[player_party_id]['factions'])
    
    # Secondary Stats
    st.session_state.diplomacy = copy.deepcopy(gd.STATE_START['diplomacy'])
    st.session_state.security = copy.deepcopy(gd.STATE_START['security'])
    st.session_state.military = copy.deepcopy(gd.STATE_START['military'])
    st.session_state.demographics = copy.deepcopy(gd.STATE_START['demographics'])
    st.session_state.land_ownership = copy.deepcopy(gd.STATE_START['land_ownership'])
    
    st.session_state.game_active = True
    st.session_state.passed_laws = set()

    # Event System
    st.session_state.current_event_id = "1931_election_night"
    st.session_state.last_outcome_text = None 
    st.session_state.dynamic_event_data = None

    st.session_state.negotiation_active = False
    st.session_state.draft_data = None

    # Card System
    st.session_state.hand = []
    st.session_state.time_units = 3
    st.session_state.selected_card = None

if 'initialized' not in st.session_state:
    st.session_state.game_active = False
    st.session_state.initialized = True

# --- 3. HELPER: EFFECT PROCESSOR ---
def apply_effects(effects_dict):
    """Wendet Effekte an und gibt einen Log-String zurück."""
    msg_log = ""
    for k, v in effects_dict.items():
        # A. Complex Mechanics
        if k == "demographic_shift":
            res = mech.apply_demographic_vector(st.session_state, v['group'], v['changes'])
            if res: msg_log += f" | {res}"
        elif k == "modify_faction":
            mech.modify_faction_dissent(st.session_state, v['tag'], v['amount'])
        elif k == "trigger_schism":
            res = mech.execute_faction_split(st.session_state, v)
            msg_log += f" | {res}"
        elif k == "transfer_ministry":
            res = mech.transfer_ministry_to_partner(st.session_state, v)
            if res: msg_log += f" | Ministry of {res} transferred."
        elif k == "remove_party":
            mech.remove_from_coalition(st.session_state, v)
        elif k == "trigger_election":
            st.session_state.parliament['seats'] = mech.calculate_election_results(st.session_state)
            msg_log += " | Seats Reallocated."
        elif k == "modify_relation":
            # Erwartet: {"source": "psoe", "target": "accion_rep", "amount": -15}
            src = v.get("source")
            trg = v.get("target")
            amt = v.get("amount")
            res = mech.modify_party_relation(st.session_state, src, trg, amt)
            if res: msg_log += f" | {res}"
        elif k == "start_negotiation":
            partners = st.session_state.government['coalition']
            st.session_state.draft_data = mech.initialize_ministry_draft(st.session_state, partners)
            st.session_state.negotiation_active = True
            st.session_state.current_event_id = None # Election > Negotiation Scene
        
        # B. Simple Stats
        elif k in st.session_state.metrics: st.session_state.metrics[k] += v
        elif k in st.session_state.society: st.session_state.society[k] += v
        elif k == "budget_int": st.session_state.economy['budget_int'] += v
        elif k == "public_order": st.session_state.metrics['public_order'] += v
        
        # C. Laws
        elif k == "add_law": st.session_state.passed_laws.add(v)
            
    return msg_log

# --- 4. MAIN LOOP ---

# A. START MENU
if not st.session_state.game_active:
    st.title("La Segunda República")
    st.markdown("### Choose your Political Path (April 1931)")
    c1, c2, c3 = st.columns(3)
    if c1.button("🚩 PSOE (Socialists)"):
        init_game_state(gd.PARTY_PSOE); st.rerun()
    if c2.button("⚖️ Acción Republicana (Reform)"):
        init_game_state(gd.PARTY_AR); st.rerun()
    if c3.button("✝️ DLR (Conservative)"):
        init_game_state(gd.PARTY_DLR); st.rerun()

# B. GAME DASHBOARD
else:
    ui.render_sidebar()
    if sum(st.session_state.parliament['seats'].values()) > 0:
        ui.render_parliament_chart()

    # 1. FEEDBACK SCREEN
    if st.session_state.get('last_outcome_text'):
        # Wenn eine Abstimmung stattfand
        if st.session_state.get('vote_result'):
            ui.render_vote_result(st.session_state.vote_result)
            
        st.info(st.session_state.last_outcome_text)
        
        if st.button("Continue"):
            st.session_state.last_outcome_text = None
            st.session_state.vote_result = None # Reset Vote Display
            # Start Event nach Feedback clearen
            if st.session_state.current_event_id == "1931_election_night":
                st.session_state.current_event_id = "1931_macia_declaration"
            st.rerun()

    # 2. EVENT MODE (Full Screen Events)
    elif st.session_state.current_event_id:
        curr = st.session_state.current_event_id
        ev_data = None
        
        # Fetch Data
        if curr == "1931_election_night": ev_data = ev31.get_event_election_night(st.session_state)
        elif curr == "1931_macia_declaration": ev_data = ev31.get_event_macia_declaration(st.session_state)
        elif curr == "1931_cardinal_segura": ev_data = ev31.get_event_cardinal_segura(st.session_state)
        elif curr == "1931_june_elections": ev_data = ev31.get_event_june_elections(st.session_state)
        elif curr == "1931_coalition_formation": ev_data = el_ev.get_event_general_election(st.session_state)
        elif curr == "1931_ministry_distribution": ev_data = ev31.get_event_ministry_distribution(st.session_state)
        elif curr == "dynamic_event_handler": ev_data = st.session_state.dynamic_event_data
        elif curr == "end_demo": st.warning("End of Prototype."); st.stop()
        
        if ev_data:
            st.markdown(f"### 📜 {ev_data['title']}")
            st.markdown(ev_data['text'])
            st.divider()
            
            # June Elections Special: Chart zeigen
            if curr == "1931_june_elections": ui.render_parliament_chart()

            for c in ev_data['choices']:
                # Requirements Check
                allowed = c.get('requires_party', [])
                if not allowed or st.session_state.player_party in allowed:
                    if st.button(c['text'], help=c.get('tooltip')):
                        # 1. Calculate Outcome
                        base = c.get('base_chance', 100)
                        mods = c.get('modifiers', {})
                        success, _, _, _ = mech.calculate_outcome(base, mods, st.session_state)
                        
                        res = c['success'] if success else c['failure']
                        
                        # 2. Apply Effects
                        logs = apply_effects(res.get('effects', {}))
                        
                        st.session_state.last_outcome_text = res['msg'] + logs
                        
                        # 3. Chain Logic (Next Event?)
                        # Hardcoded Chains
                        if curr == "1931_election_night": pass # Wird im Feedback Screen gesetzt (s.o.)
                        elif curr == "1931_macia_declaration": st.session_state.current_event_id = None # Desk
                        elif curr == "1931_cardinal_segura": st.session_state.current_event_id = "1931_june_elections"
                        elif curr == "1931_june_elections": 
                            st.session_state.current_event_id = "1931_coalition_formation"
                        elif curr == "1931_coalition_formation": 
                            # Falls die Koalition direkt in die Verhandlung führt:
                            if st.session_state.get('negotiation_active'):
                                st.session_state.current_event_id = None 
                            else:
                                st.session_state.current_event_id = "1931_ministry_distribution"
                        elif curr == "1931_ministry_distribution": 
                            st.session_state.current_event_id = None # Zurück zum Desk
                        elif curr == "dynamic_event_handler": st.session_state.current_event_id = None
                        
                        st.rerun()
        else:
            st.error(f"Event ID not found: {curr}")

    # 2.b MINISTRY NEGOTIATION MODE (Der Draft)
    elif st.session_state.get('negotiation_active'):
        st.markdown("### 🤝 Cabinet Formation")
        
        draft = st.session_state.draft_data
        current_party = draft['order'][draft['current_index']]
        is_player_turn = (current_party == st.session_state.player_party)
        
        # --- HEADER: Wer ist dran? ---
        cols = st.columns(len(draft['order']))
        for i, p_id in enumerate(draft['order']):
            p_name = gd.PARTIES[p_id]['name']
            if i == draft['current_index']:
                cols[i].markdown(f"**👉 {p_name}**") # Highlight
            else:
                cols[i].markdown(f"{p_name}")

        st.divider()
        
        # --- SPIELFELD: Verfügbare Ministerien ---
        st.markdown("#### Available Portfolios")
        
        # Grid Layout für Ministerien
        m_cols = st.columns(3)
        
        if is_player_turn:
            st.info("It is your turn to claim a ministry.")
            
            # Button für jedes verfügbare Ministerium
            for idx, m_key in enumerate(draft['available']):
                with m_cols[idx % 3]:
                    m_name = st.session_state.ministries[m_key]['name']
                    if st.button(f"Claim {m_name}", key=f"claim_{m_key}"):
                        # LOGIC: Spieler wählt
                        # Namen auswählen (Erster aus der Liste oder Generic)
                        candidates = gd.PARTY_MINISTERS.get(st.session_state.player_party, {}).get(m_key, ["Party Appointee"])
                        
                        draft['assignments'][m_key] = {
                            'party': st.session_state.player_party,
                            'holder': candidates[0] # Default zum ersten
                        }
                        draft['available'].remove(m_key)
                        
                        # Nächster Spieler
                        draft['current_index'] = (draft['current_index'] + 1) % len(draft['order'])
                        
                        # Check End Condition (Alle verteilt ODER Runde vorbei?)
                        # Wir machen es einfach: Bis alle weg sind.
                        if not draft['available']:
                            draft['finished'] = True
                            
                        st.rerun()
            
            if st.button("Pass (Take no more ministries)"):
                # Spieler überspringt seinen Zug permanent? Oder nur diese Runde?
                # Wir entfernen den Spieler aus der Draft Order für den Rest.
                st.warning("You stepped back from further negotiations.")
                draft['order'].remove(st.session_state.player_party)
                # Index Korrektur, falls wir nicht am Ende waren
                if draft['current_index'] >= len(draft['order']):
                    draft['current_index'] = 0
                st.rerun()

        else:
            # KI IST DRAN
            with st.spinner(f"{gd.PARTIES[current_party]['name']} is deliberating..."):
                import time
                # time.sleep(1) # Künstliche Verzögerung für Effekt (optional)
                
                # KI Logik aufrufen
                pick, holder = mech.ai_pick_ministry(st.session_state, current_party, draft['available'])
                
                if pick:
                    draft['assignments'][pick] = {'party': current_party, 'holder': holder}
                    draft['available'].remove(pick)
                    last_action = f"{gd.PARTIES[current_party]['name']} took {st.session_state.ministries[pick]['name']}."
                else:
                    last_action = f"{gd.PARTIES[current_party]['name']} passed."
                
                # Nächster
                draft['current_index'] = (draft['current_index'] + 1) % len(draft['order'])
                if not draft['available']:
                    draft['finished'] = True
                
                st.toast(last_action)
                st.rerun()

        # --- ABSCHLUSS ---
        if draft['finished']:
            st.success("The Cabinet is formed!")
            st.json(draft['assignments']) # Debug View
            
            if st.button("Confirm Government"):
                # 1. State updaten
                for m_key, data in draft['assignments'].items():
                    st.session_state.ministries[m_key]['party'] = data['party']
                    st.session_state.ministries[m_key]['holder'] = data['holder']
                
                # 2. Modus beenden
                st.session_state.negotiation_active = False
                st.session_state.current_event_id = None # Zurück zum Desk
                st.rerun()

    # 3. DESK MODE (Card Game)
    else:
        # DETAIL VIEW (Eine Karte ist offen)
        if st.session_state.selected_card:
            card = st.session_state.selected_card
            decision = ui.render_card_detail(card)
            
            if decision == "CANCEL":
                st.session_state.selected_card = None; st.rerun()
                
            elif decision:
                # 1. Gesetzes-Abstimmung nötig?
                passed = True
                if 'vote_config' in decision and sum(st.session_state.parliament['seats'].values()) > 0:
                    passed, votes, details = mech.calculate_parliament_vote(st.session_state, decision)
                    st.session_state.vote_result = {'votes': votes, 'details': details}
                
                # 2. Wenn durchgegangen (oder kein Vote nötig)
                if passed:
                    res = decision['success']
                    logs = apply_effects(res.get('effects', {}))
                    if 'add_law' in res: st.session_state.passed_laws.add(res['add_law'])
                    
                    st.session_state.last_outcome_text = res['msg'] + logs
                else:
                    st.session_state.last_outcome_text = "The bill failed in the Cortes."

                # 3. Karte entfernen & Zeit abziehen
                st.session_state.hand.remove(card)
                st.session_state.time_units -= 1
                st.session_state.selected_card = None
                st.rerun()

        # OVERVIEW (Stapel & Hand)
        else:
            # Init Hand wenn leer
            if 'hand' not in st.session_state: st.session_state.hand = []
            
            action = ui.render_desk_layout(st.session_state.hand, st.session_state.time_units)
            
            if action:
                # A. KARTEN ZIEHEN
                if action[0] == "draw":
                    deck_type = action[1]
                    new_c = deck_sys.draw_specific_card(st.session_state, deck_type)
                    if new_c: 
                        st.session_state.hand.append(new_c)
                        if new_c.get('type') == 'reactive': st.toast("⚠️ Crisis Card Drawn!")
                        st.rerun()
                    else: st.warning("This deck is empty for now.")
                
                # B. KARTE ÖFFNEN
                elif action[0] == "play":
                    st.session_state.selected_card = action[1]
                    st.rerun()
            
            st.divider()
            
            # C. MONAT BEENDEN
            if st.button("End Month (Process Timeouts)"):
                timeout_log = []
                
                # 1. Timeouts verarbeiten (für Reactive Cards auf der Hand)
                for c in st.session_state.hand:
                    if c.get('type') == 'reactive' and 'timeout_effect' in c:
                        eff = c['timeout_effect']
                        logs = apply_effects(eff.get('effects', {}))
                        timeout_log.append(f"⚠️ {c['title']}: {eff['msg']}")
                
                # 2. Hand aufräumen (Reactive fliegen raus)
                st.session_state.hand = deck_sys.refresh_hand_for_month(st.session_state)
                st.session_state.time_units = 3 # Reset Time
                
                # 3. Monthly Mechanics Tick
                msg, crisis, hist_id = mech.process_monthly_tick(st.session_state)
                
                final_msg = msg
                if timeout_log: final_msg += " | " + " ".join(timeout_log)
                
                # 4. Trigger Check
                if hist_id:
                    st.session_state.current_event_id = hist_id
                elif crisis:
                    if crisis['type'] == 'event_trigger':
                        st.session_state.dynamic_event_data = crisis['event_data']
                        st.session_state.current_event_id = "dynamic_event_handler"
                    elif crisis['type'] == 'minority_government':
                        final_msg += " | ⚠️ Minority Government Warning"
                        
                st.session_state.last_outcome_text = final_msg
                st.rerun()