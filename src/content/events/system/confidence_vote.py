import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from content.base_event import GameEvent

class ConfidenceVoteEvent(GameEvent):
    EVENT_ID = "confidence_vote"
    
    def should_trigger(self):
        # Trigger-Bedingungen:
        # 1. Es gibt ein Parlament.
        # 2. Die Koalitionsstabilität ist kritisch niedrig (< 20).
        # 3. Es ist nicht gerade Wahlkampf.
        has_parliament = sum(self.state.parliament['seats'].values()) > 0
        is_unstable = self.state.metrics['coalition_stability'] < 20
        not_in_election = not self.state.current_event_id or "election" not in self.state.current_event_id
        
        return has_parliament and is_unstable and not_in_election

    def get_data(self):
        return {
            "id": "confidence_vote",
            "title": "Vote of No Confidence",
            "text": """
            **The government is on the brink of collapse!**
            
            Due to the extreme instability and lack of a clear mandate, the opposition has tabled a Vote of No Confidence. 
            You must now face the Cortes and prove you still command a majority.
            """,
            "choices": [
                {
                    "text": "Face the Vote",
                    "tooltip": "A parliamentary vote will decide the fate of your government.",
                    "success": {
                        "msg": "The votes are being counted...",
                        "effects": {"trigger_confidence_vote": True}
                    }
                },
                {
                    "text": "Resign Immediately",
                    "tooltip": "Avoid the humiliation. This will trigger immediate snap elections.",
                    "success": {
                        "msg": "You have resigned as Head of Government. The country prepares for new elections.",
                        "effects": {"trigger_election": True}
                    }
                }
            ]
        }