import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
import content.game_data as gd

def get_initiatives(state):
    cards = []
    
    # Bedingung: Parlament muss existieren
    if sum(state.parliament['seats'].values()) == 0:
        return cards

    # --- Bestimmung des Initiators (Kabinett-Logik) ---
    if state.player_party in state.government['coalition']:
        initiator = "player"
        author_party = state.player_party
    elif gd.PARTY_PRR in state.government['coalition'] or gd.PARTY_PRRS in state.government['coalition']:
        initiator = "ally"
        author_party = gd.PARTY_PRR if gd.PARTY_PRR in state.government['coalition'] else gd.PARTY_PRRS
    else:
        initiator = "parliament"
        author_party = None

    # --- 1. DOSSIER: FRAUENWAHLRECHT (ARTIKEL 36) ---
    if "const_suffrage" not in state.passed_laws and "const_suffrage_limited" not in state.passed_laws:
        intro = {
            "player": "Your government introduces Article 36 for debate. ",
            "ally": "A coalition partner raises Article 36 in the Cortes. ",
            "parliament": "The Cortes itself brings Article 36 to the floor. "
        }[initiator]

        cards.append({
            "id": "const_suffrage",
            "type": "initiative",
            "deck": "state",
            "category": "Constitution",
            "title": "Dossier: Women's Suffrage",
            "text": intro + "Clara Campoamor (PRR) argues for equal political rights for women, while Victoria Kent (PRRS) warns that clerical influence may strengthen the Right.",
            "base_weight": 50,
            "options": [
                {
                    "text": "Support full suffrage.",
                    "success": {
                        "msg": "You support full suffrage. The bill goes to the floor.",
                        "effects": {
                            "trigger_vote": {
                                "issue": "const_suffrage",
                                "player_position": "full",
                                "author_party": author_party,
                                "ideology_target": 4,
                                "add_law": "const_suffrage"
                            }
                        }
                    }
                },
                {
                    "text": "Support postponement.",
                    "success": {
                        "msg": "You support postponement. The bill goes to the floor.",
                        "effects": {
                            "trigger_vote": {
                                "issue": "const_suffrage",
                                "player_position": "limited",
                                "author_party": author_party,
                                "ideology_target": 7,
                                "add_law": "const_suffrage_limited"
                            }
                        }
                    }
                }
            ]
        })
        return cards # Nur ein Verfassungs-Dossier gleichzeitig

    # --- 2. DOSSIER: RELIGIONSGEMEINSCHAFTEN (ARTIKEL 26) ---
    if "const_art_26_radical" not in state.passed_laws and "const_art_26_moderate" not in state.passed_laws:
        intro = {
            "player": "Your government must now define Article 26. ",
            "ally": "Coalition partners demand a vote on the religious orders. ",
            "parliament": "The anticlerical bloc in the Cortes pushes Article 26 to the floor. "
        }[initiator]

        cards.append({
            "id": "const_art_26",
            "type": "initiative",
            "deck": "state",
            "category": "Constitution",
            "title": "Dossier: Article 26 (The Church)",
            "text": intro + "The debate concerns the dissolution of the Jesuits and the prohibition of religious teaching. The DLR threatens to leave the coalition if the draft is too radical.",
            "base_weight": 50,
            "options": [
                {
                    "text": "Draft a radical secularist clause.",
                    "success": {
                        "msg": "A radical draft is submitted. The Right is in uproar.",
                        "effects": {
                            "trigger_vote": {
                                "issue": "const_art_26",
                                "player_position": "radical",
                                "author_party": author_party,
                                "ideology_target": 1,
                                "modifier": -20,
                                "add_law": "const_art_26_radical"
                            }
                        }
                    }
                },
                {
                    "text": "Draft a moderate secularist clause.",
                    "success": {
                        "msg": "A moderate draft is submitted, seeking to avoid a total break with the DLR.",
                        "effects": {
                            "trigger_vote": {
                                "issue": "const_art_26",
                                "player_position": "moderate",
                                "author_party": author_party,
                                "ideology_target": 4,
                                "modifier": 10,
                                "add_law": "const_art_26_moderate"
                            }
                        }
                    }
                }
            ]
        })
        return cards

    # --- 3. DOSSIER: EIGENTUM UND ENTEIGNUNG (ARTIKEL 44) ---
    if "const_art_44_social" not in state.passed_laws and "const_art_44_liberal" not in state.passed_laws:
        intro = {
            "player": "Your government tackles the economic foundations of the state. ",
            "ally": "The Socialists insist on defining the social utility of property. ",
            "parliament": "The Cortes debates the right of the state to expropriate land. "
        }[initiator]

        cards.append({
            "id": "const_art_44",
            "type": "initiative",
            "deck": "state",
            "category": "Constitution",
            "title": "Dossier: Article 44 (Property)",
            "text": intro + "This clause will determine the legal basis for future land reforms. The Agrarians warn of 'institutionalized theft'.",
            "base_weight": 50,
            "options": [
                {
                    "text": "Property is subject to national interest.",
                    "success": {
                        "msg": "The draft prioritizes social utility. The Agrarians prepare for battle.",
                        "effects": {
                            "trigger_vote": {
                                "issue": "const_art_44",
                                "player_position": "social",
                                "author_party": author_party,
                                "ideology_target": 2,
                                "add_law": "const_art_44_social"
                            }
                        }
                    }
                },
                {
                    "text": "Maintain strict private property rights.",
                    "success": {
                        "msg": "The draft ensures property is untouchable. The Left feels betrayed.",
                        "effects": {
                            "trigger_vote": {
                                "issue": "const_art_44",
                                "player_position": "liberal",
                                "author_party": author_party,
                                "ideology_target": 7,
                                "add_law": "const_art_44_liberal"
                            }
                        }
                    }
                }
            ]
        })
        return cards

    return cards