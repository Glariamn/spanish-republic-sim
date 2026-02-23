import streamlit as st
import content.game_data as gd  
import engine.mechanics as mech
import content.events.historical.events_1931 as ev31 
import ui.interface as ui       
import engine.deck_engine as deck_sys
import content.election_events as el_ev
import content.actions as actions
import content.events.historical.constitution_events as const
import content.events.historical.military_reform_event as mil_ev

from engine.mechanics.parliament import resolve_vote
from content.issue_effects import get_issue_effects

# --- 1. EVENT MAP (Korrigiert auf Klassen) ---
EVENT_MAP = {
    # Historical events — 1931 sequence
    "1931_election_night":                   ev31.AprilElectionNightEvent,
    "1931_macia_declaration":                ev31.MaciaDeclarationEvent,
    "1931_proclamation_of_second_republic":  ev31.ProclamationOfSecondRepublicEvent,
    "1931_provisional_government":           ev31.ProvisionalGovernmentEvent,
    "1931_cardinal_segura":                  ev31.CardinalSeguraEvent,
    "1931_june_elections":                   ev31.JuneElectionsEvent,
    # Constitution events
    "1931_lerroux_exit":                     const.LerrouxExitEvent,
    "1931_constitution_26_crisis":           const.Constitution26CrisisEvent,
    "1931_constitution_27_crisis":           const.ConstitutionCrisis27Event,
    "1931_constitution_44_crisis":           const.ConstitutionCrisis44Event,
    "1931_constitution_ratified":            const.ConstitutionRatifiedEvent,
    # Military events
    "1931_ley_azana":                        mil_ev.LeyAzanaEvent,
}

