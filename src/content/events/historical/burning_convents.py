import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from content.base_event import GameEvent
import content.game_data as gd

class BurningConventsEvent(GameEvent):
    def should_trigger(self):
        # Bedingung 1: Datum (Mai 1931)
        is_date = (self.state.date['year'] == 1931 and self.state.date['month'] == 5)
        
        # Bedingung 2: Stimmung ist aufgeheizt
        # Wenn Public Order < 50 ODER wir Segura nur "verwarnt" haben (Flag checken, noch nicht implementiert)
        is_angry = (self.state.metrics['public_order'] < 60)
        
        return is_date and is_angry

    def get_data(self):
        return {
            "id": "1931_burning_convents",
            "title": "La Quema de Conventos",
            "text": "Mobs are attacking religious buildings in Madrid and Málaga! They claim the Church is conspiring against the Republic. The Civil Guard awaits your orders.",
            "choices": [
                {
                    "text": "Intervene immediately. Send the Guardia Civil to protect the Churches.",
                    "tooltip": "Restores Order but angers the Workers/Republicans.",
                    "success": {
                        "msg": "Order is restored. The Church is relieved but wary.",
                        "effects": {
                            "public_order": 10,
                            "clergy": 10,
                            "workers_urban": -15, 
                            "modify_faction": {"tag": "left", "amount": 20} 
                        }
                    }
                },
                {
                    "text": "Do nothing ('All the convents in Spain are not worth the life of a Republican').",
                    "tooltip": "Azaña's famous quote. The Church burns.",
                    "success": {
                        "msg": "The fires burn for days. The Right is horrified and radicalizes.",
                        "effects": {
                            "public_order": -20,
                            "clergy": -30,
                            "workers_urban": 5,
                            "demographic_shift": {
                                "group": "bourgeoisie",
                                "changes": {
                                    gd.PARTY_CEDA: 0.03,
                                    gd.PARTY_MON: 0.03,
                                    gd.PARTY_DLR: -0.10
                                }
                            },
                            "coalition_stability": -10
                        }
                    }
                }
            ]
        }