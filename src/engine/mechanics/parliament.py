import content.game_data as gd
import random

def calculate_parliament_vote(state, bill):
    votes = {"yes": 0, "no": 0, "abstain": 0}
    details = []
    player_p = state.player_party
    author = bill.get('author_party')

    for party_id, seats in state.parliament['seats'].items():
        if seats == 0:
            continue

        party_data = state.parties.get(party_id, gd.PARTIES['others'])

        party_index = party_data.get('ideology_index', 5)
        target = bill["vote_config"]["ideology_target"]

        d = party_index - target          # signed distance
        dist = abs(d)

        # viel härtere, nichtlineare Strafe
        score = 50 - (dist ** 2) * 6      # 0→50, 1→44, 2→26, 3→-4, 4→-50

        # Koalitionsbindung
        if party_id in state.government:
            coalition_factor = state.coalition_stability / 100
            rel_to_player = party_data['relations'].get(player_p, 50)
            score += coalition_factor * (rel_to_player - 50)

            # Koalitionsbruch proportional zur Distanz
            score -= coalition_factor * dist * 5

        # Einbringer-Effekt
        if author is not None and party_id != author:
            rel_to_author = party_data['relations'].get(author, 50)
            score += (rel_to_author - 50) * 0.5

        # Spielerposition
        if bill.get("player_position") == "full":
            score += (party_data['relations'].get(player_p, 50) - 50) / 2
        elif bill.get("player_position") == "limited":
            score -= (party_data['relations'].get(player_p, 50) - 50) / 2

        # Zufällige Variation proportional zur Parteigröße
        noise = random.uniform(-0.3, 0.3) * (seats / state.total_seats)
        score += noise

        # Ja-Anteil aus Score ableiten
        yes_share = max(0.0, min(1.0, (score + 50) / 100))
        yeas = int(seats * yes_share)
        nays = seats - yeas

        votes["yes"] += yeas
        votes["no"] += nays

        details.append({
            "party": party_data['name'],
            "color": party_data['color'],
            "text": f"{yeas} Y / {nays} N"
        })

    return (votes["yes"] > votes["no"]), votes, details


def calculate_confidence_vote(state):
    votes = {"yes": 0, "no": 0, "abstain": 0}
    gov_parties = state.government['coalition']
    
    for p_id in gov_parties:
        votes['yes'] += state.parliament['seats'].get(p_id, 0)
        
    for p_id, seats in state.parliament['seats'].items():
        if p_id not in gov_parties:
            votes['no'] += seats
            
    stability_mod = state.metrics['coalition_stability'] / 100.0 
    rebels = int(votes['yes'] * (1 - stability_mod) * 0.2) 
    votes['yes'] -= rebels
    votes['no'] += rebels
    
    return (votes['yes'] > votes['no']), votes

def resolve_vote(state, issue, player_position, author_party=None):
    """
    Generic parliamentary vote resolver.
    Does NOT contain issue-specific effects.
    """

    # --- 1. Bill-Konfiguration ---
    bill = {
        "vote_config": {},
        "author_party": author_party,
        "player_position": player_position,
        "modifier": 0
    }

    # Ideologie-Ziel (rein relational)
    bill["vote_config"]["ideology_target"] = 8 if player_position == "full" else 3

    # Wenn Spieler nicht der Einbringer ist → neutral
    if author_party != state.player_party:
        bill["modifier"] = 0

    # --- 2. Abstimmung durchführen ---
    passed, votes, details = calculate_parliament_vote(state, bill)

    # --- 3. Ergebnis zurückgeben ---
    return {
        "passed": passed,
        "issue": issue,
        "player_position": player_position,
        "author_party": author_party,
        "votes": votes,
        "details": details
    }

def get_issue_effects(state, vote_result):
    issue = vote_result["issue"]
    passed = vote_result["passed"]

    outcome = "full" if passed else "limited"
    effects = ISSUE_EFFECTS[issue][outcome].copy()

    # "player" als Platzhalter ersetzen
    if "modify_relation" in effects:
        if effects["modify_relation"]["target"] == "player":
            effects["modify_relation"]["target"] = state.player_party

    return effects
