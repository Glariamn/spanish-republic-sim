import content.game_data as gd
import random

def get_pm_candidates(state):
    """
    Returns a ranked list of PM candidates from coalition partners.
    Ranked by seats * institutionalization — reflects both electoral weight
    and willingness/capacity to govern.
    DLR is excluded (they hold the presidency, not the premiership).
    """
    coalition = state.government['coalition']
    coalition_seats = sum(state.parliament["seats"].get(p, 0) for p in coalition)
    SEAT_THRESHOLD = max(5, int(coalition_seats * 0.08))

    candidates = []
    for p in coalition:
        if p not in gd.PARTY_MINISTERS:
            continue
        if p == gd.PARTY_DLR:
            continue  # Holds presidency, not PM role
        seats = state.parliament["seats"].get(p, 0)
        if p != state.player_party and seats < SEAT_THRESHOLD:
            continue

        inst = gd.PARTIES.get(p, {}).get("institutionalization", 50)
        score = seats * inst / 100

        name = gd.PARTY_MINISTERS.get(p, {}).get("prime_minister", ["Party Leader"])[0]
        party_data = gd.PARTIES.get(p, {})

        # Coalition acceptance: weighted avg relation to candidate's party across coalition seats
        acceptance_weighted = 0
        total_coalition_seats = 0
        for other_p in coalition:
            other_seats = state.parliament["seats"].get(other_p, 0)
            if other_seats == 0:
                continue
            # Use live state relations (may have been modified by events)
            rel = state.parties.get(other_p, {}).get("relations", {}).get(p, 50)
            acceptance_weighted += other_seats * (rel / 100)
            total_coalition_seats += other_seats

        acceptance_pct = int((acceptance_weighted / max(1, total_coalition_seats)) * 100)

        candidates.append({
            "party": p,
            "name": name,
            "party_name": party_data.get("name", p),
            "color": party_data.get("color", "#888888"),
            "seats": seats,
            "score": score,
            "acceptance": acceptance_pct,
            "failed": False,  # Marked True if investiture vote fails
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    return candidates[:4]  # Show top 4 options


def get_wavering_parties(state, candidate_party):
    """
    Returns coalition parties that are on the fence (30–60 relation to candidate).
    These are the targets for concessions — below 30 they won't flip, above 60 they're already on board.
    """
    coalition = state.government['coalition']
    wavering = []
    for p in coalition:
        if p == candidate_party:
            continue
        seats = state.parliament["seats"].get(p, 0)
        if seats == 0:
            continue
        rel = state.parties.get(p, {}).get("relations", {}).get(candidate_party, 50)
        if 20 <= rel <= 60:
            wavering.append({
                "party": p,
                "party_name": gd.PARTIES.get(p, {}).get("name", p),
                "color": gd.PARTIES.get(p, {}).get("color", "#888"),
                "seats": seats,
                "relation": rel,
            })
    wavering.sort(key=lambda x: x["seats"], reverse=True)
    return wavering[:3]  # Max 3 concession targets to keep it manageable


def simulate_investiture_vote(state, candidate_party, concession_parties=None, player_supporting=True):
    """
    Simulates the investiture vote for a nominated PM candidate.
    
    - Coalition parties lean yes based on relation to candidate's party
    - Opposition parties lean no unless relation is very high
    - Concessions flip wavering parties
    - Faction dissent bleeds some coalition yes-votes
    - Player support adds a small relation-weighted nudge
    
    Returns: (passed, votes_for, votes_against, details)
    """
    if concession_parties is None:
        concession_parties = []

    coalition = state.government['coalition']
    votes_for = 0
    votes_against = 0
    details = []

    for p_id, seats in state.parliament['seats'].items():
        if seats == 0:
            continue

        party_data = gd.PARTIES.get(p_id, gd.PARTIES['others'])
        in_coalition = p_id in coalition

        # Base yes-share: relation to candidate party
        rel = state.parties.get(p_id, party_data).get("relations", {}).get(candidate_party, 50)
        base_yes = rel / 100

        # Coalition parties get a loyalty floor (they agreed to this government)
        if in_coalition:
            base_yes = max(base_yes, 0.50)

        # Player actively supporting nudges coalition partners
        if player_supporting and in_coalition and p_id != state.player_party:
            player_rel = state.parties.get(p_id, {}).get("relations", {}).get(state.player_party, 50)
            base_yes += (player_rel - 50) / 300  # subtle nudge, max ~+16%

        # Concessions flip this party strongly
        if p_id in concession_parties:
            base_yes = min(0.92, base_yes + 0.28)

        # Faction dissent bleeds yes-votes within the coalition
        if in_coalition:
            p_state_data = state.parties.get(p_id, {})
            factions = p_state_data.get("factions", {})
            if factions:
                avg_dissent = sum(f.get("dissent", 0) for f in factions.values()) / len(factions)
                rebel_share = (avg_dissent / 100) * 0.15  # up to 15% rebels
                base_yes = max(0.0, base_yes - rebel_share)

        # Small random noise
        noise = random.uniform(-0.04, 0.04)
        yes_share = max(0.0, min(1.0, base_yes + noise))

        yeas = int(seats * yes_share)
        nays = seats - yeas

        votes_for += yeas
        votes_against += nays

        details.append({
            "party": party_data["name"],
            "color": party_data["color"],
            "yeas": yeas,
            "nays": nays,
            "in_coalition": in_coalition,
        })

    passed = votes_for > votes_against
    return passed, votes_for, votes_against, details


def apply_nomination_relation_effects(state, chosen_party, player_supported_party):
    """
    Applies relation effects based on the player's nomination choice.
    Supporting another party's candidate improves relations with them.
    Pushing your own man against a consensus candidate strains relations.
    """
    effects_log = []

    if player_supported_party and player_supported_party != state.player_party:
        # Supporting their candidate: clear goodwill signal
        target_relations = state.parties.get(player_supported_party, {}).get("relations", {})
        current = target_relations.get(state.player_party, 50)
        new_val = min(100, current + 12)
        if state.player_party in target_relations:
            state.parties[player_supported_party]["relations"][state.player_party] = new_val
        effects_log.append(f"+12 relations with {gd.PARTIES.get(player_supported_party, {}).get('name', player_supported_party)}")

    elif chosen_party == state.player_party:
        # Pushing our own man — others may resent it if they had a preferred candidate
        for p in state.government['coalition']:
            if p == state.player_party or p == gd.PARTY_DLR:
                continue
            p_data = state.parties.get(p, {})
            rel = p_data.get("relations", {}).get(state.player_party, 50)
            if rel < 60:
                # Parties already lukewarm become more suspicious
                new_rel = max(0, rel - 5)
                if state.player_party in p_data.get("relations", {}):
                    state.parties[p]["relations"][state.player_party] = new_rel

    return effects_log


def init_pm_nomination(state):
    """Initialises the pm_nomination dict in session state."""
    candidates = get_pm_candidates(state)
    return {
        "stage": "nominate",        # nominate → concessions → vote → done
        "candidates": candidates,
        "chosen": None,             # The candidate dict that was selected
        "concession_parties": [],   # Party IDs that received concession offers
        "player_supported": None,   # Which party's candidate the player backed
        "vote_result": None,        # Filled after vote
        "attempts": 0,              # How many candidates have failed already
    }
