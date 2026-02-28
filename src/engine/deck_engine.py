import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Initiative card sources.
# Each module must expose get_initiatives(state) -> list[dict].
# Add new modules here when created.
import content.initiatives.agriculture.agriculture as card_agri
import content.initiatives.politics.constitution_initiatives as card_const
import content.initiatives.military.military_reform_initiatives as card_mil
import content.initiatives.security.security_transfer_initiatives as card_sec


def get_all_potential_cards(state):
    pool = []
    for source in (card_agri, card_const, card_mil, card_sec):
        if hasattr(source, 'get_initiatives'):
            pool.extend(source.get_initiatives(state))
    return pool


def draw_specific_card(state, target_deck):
    pool = get_all_potential_cards(state)
    current_ids = [c['id'] for c in state.get('hand', [])]
    valid = [
        c for c in pool
        if c.get('deck', 'state') == target_deck and c['id'] not in current_ids
    ]
    if not valid:
        return None
    weights = [c.get('base_weight', 10) for c in valid]
    return random.choices(valid, weights=weights, k=1)[0]


def refresh_hand_for_month(state):
    current = state.get('hand', [])
    return [c for c in current if c.get('type') == 'initiative']
