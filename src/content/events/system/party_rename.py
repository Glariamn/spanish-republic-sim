import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from content.base_event import GameEvent
import content.game_data as gd


class AccionPopularRenameEvent(GameEvent):
    EVENT_ID = "1932_accion_popular_rename"
    """
    April 1932: The government rules that 'Acción Nacional' is an implicitly
    monarchist name and orders it dropped. Gil Robles renames the party
    Acción Popular — wider, more neutral, deliberately vague.
    Fires once in April 1932.
    """

    def should_trigger(self):
        already_fired = "flag_accion_popular_rename" in self.state.passed_laws
        is_date = (self.state.date['year'] == 1932 and self.state.date['month'] == 4)
        return is_date and not already_fired

    def get_data(self):
        return {
            "id": "1932_accion_popular_rename",
            "title": "Acción Nacional Dissolved by Government Order",
            "date_str": "April 1932",
            "text": """
            The Azaña government has ruled that the name *Acción Nacional* carries
            implicitly monarchist connotations and orders its dissolution as a registered party.

            Gil Robles is untroubled. He re-registers the organisation under a new name:
            **Acción Popular** — broader, more neutral, and deliberately harder to attack.
            He has begun quiet negotiations with other right-wing organisations
            about a future confederation.

            The right is consolidating. It will take time, but the trajectory is clear.
            """,
            "choices": [
                {
                    "text": "Note the development. The right is organising.",
                    "success": {
                        "msg": "Acción Nacional is renamed Acción Popular. Gil Robles continues building.",
                        "effects": {
                            "add_law": "flag_accion_popular_rename",
                            "rename_party": {
                                "party": gd.PARTY_CEDA,
                                "new_name": "Acción Popular"
                            }
                        }
                    }
                }
            ]
        }


class CEDAFoundedEvent(GameEvent):
    EVENT_ID = "1933_ceda_founded"
    """
    February 1933: Acción Popular merges with Derecha Regional Valenciana and
    other provincial Catholic-conservative groups into the CEDA — Confederación
    Española de Derechas Autónomas. Gil Robles leads it.
    The largest right-wing party in Republican Spain.
    Fires once in February 1933.
    """

    def should_trigger(self):
        already_fired = "flag_ceda_founded" in self.state.passed_laws
        rename_done = "flag_accion_popular_rename" in self.state.passed_laws
        is_date = (self.state.date['year'] == 1933 and self.state.date['month'] == 2)
        return is_date and rename_done and not already_fired

    def get_data(self):
        return {
            "id": "1933_ceda_founded",
            "title": "CEDA Founded",
            "date_str": "February 1933",
            "text": """
            **José María Gil Robles** has announced the formation of the
            *Confederación Española de Derechas Autónomas* — the CEDA.

            Acción Popular merges with the Derecha Regional Valenciana, the
            Agrarian Minority, and a dozen smaller provincial Catholic and
            conservative organisations. Together they claim over 700,000 members.

            The CEDA's programme is deliberately ambiguous: it does not declare
            itself republican, monarchist, or fascist. It demands revision of
            the Constitution — above all the religious articles — and presents
            itself as the defender of *"Religion, Fatherland, Family, Order,
            Work, and Property."*

            Gil Robles has studied Dollfuss in Austria. He is patient.
            He intends to reach power through elections, then use it to
            transform the Republic from within.

            The left calls this *accidentalism* — using republican legality
            as a ladder to be kicked away once the top is reached.
            Gil Robles neither confirms nor denies it.
            """,
            "choices": [
                {
                    "text": "The Republic faces its most dangerous opponent yet.",
                    "success": {
                        "msg": "The CEDA is founded. The right now has a mass party.",
                        "effects": {
                            "add_law": "flag_ceda_founded",
                            "rename_party": {
                                "party": gd.PARTY_CEDA,
                                "new_name": "CEDA"
                            },
                            "coalition_stability": -5,
                            "demographic_shift": {
                                "group": "bourgeoisie",
                                "changes": {gd.PARTY_CEDA: 0.05, gd.PARTY_MON: -0.03}
                            }
                        }
                    }
                }
            ]
        }
