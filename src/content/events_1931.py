import content.game_data as gd

def get_event_election_night(state):
    return {
        "id": "1931_election_night",
        "title": "La Noche Electoral (Election Night)",
        "date_str": "12. April 1931",
        "text": """
        **The telegrams are arriving.**
        
        In the rural countryside, the Monarchist candidates have won, backed by the 'Caciques' (local bosses).
        But in the provincial capitals – Madrid, Barcelona, Valencia – the Republican coalition has swept the vote!
        
        Technically, the Monarchists have more council seats total.
        Politically, the cities have spoken against the King.
        
        Crowds are gathering at the Puerta del Sol. The King's advisors are panicked.
        **What is your strategy for the transition?**
        """,
        "choices": [
            {
                "id": "mobilize_streets",
                "text": "Mobilize the Streets! Demand immediate abdication.",
                "requires_party": [gd.PARTY_PSOE, gd.PARTY_AR, gd.PARTY_PRRS], 
                "tooltip": "Risky. Uses the mob to scare the King. Might provoke the Army.",
                "base_chance": 40,
                "modifiers": {
                    "public_order": 0.5,   
                    "army_loyalty": -0.8   
                },
                "success": {
                    "msg": "The sheer size of the crowds terrifies the Palace! The King packs his bags.",
                    "effects": {"public_order": 10, "army_loyalty": -10, "budget_int": 0}
                },
                "failure": {
                    "msg": "The Civil Guard opens fire on the protesters! A bloodbath.",
                    "effects": {"public_order": -20, "army_loyalty": 5}
                }
            },
            
            {
                "id": "negotiate_transition",
                "text": "Negotiate a peaceful transfer of power with Romanones.",
                "requires_party": [gd.PARTY_AR, gd.PARTY_DLR, gd.PARTY_PRR], 
                "tooltip": "Safer, but slower. Depends on the Army staying in barracks.",
                "base_chance": 70,
                "modifiers": {
                    "army_loyalty": 0.3,      
                    "church_influence": 0.2
                },
                "success": {
                    "msg": "Admiral Aznar admits: 'Spain went to bed monarchist and woke up republican.' The King leaves quietly.",
                    "effects": {"army_loyalty": 5, "public_order": -5} 
                },
                "failure": {
                    "msg": "The King interprets your negotiation as weakness. He delays his departure.",
                    "effects": {"public_order": -15} 
                }
            },

            {
                "id": "wait_and_see",
                "text": "Wait for the official results. Do not provoke.",
                "tooltip": "Do nothing. Let history take its course.",
                "base_chance": 100, 
                "modifiers": {},
                "success": { 
                    "msg": "The momentum slows down. The Republic is declared eventually, but without your leadership.",
                    "effects": {"public_order": -10, "members": -1000} 
                }
            }
        ]
    }

def get_event_june_elections(state):
    return {
        "id": "1931_june_elections",
        "title": "Las Elecciones Constituyentes",
        "date_str": "28. Juni 1931",
        "text": """
        **Spain goes to the polls.**
        
        The provisional period is over. For the first time, the Spanish people will freely elect a parliament (Las Cortes) to draft a new Constitution.
        
        The campaign was heated. The Church urged Catholics to vote for 'Order', while the Socialists mobilized the unions with promises of land.
        The ballot boxes are closed. The count begins.
        """,
        "choices": [
            {
                "text": "Await the Results",
                "tooltip": "Calculates seats based on current demographics.",
                # Special Function in mechanics.py
                "base_chance": 100, 
                "success": {
                    "msg": "The new Cortes Generales have assembled.",
                    "effects": {
                        "trigger_election": True, # Signal for app.py
                        "public_order": 5 
                    }
                }
            }
        ]
    }