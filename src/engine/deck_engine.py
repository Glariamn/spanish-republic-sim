import random
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importiere deine Module
import content.initiatives.agriculture.agriculture as card_agri

def get_all_potential_cards(state):
    pool = []
    if hasattr(card_agri, 'get_initiatives'):
        pool.extend(card_agri.get_initiatives(state))
    return pool

def draw_specific_card(state, target_deck):
    """Zieht eine Karte aus 'state' oder 'party' Stapel."""
    pool = get_all_potential_cards(state)
    current_ids = [c['id'] for c in state.get('hand', [])]
    
    valid = []
    for c in pool:
        if c.get('deck', 'state') == target_deck and c['id'] not in current_ids:
            valid.append(c)
            
    if not valid: return None
    
    weights = [c.get('base_weight', 10) for c in valid]
    return random.choices(valid, weights=weights, k=1)[0]

def refresh_hand_for_month(state):
    """Räumt Reactive Karten auf (Timeout war schon), behält Initiativen."""
    current = state.get('hand', [])
    # Behalte nur Initiativen
    new_hand = [c for c in current if c.get('type') == 'initiative']
    return new_hand