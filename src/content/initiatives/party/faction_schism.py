# src/content/initiatives/party/faction_schism.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from content.base_event import GameEvent

class FactionSchismEvent(GameEvent):
    
    def should_trigger(self):
        if 'my_factions' not in self.state: return False
        
        for key, faction in self.state.my_factions.items():
            if faction['dissent'] >= 80:
                self.splitting_faction_key = key
                self.splitting_faction_name = faction['name']
                return True
                
        return False

    def get_data(self):
        key = self.splitting_faction_key
        name = self.splitting_faction_name
        
        return {
            "id": "faction_schism",
            "title": "Internal Schism!",
            "text": f"Disaster! The **{name}** faction has declared that your leadership has betrayed the party's principles. They are leaving to form a new movement.",
            "choices": [
                {
                    "text": "We cannot stop them. (Recalculate Party Strength)",
                    "tooltip": "Lose members and budget. Remaining factions grow in relative influence.",
                    "success": {
                        "msg": "The split is finalized.",
                        "effects": {
                            # Key triggert die Funktion in mechanics
                            "trigger_schism": key 
                        }
                    }
                }
            ]
        }