# --- 2. CONFIGURATION & STATE INIT ---
st.set_page_config(
    page_title="La Segunda República", 
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def init_game_state(player_party_id):
    st.session_state.player_party = player_party_id
    import copy
    
    for key, value in gd.STATE_START.items():
        st.session_state[key] = copy.deepcopy(value)
    
    st.session_state.parties = copy.deepcopy(gd.PARTIES)
    st.session_state.my_factions = copy.deepcopy(gd.PARTIES[player_party_id].get('factions', {}))
    st.session_state.REGIONAL_DEMOGRAPHICS = copy.deepcopy(gd.REGIONAL_DEMOGRAPHICS)
    st.session_state.CONSTITUENCIES_1931 = copy.deepcopy(gd.CONSTITUENCIES_1931)
    st.session_state.total_seats = sum(st.session_state.parliament['seats'].values())

    st.session_state.ministries = copy.deepcopy(gd.MINISTRIES)
    
    st.session_state.game_active = True
    st.session_state.passed_laws = set()
    st.session_state.current_event_id = "1931_election_night"
    st.session_state.last_outcome_text = None 
    st.session_state.dynamic_event_data = None
    st.session_state.negotiation_active = False
    st.session_state.draft_data = None
    st.session_state.hand = []
    st.session_state.time_units = 3
    st.session_state.selected_card = None
    st.session_state.action_confirmation = None
    st.session_state.event_history = []
    st.session_state.pending_event = None

    # DEBUG STUFF
    st.session_state.TARGET_1931 = copy.deepcopy(gd.TARGET_1931)

if 'initialized' not in st.session_state:
    st.session_state.game_active = False
    st.session_state.initialized = True

# --- 3. HELPER: EFFECT PROCESSOR ---
def apply_effects(effects_dict):
    msg_log = ""
    for k, v in effects_dict.items():
        if k in ["demographic_shift", "demographic_shift_2", "demographic_shift_3"]:
            res = mech.apply_demographic_vector(st.session_state, v['group'], v['changes'])
            if res: msg_log += f" | {res}"
        elif k == "modify_faction":
            mech.modify_faction_dissent(st.session_state, v)
        elif k == "trigger_schism":
            res = mech.execute_faction_split(st.session_state, v)
            msg_log += f" | {res}"
        elif k == "transfer_ministry":
            res = mech.transfer_ministry_to_partner(st.session_state, v)
            if res: msg_log += f" | Min. of {res} transferred."
        elif k == "remove_party":
            mech.remove_from_coalition(st.session_state, v)
        elif k == "trigger_election":
            log_msg = mech.call_new_election(st.session_state)
            msg_log += f" | {log_msg}"
            st.session_state.current_event_id = "generic_coalition_formation"
        elif k.startswith("modify_relation"):
            res = mech.modify_party_relation(st.session_state, v.get("source"), v.get("target"), v.get("amount"))
            if res: msg_log += f" | {res}"
        elif k == "start_pm_nomination":
            nom = mech.init_pm_nomination(st.session_state)
            nom['skip_draft'] = v.get('skip_draft', False) if isinstance(v, dict) else False
            st.session_state.pm_nomination = nom
            st.session_state.pm_nomination_active = True
            st.session_state.current_event_id = None
        elif k == "start_negotiation":
            st.session_state.draft_data = mech.initialize_ministry_draft(st.session_state, st.session_state.government['coalition'])
            st.session_state.negotiation_active = True
            st.session_state.current_event_id = None
        elif k == "start_presidential_election":
            st.session_state.presidential_election = mech.init_presidential_election(st.session_state)
            st.session_state.presidential_election_active = True
            st.session_state.current_event_id = None
        elif k == "set_coalition":
            st.session_state.government['coalition'] = v
        elif k == "trigger_confidence_vote":
            passed, votes = mech.calculate_confidence_vote(st.session_state)
            st.session_state.vote_result = {'votes': votes, 'details': []}
            if passed:
                msg_log += " | The government survived!"
                st.session_state.metrics['coalition_stability'] += 15
            else:
                msg_log += " | The government has fallen!"
                logs = apply_effects({"trigger_election": True})
                msg_log += logs
        # ── MILITARY EFFECTS ──────────────────────────────────────────────────
        elif k == "army_officer_loyalty":
            army = st.session_state.military.get("army_peninsular", {})
            army["officer_loyalty"] = max(0, min(100, army.get("officer_loyalty", 40) + v))
        elif k == "army_soldier_loyalty":
            army = st.session_state.military.get("army_peninsular", {})
            army["soldier_loyalty"] = max(0, min(100, army.get("soldier_loyalty", 60) + v))
        elif k == "army_reform_progress":
            army = st.session_state.military.get("army_peninsular", {})
            army["reform_progress"] = max(0, min(100, army.get("reform_progress", 0) + v))
        elif k == "army_readiness":
            army = st.session_state.military.get("army_peninsular", {})
            army["readiness"] = max(0, min(100, army.get("readiness", 20) + v))
        elif k == "army_efficiency":
            army = st.session_state.military.get("army_peninsular", {})
            army["efficiency"] = max(0, min(100, army.get("efficiency", 10) + v))
        elif k == "army_officers_retired":
            import random as _r
            army = st.session_state.military.get("army_peninsular", {})
            current = army.get("officers", 16000)
            retired = int(current * _r.uniform(0.35, 0.45))
            army["officers"] = current - retired
            msg_log += f" | {retired:,} officers retire on full pension."
        elif k == "army_capitanias_abolished":
            st.session_state.military["army_peninsular"]["capitanias_active"] = False
            msg_log += " | Capitanías Generales dissolved."
        elif k == "army_zaragoza_closed":
            st.session_state.military["army_peninsular"]["zaragoza_open"] = False
            msg_log += " | Academia General Militar closed."
        elif k == "assault_guard_created":
            ag = st.session_state.security.get("assault_guard", {})
            ag["manpower"] = 10000
            ag["loyalty"] = 95
            ag["equipment"] = 60
            ag["readiness"] = 50
            msg_log += " | Guardia de Asalto established."
        # ── FALLBACK METRICS ──────────────────────────────────────────────────
        elif k in st.session_state.metrics: st.session_state.metrics[k] += v
        elif k in st.session_state.society: st.session_state.society[k] += v
        elif k == "budget_int": st.session_state.economy['budget_int'] += v
        elif k == "public_order": st.session_state.metrics['public_order'] += v
        elif k == "add_law": st.session_state.passed_laws.add(v)
        elif k == "add_law_2": st.session_state.passed_laws.add(v)
        elif k == "rename_party":
            p = v["party"]
            new = v["new_name"]
            st.session_state.parties[p]["name"] = new
        elif k == "trigger_vote":
            vote_config = {
                "ideology_target": v["ideology_target"],
                "modifier": v.get("modifier", 0),
                "author_party": v.get("author_party")
            }
            passed, votes, details = mech.calculate_parliament_vote(st.session_state, {"vote_config": vote_config})
            st.session_state.vote_result = {'votes': votes, 'details': details}
            
            if passed:
                msg_log += f" | {v['issue']} PASSED in the Cortes."
                st.session_state.passed_laws.add(v["add_law"])
            else:
                msg_log += f" | {v['issue']} FAILED in the Cortes."
            
    return msg_log

# --- 4. MAIN LOOP ---
if not st.session_state.game_active:
    st.title("La Segunda República")
    c1, c2, c3 = st.columns(3)
    if c1.button("🚩 PSOE"): init_game_state(gd.PARTY_PSOE); st.rerun()
    if c2.button("⚖️ Acción Rep."): init_game_state(gd.PARTY_AR); st.rerun()
    if c3.button("✝️ DLR"): init_game_state(gd.PARTY_DLR); st.rerun()
else:
    ui.render_sidebar()
    ui.render_government_actions(st.session_state)
    if sum(st.session_state.parliament['seats'].values()) > 0:
        ui.render_top_overview(st.session_state)

    # 1. FEEDBACK SCREEN
    if st.session_state.get('last_outcome_text'):
        if st.session_state.get('vote_result'):
            ui.render_vote_result(st.session_state.vote_result)
        st.info(st.session_state.last_outcome_text)
        if st.button("Continue"):
            st.session_state.last_outcome_text = None
            st.session_state.vote_result = None
            # If a chain was queued, fire it now
            if st.session_state.get('pending_event'):
                st.session_state.current_event_id = st.session_state.pending_event
                st.session_state.pending_event = None
            st.rerun()

    # 2. ACTION CONFIRMATION
    elif st.session_state.get('action_confirmation'):
        action_data = actions.get_action(st.session_state.action_confirmation, st.session_state)
        if action_data:
            st.warning(f"### {action_data['title']}")
            st.markdown(action_data['text'])
            c1, c2 = st.columns(2)
            if c1.button(action_data['confirm_text'], type="primary"):
                logs = apply_effects(action_data['effects'])
                st.session_state.last_outcome_text = f"Action: {action_data['title']}" + logs
                st.session_state.action_confirmation = None
                st.rerun()
            if c2.button("Cancel"):
                st.session_state.action_confirmation = None
                st.rerun()

    # 3. EVENT MODE
    elif st.session_state.current_event_id:
        curr = st.session_state.current_event_id
        ev_data = None
        
        # A) KLASSEN-BASIERTE EVENTS
        if curr in EVENT_MAP:
            EventClass = EVENT_MAP[curr]
            event_instance = EventClass(st.session_state)
            ev_data = event_instance.get_data()
            
        # B) GENERISCHE WAHL (noch als Funktion)
        elif curr == "generic_coalition_formation":
             ev_data = el_ev.get_event_general_election(st.session_state)

        # C) DYNAMISCHE EVENTS (Kommen als Dict aus Mechanics)
        elif curr == "dynamic_event_handler":
            ev_data = st.session_state.dynamic_event_data
            
        if ev_data:
            st.markdown(f"### 📜 {ev_data['title']}")
            if ev_data.get('date_str'): st.caption(ev_data['date_str'])
            st.markdown('\n'.join(line.lstrip() for line in ev_data['text'].splitlines()).strip())
            st.divider()

            if "election" in curr or curr == "generic_coalition_formation": 
                ui.render_election_comparison()
            if curr == "1931_june_elections": 
                ui.render_top_overview(st.session_state)

            for idx, c in enumerate(ev_data['choices']):
                if c.get('requires_party', []) == [] or st.session_state.player_party in c.get('requires_party', []):
                    btn_key = f"choice_{curr}_{idx}"
                    if st.button(c['text'], help=c.get('tooltip'), key=btn_key):
                        success, _, _, _ = mech.calculate_outcome(
                            c.get('base_chance', 100),
                            c.get('modifiers', {}),
                            st.session_state
                        )
                        res = c['success'] if success else c.get('failure', c['success'])

                        logs = apply_effects(res.get('effects', {}))
                        st.session_state.last_outcome_text = res['msg'] + logs

                        # Chain: queue the next event for after the feedback screen
                        CHAIN = {
                            "1931_election_night":               "1931_macia_declaration",
                            "1931_macia_declaration":            "1931_proclamation_of_second_republic",
                            "1931_proclamation_of_second_republic": "1931_provisional_government",
                        }
                        if curr in CHAIN:
                            st.session_state.pending_event = CHAIN[curr]

                        if ("trigger_election" not in res.get('effects', {}) and
                                "start_negotiation" not in res.get('effects', {}) and
                                "start_pm_nomination" not in res.get('effects', {}) and
                                "start_presidential_election" not in res.get('effects', {})):
                            st.session_state.current_event_id = None

                        if curr not in st.session_state.get('event_history', []):
                            st.session_state.event_history.append(curr)

                        st.rerun()


        else:
            st.error(f"Event not found/mapped: {curr}")

    elif st.session_state.get('pm_nomination_active'):
        nom = st.session_state.pm_nomination
        candidates = nom['candidates']
        stage = nom['stage']

        st.markdown("### 👤 Nomination of the Prime Minister")
        st.caption("President Alcalá-Zamora invites coalition leaders to propose a candidate for *Presidente del Gobierno*.")
        st.divider()

        # --- STAGE 1: NOMINATE ---
        if stage == "nominate":
            st.markdown("**Who should lead the government?**")
            for i, cand in enumerate(candidates):
                if cand.get('failed'):
                    st.markdown(f"~~{cand['name']} ({cand['party_name']}, {cand['seats']} seats)~~ — *Investiture failed*")
                    continue

                is_player_party = (cand['party'] == st.session_state.player_party)
                acceptance_color = "🟢" if cand['acceptance'] >= 65 else ("🟡" if cand['acceptance'] >= 45 else "🔴")
                label = f"{'⭐ ' if i == 0 else ''}**{cand['name']}** — {cand['party_name']} ({cand['seats']} seats) {acceptance_color} {cand['acceptance']}% coalition acceptance"
                st.markdown(label)

                col1, col2 = st.columns([2, 3])
                with col1:
                    btn_label = "Nominate (your candidate)" if is_player_party else f"Support {cand['name']}"
                    if st.button(btn_label, key=f"nom_{i}"):
                        nom['chosen'] = cand
                        nom['player_supported'] = cand['party']
                        nom['stage'] = "concessions"
                        st.rerun()
                with col2:
                    if not is_player_party:
                        st.caption(f"Supporting {cand['party_name']}'s candidate will improve relations (+12).")
                st.markdown("")

        # --- STAGE 2: CONCESSIONS ---
        elif stage == "concessions":
            chosen = nom['chosen']
            wavering = mech.get_wavering_parties(st.session_state, chosen['party'])
            
            st.markdown(f"**Candidate: {chosen['name']} ({chosen['party_name']})**")
            st.markdown(f"Coalition acceptance: **{chosen['acceptance']}%**")

            if wavering:
                st.markdown("The following parties are **on the fence**. You may offer them a ministry to secure their vote.")
                for w in wavering:
                    already_conceded = w['party'] in nom['concession_parties']
                    col1, col2 = st.columns([3, 2])
                    with col1:
                        status = "✅ Concession offered" if already_conceded else f"Relation to candidate: {w['relation']}/100"
                        st.markdown(f"<span style='color:{w['color']}'>■</span> **{w['party_name']}** ({w['seats']} seats) — {status}", unsafe_allow_html=True)
                    with col2:
                        if not already_conceded:
                            if st.button(f"Offer ministry to {w['party_name']}", key=f"con_{w['party']}"):
                                nom['concession_parties'].append(w['party'])
                                st.rerun()
            else:
                st.info("No wavering parties — the coalition is broadly behind this candidate.")

            st.divider()
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Proceed to Investiture Vote", type="primary"):
                    nom['stage'] = "vote"
                    st.rerun()
            with col2:
                if st.button("← Change Candidate"):
                    nom['stage'] = "nominate"
                    nom['chosen'] = None
                    nom['concession_parties'] = []
                    st.rerun()

        # --- STAGE 3: VOTE ---
        elif stage == "vote":
            chosen = nom['chosen']
            if nom['vote_result'] is None:
                passed, for_votes, against_votes, details = mech.simulate_investiture_vote(
                    st.session_state, chosen['party'],
                    concession_parties=nom['concession_parties'],
                    player_supporting=True
                )
                nom['vote_result'] = {
                    'passed': passed, 'for': for_votes, 'against': against_votes, 'details': details
                }
                # Apply relation effects based on nomination choice
                mech.apply_nomination_relation_effects(
                    st.session_state, chosen['party'], nom['player_supported']
                )
                st.rerun()
            else:
                result = nom['vote_result']
                if result['passed']:
                    st.success(f"✅ **{chosen['name']} confirmed as Presidente del Gobierno** — {result['for']} for, {result['against']} against")
                else:
                    st.error(f"❌ **Investiture failed** — {result['for']} for, {result['against']} against")

                with st.expander("Vote breakdown"):
                    for d in result['details']:
                        label = "🏛️" if d['in_coalition'] else "⚖️"
                        st.markdown(f"<span style='color:{d['color']}'>■</span> {label} {d['party']}: {d['yeas']}Y / {d['nays']}N", unsafe_allow_html=True)

                if result['passed']:
                    if st.button("Confirm & Begin Cabinet Formation", type="primary"):
                        # Assign PM to ministries
                        if 'prime_minister' in st.session_state.ministries:
                            pm_candidates = gd.PARTY_MINISTERS.get(chosen['party'], {}).get('prime_minister', ["Party Leader"])
                            st.session_state.ministries['prime_minister']['party'] = chosen['party']
                            st.session_state.ministries['prime_minister']['holder'] = pm_candidates[0]
                        # Concession promises: set aside those ministries for the promised parties
                        for p in nom['concession_parties']:
                            # Flag them in draft so they get early pick
                            if 'concession_promises' not in st.session_state:
                                st.session_state.concession_promises = {}
                            st.session_state.concession_promises[p] = True
                        # Start ministry draft (excluding PM)
                        draft = mech.initialize_ministry_draft(st.session_state, st.session_state.government['coalition'])
                        # Remove prime_minister from draft if it snuck back in
                        if 'prime_minister' in draft['available']:
                            draft['available'].remove('prime_minister')
                        st.session_state.draft_data = draft
                        st.session_state.pm_nomination_active = False
                        st.session_state.negotiation_active = True
                        st.rerun()
                else:
                    if st.button("Try Another Candidate"):
                        # Mark this candidate as failed, reset vote
                        for c in nom['candidates']:
                            if c['party'] == chosen['party']:
                                c['failed'] = True
                        nom['chosen'] = None
                        nom['concession_parties'] = []
                        nom['vote_result'] = None
                        nom['attempts'] += 1
                        nom['stage'] = "nominate"
                        # Relations hit: coalition instability from failed investiture
                        st.session_state.metrics['coalition_stability'] -= 10
                        st.rerun()


    # 4. MINISTRY NEGOTIATION
    elif st.session_state.get('negotiation_active'):
         draft = st.session_state.draft_data
         if not draft['available']: draft['finished'] = True
         
         st.markdown("### 🤝 Cabinet Formation")
         
         if not draft['finished']:
             # Header
             cols = st.columns(len(draft['order']))
             for i, p_id in enumerate(draft['order']):
                 p_name = gd.PARTIES[p_id]['name']
                 if i == draft['current_index']:
                     cols[i].markdown(f"**👉 {p_name}**")
                 else:
                     cols[i].markdown(f"{p_name}")
             st.divider()

             st.markdown("#### Available Portfolios")
             m_cols = st.columns(3)
             current_party = draft['order'][draft['current_index']]
             is_player_turn = (current_party == st.session_state.player_party)

             if is_player_turn:
                 st.info("Your turn.")
                 for idx, m_key in enumerate(draft['available']):
                     with m_cols[idx % 3]:
                        m_name = st.session_state.ministries[m_key]['name']
                        if st.button(f"Claim {m_name}", key=m_key):
                            candidates = gd.PARTY_MINISTERS.get(st.session_state.player_party, {}).get(m_key, ["Party Appointee"])
                            draft['assignments'][m_key] = {'party': st.session_state.player_party, 'holder': candidates[0]}
                            draft['available'].remove(m_key)
                            if draft['order']:
                                draft['current_index'] = (draft['current_index'] + 1) % len(draft['order'])
                            st.rerun()
                 
                 st.markdown("---")
                 if st.button("Pass"):
                    draft['order'].remove(st.session_state.player_party)
                    if draft['order']:
                        draft['current_index'] = draft['current_index'] % len(draft['order'])
                    st.rerun()
             else:
                 # KI Zug
                 with st.spinner(f"{gd.PARTIES[current_party]['name']} deliberating..."):
                     import time; time.sleep(0.1)
                     pick, holder = mech.ai_pick_ministry(st.session_state, current_party, draft['available'])
                     if pick:
                        draft['assignments'][pick] = {'party': current_party, 'holder': holder}
                        draft['available'].remove(pick)
                     if draft['order']:
                        draft['current_index'] = (draft['current_index'] + 1) % len(draft['order'])
                     st.rerun()
         else:
             st.success("Cabinet formed.")
             for m_key, data in draft['assignments'].items():
                m_name = st.session_state.ministries[m_key]['name']
                p_name = gd.PARTIES[data['party']]['name']
                p_color = gd.PARTIES[data['party']]['color']
                st.markdown(f"**{m_name}**: <span style='color:{p_color}'>{p_name}</span>", unsafe_allow_html=True)
             
             if st.button("Confirm"):
                 for k, v in draft['assignments'].items():
                     st.session_state.ministries[k]['party'] = v['party']
                     st.session_state.ministries[k]['holder'] = v['holder']
                 st.session_state.negotiation_active = False
                 st.session_state.current_event_id = None
                 st.session_state.hand = []
                 st.session_state.time_units = 3
                 st.rerun()

    # 5. DESK MODE
    else:
        if st.session_state.selected_card:
            card = st.session_state.selected_card
            decision = ui.render_card_detail(card)
            if decision == "CANCEL":
                st.session_state.selected_card = None; st.rerun()
            elif decision:
                passed = True
                if 'vote_config' in decision and sum(st.session_state.parliament['seats'].values()) > 0:
                    passed, votes, details = mech.calculate_parliament_vote(st.session_state, decision)
                    st.session_state.vote_result = {'votes': votes, 'details': details}
                
                if passed:
                    res = decision['success']
                    logs = apply_effects(res.get('effects', {}))
                    st.session_state.last_outcome_text = res['msg'] + logs
                else:
                    st.session_state.last_outcome_text = "Bill failed."
                
                st.session_state.hand.remove(card)
                st.session_state.time_units -= 1
                st.session_state.selected_card = None
                st.rerun()
        else:
            if 'hand' not in st.session_state: st.session_state.hand = []
            action = ui.render_desk_layout(st.session_state.hand, st.session_state.time_units)
            if action:
                if action[0] == "draw":
                    new_c = deck_sys.draw_specific_card(st.session_state, action[1])
                    if new_c: st.session_state.hand.append(new_c); st.rerun()
                elif action[0] == "play":
                    st.session_state.selected_card = action[1]; st.rerun()
            
            st.divider()
            if st.button("End Month"):
                for c in st.session_state.hand:
                    if c.get('type') == 'reactive' and 'timeout_effect' in c:
                         apply_effects(c['timeout_effect']['effects'])
                st.session_state.hand = deck_sys.refresh_hand_for_month(st.session_state)
                st.session_state.time_units = 3 
                msg, crisis, hist_id = mech.process_monthly_tick(st.session_state)
                
                if hist_id:
                    if hist_id == "auto_election_trigger":
                        mech.call_new_election(st.session_state)
                        st.session_state.current_event_id = "generic_coalition_formation"
                    else:
                        st.session_state.current_event_id = hist_id
                elif crisis:
                    if crisis['type'] == 'event_trigger':
                        st.session_state.dynamic_event_data = crisis['event_data']
                        st.session_state.current_event_id = "dynamic_event_handler"
                st.session_state.last_outcome_text = msg
                st.rerun()
