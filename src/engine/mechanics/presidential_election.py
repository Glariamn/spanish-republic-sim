import content.game_data as gd
import random

# --- PRESIDENTIAL CANDIDATES ---
# Each entry defines a candidate that a party can field or endorse.
# "support" = parties that will vote for this candidate if no own candidate runs
# "oppose"  = parties that will actively vote against
# "abstain" = parties likely to abstain

PRESIDENTIAL_CANDIDATES = {
    "zamora": {
        "name": "Niceto Alcalá-Zamora",
        "party": gd.PARTY_DLR,
        "description": "The consensus choice. Conservative republican, Catholic. "
                       "Acceptable to most — trusted by neither extreme.",
        "support":  [gd.PARTY_DLR, gd.PARTY_PSOE, gd.PARTY_AR, gd.PARTY_PRRS, gd.PARTY_PRR],
        "oppose":   [gd.PARTY_CEDA, gd.PARTY_MON],
        "abstain":  [gd.PARTY_PCE, gd.PARTY_CNT],
    },
    "besteiro": {
        "name": "Julián Besteiro",
        "party": gd.PARTY_PSOE,
        "description": "Moderate socialist, respected across the aisle. "
                       "A credible alternative if the left wants its own candidate.",
        "support":  [gd.PARTY_PSOE, gd.PARTY_PRRS],
        "oppose":   [gd.PARTY_DLR, gd.PARTY_PRR, gd.PARTY_CEDA, gd.PARTY_MON],
        "abstain":  [gd.PARTY_AR, gd.PARTY_PCE],
    },
    "lerroux": {
        "name": "Alejandro Lerroux",
        "party": gd.PARTY_PRR,
        "description": "Ambitious republican veteran. Broadly distrusted by the left "
                       "and the right alike. A vanity candidacy.",
        "support":  [gd.PARTY_PRR],
        "oppose":   [gd.PARTY_PSOE, gd.PARTY_AR, gd.PARTY_PRRS, gd.PARTY_CEDA],
        "abstain":  [gd.PARTY_DLR, gd.PARTY_MON],
    },
    "maura": {
        "name": "Miguel Maura",
        "party": gd.PARTY_DLR,
        "description": "Conservative republican, Interior minister. "
                       "More palatable to the right than Zamora, less to the left.",
        "support":  [gd.PARTY_DLR, gd.PARTY_PRR],
        "oppose":   [gd.PARTY_PSOE, gd.PARTY_PRRS],
        "abstain":  [gd.PARTY_AR, gd.PARTY_CEDA],
    },
}

# Which candidate each party would put forward if given the choice
PARTY_PREFERRED_CANDIDATE = {
    gd.PARTY_DLR:  "zamora",
    gd.PARTY_PSOE: None,        # Historically endorsed Zamora, no own candidate
    gd.PARTY_AR:   None,        # Backed Zamora
    gd.PARTY_PRRS: None,        # Backed Zamora
    gd.PARTY_PRR:  "lerroux",   # Would try their own man
    gd.PARTY_CEDA: None,        # Abstained or opposed
}


def get_presidential_candidates_in_race(state):
    """
    Returns the candidates actually in the race.
    A candidate runs if their sponsoring party is in parliament with seats > 0.
    Zamora always runs as the default consensus candidate.
    """
    seats = state.parliament["seats"]
    candidates_in_race = {}

    for cand_id, cand in PRESIDENTIAL_CANDIDATES.items():
        sponsor = cand["party"]
        # Zamora always in the race (consensus candidate)
        if cand_id == "zamora":
            candidates_in_race[cand_id] = cand
            continue
        # Others only run if their party has seats
        if seats.get(sponsor, 0) > 0:
            candidates_in_race[cand_id] = cand

    return candidates_in_race


def simulate_presidential_vote(state, candidates_in_race, player_endorsement=None):
    """
    Simulates the parliamentary vote for President of the Republic.
    Each party's seats flow to their preferred candidate or their endorsed one.
    
    player_endorsement: candidate_id the player's party is backing
    
    Returns: dict of {candidate_id: votes}, winner_id, details_by_party
    """
    seats = state.parliament["seats"]
    totals = {cid: 0 for cid in candidates_in_race}
    details = []

    for party_id, party_seats in seats.items():
        if party_seats == 0:
            continue

        p_data = gd.PARTIES.get(party_id, gd.PARTIES["others"])

        # Determine which candidate this party votes for
        # Priority: player endorsement (if this is the player party) > party preferred > support list > abstain
        if party_id == state.player_party and player_endorsement:
            voted_for = player_endorsement if player_endorsement in candidates_in_race else None
        else:
            voted_for = PARTY_PREFERRED_CANDIDATE.get(party_id)
            # If preferred not in race, fall back to support list
            if voted_for not in candidates_in_race:
                voted_for = None
                for cand_id, cand in candidates_in_race.items():
                    if party_id in cand.get("support", []):
                        voted_for = cand_id
                        break

        # Small noise — party discipline isn't perfect
        rebel_share = random.uniform(0.0, 0.08)
        effective_seats = int(party_seats * (1 - rebel_share))

        if voted_for and voted_for in totals:
            totals[voted_for] += effective_seats
            vote_label = candidates_in_race[voted_for]["name"]
        else:
            vote_label = "Abstain"

        details.append({
            "party": p_data["name"],
            "color": p_data.get("color", "#888"),
            "voted_for": vote_label,
            "seats": effective_seats,
        })

    # Winner = most votes (no runoff in this simplified model)
    winner_id = max(totals, key=totals.get) if totals else "zamora"
    return totals, winner_id, details


def init_presidential_election(state):
    """Initialise the presidential_election dict in session state."""
    candidates = get_presidential_candidates_in_race(state)
    return {
        "stage": "endorse",         # endorse -> vote -> done
        "candidates": candidates,
        "player_endorsement": None,
        "vote_totals": None,
        "winner_id": None,
        "details": None,
    }
