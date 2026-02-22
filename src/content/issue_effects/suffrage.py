import content.game_data as gd

ISSUE_EFFECTS = {
    "const_suffrage": {
        "full": {
            "add_law": "const_suffrage",
            "clergy": 10,
            "ar_intellectuals": 5,
            "modify_relation": {
                "source": gd.PARTY_PRR,
                "target": "player",
                "amount": 10
            },
            "msg": "The Cortes approves full women's suffrage."
        },
        "limited": {
            "add_law": "const_suffrage_limited",
            "ar_intellectuals": 10,
            "clergy": -5,
            "modify_relation": {
                "source": gd.PARTY_PRR,
                "target": "player",
                "amount": -10
            },
            "msg": "The Cortes opts for postponement."
        }
    }
}
