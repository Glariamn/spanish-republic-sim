from .suffrage import ISSUE_EFFECTS as SUFFRAGE

ALL_ISSUE_EFFECTS = {}
ALL_ISSUE_EFFECTS.update(SUFFRAGE)

def get_issue_effects(state, vote_result):
    issue = vote_result["issue"]
    passed = vote_result["passed"]

    outcome = "full" if passed else "limited"
    effects = ALL_ISSUE_EFFECTS[issue][outcome].copy()

    # "player" ersetzen
    if "modify_relation" in effects:
        if effects["modify_relation"]["target"] == "player":
            effects["modify_relation"]["target"] = state.player_party

    return effects
