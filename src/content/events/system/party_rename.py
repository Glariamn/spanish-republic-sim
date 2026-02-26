import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from content.base_event import GameEvent
import content.game_data as gd
import random

class CEDAFoundedEvent(GameEvent):
    EVENT_ID = "1932_ceda_foundation"
    """
    Template für ein dynamisches, zustandsbasiertes Event.
    Wird jeden Monat im `process_monthly_tick` geprüft.
    """
    
    def should_trigger(self):
        """
        CEDA founded on 1932
        """

        is_correct_year = self.state.date['year'] == 1932
        if is_correct_year:
            return True
        else:
            return False

    def get_data(self):
        """
        
        """

        event_data = {
            "id": "1932_ceda_foundation",
            "title": "Fundación de la CEDA",
            "text": "Gil Robles reorganizes Acción Nacional to CEDA.",
            "choices": [
                {
                    "text": "Die Rechte formiert sich.",
                    "success": {
                        "msg": "Acción Nacional wird zur CEDA.",
                        "effects": {
                            "rename_party": {
                                "party": self.state.PARTY_CEDA,
                                "new_name": "CEDA"
                            }
                        }
                    }
                }
            ]
        }
        
        return event_data