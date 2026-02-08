def confidence_vote_event(state):
    if state.metrics["coalition_stability"] > 15:
        return None

    return {
        "id": "confidence_vote",
        "category": "Government",
        "title": "Vote of Confidence",
        "text": "The government must prove it still has parliamentary support.",
        "options": [
            {
                "label": "Call confidence vote",
                "type": "ConfidenceVote"
            },
            {
                "label": "Resign",
                "effects": {"game_over": True}
            }
        ]
    }
