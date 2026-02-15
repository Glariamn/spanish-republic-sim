# src/content/actions.py
import content.game_data as gd

def get_action(action_id, state):
    """Gibt die Daten für eine generische Regierungsaktion zurück."""
    
    if action_id == "dissolve_parliament":
        return {
            "id": "dissolve_parliament",
            "title": "Dissolve the Cortes?",
            "text": "This will trigger a snap election. Your current government will be dissolved, and you will enter a heated election campaign. This action cannot be undone.",
            "confirm_text": "Confirm: Call Elections",
            "effects": {
                "trigger_election": True,
                "public_order": -15, 
                "coalition_stability": -100 
            }
        }
    
    # Hier später weitere Aktionen
    # if action_id == "declare_emergency":
    #     return { ... }
    
    return None