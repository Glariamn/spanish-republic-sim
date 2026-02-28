import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from content.base_event import GameEvent
import content.game_data as gd
import random


class CasasViejasEvent(GameEvent):
    EVENT_ID = "1933_casas_viejas"
    """
    January 11, 1933: Anarchist uprising in Casas Viejas, a village in
    the province of Cádiz. CNT militants proclaim libertarian communism
    and seize the village. The Assault Guard is sent in.

    What follows is the wound that kills the Azaña government. The Guard
    storms a hut and shoots prisoners — possibly on orders from the
    government, possibly not. 21 dead including a 70-year-old man.

    The left is horrified. The right has a field day. 'Azaña gave the order.'
    He probably didn't. But he can't prove it, and the investigation
    he orders only drags the story out longer.

    If the Assault Guard exists and is strong, the suppression is harsher —
    more casualties, more political damage.
    If PSOE holds Interior with Prieto, he resigns in protest after learning
    the details, damaging the coalition further.

    Player must decide how to handle the aftermath.
    Fires once in January 1933.
    """

    def should_trigger(self):
        already_fired = "flag_casas_viejas" in self.state.passed_laws
        is_date = (self.state.date['year'] == 1933 and self.state.date['month'] == 1)
        return is_date and not already_fired

    def get_data(self):
        player = self.state.player_party
        ag = self.state.security.get("assault_guard", {})
        ag_active = ag.get("manpower", 0) > 0
        interior = self.state.ministries.get("interior", {})
        interior_holder = interior.get("holder", "the Interior Minister")
        prieto_holds = (
            interior.get("party") == gd.PARTY_PSOE
            and "prieto" in interior_holder.lower()
        )
        war_holder = self.state.ministries.get("war", {}).get("holder", "the War Minister")

        if ag_active:
            force_text = (
                f"It is the Guardia de Asalto that arrives in Casas Viejas — "
                f"the Republic's own creation, loyal, well-equipped. "
                f"They surround the hut of Francisco Curro Cruz, known as *Seisdedos*, "
                f"who has barricaded himself inside with his family and a few anarchists. "
                f"They storm it. They shoot the survivors in the street."
            )
        else:
            force_text = (
                f"It is the Guardia Civil that arrives in Casas Viejas. "
                f"They surround the hut of *Seisdedos* and storm it. "
                f"They shoot the survivors in the street."
            )

        if prieto_holds:
            prieto_text = (
                f"\n\n**{interior_holder}** learns the details three days later. "
                f"He is not the kind of man to pretend he didn't. "
                f"He submits his resignation from Interior quietly, without a press statement. "
                f"The coalition has lost its best administrator."
            )
            prieto_effect = {
                "modify_relation": {
                    "source": gd.PARTY_PSOE,
                    "target": player,
                    "amount": -15
                }
            }
        else:
            prieto_text = ""
            prieto_effect = {}

        return {
            "id": "1933_casas_viejas",
            "title": "Casas Viejas",
            "date_str": "11 January 1933",
            "text": f"""
            **A village in Cádiz has risen.**

            In the early hours of January 11th, CNT militants in Casas Viejas
            proclaimed *comunismo libertario* and cut the telegraph lines.
            They were eleven men with shotguns and thirty years of waiting.

            {force_text}

            Twenty-one people are dead. The images reach Madrid by evening.

            The question of who gave the order — *Tiroteadlos* — is already
            circulating in the opposition press. Did {war_holder} authorise it?
            Did Interior? The government has no clean answer.

            In the Cortes, the right demands a full inquiry.
            In the *Casas del Pueblo*, PSOE militants are asking the same question.
            {prieto_text}
            """,
            "choices": [
                {
                    "text": "Order a full independent inquiry. The government has nothing to hide.",
                    "tooltip": "Historical path. The inquiry drags out for months, "
                               "keeping the story alive. Azaña gives contradictory testimony. "
                               "Demonstrates rule of law but prolongs the damage.",
                    "success": {
                        "msg": "An independent commission is established. "
                               "The inquiry will take months. Every session is reported. "
                               "The government's credibility bleeds slowly.",
                        "effects": {
                            "add_law": "flag_casas_viejas",
                            "add_law_2": "flag_casas_viejas_inquiry",
                            "coalition_stability": -12,
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {player: -0.03, gd.PARTY_PCE: 0.02, gd.PARTY_PSOE: 0.01}
                            },
                            **prieto_effect
                        }
                    }
                },
                {
                    "text": "Defend the security forces. Order was restored. The Republic cannot be held hostage by anarchists.",
                    "tooltip": "Closes ranks with the Guard. The left is appalled. "
                               "The right pivots — now Azaña is a hypocrite who preaches "
                               "republicanism and shoots peasants.",
                    "success": {
                        "msg": "The government defends the security forces. "
                               "Order was restored — that is what matters. "
                               "The left does not forgive this.",
                        "effects": {
                            "add_law": "flag_casas_viejas",
                            "add_law_2": "flag_casas_viejas_defended",
                            "coalition_stability": -18,
                            "public_order": 5,
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {player: -0.05, gd.PARTY_PCE: 0.03, gd.PARTY_PSOE: 0.02}
                            },
                            "demographic_shift_2": {
                                "group": "workers_rural",
                                "changes": {player: -0.03, gd.PARTY_PCE: 0.02}
                            },
                            **prieto_effect
                        }
                    }
                },
                {
                    "text": "Dismiss the officers responsible. Make clear this was not government policy.",
                    "tooltip": "Throws the Guard commanders under the bus. "
                               "Angers the military. Slightly limits the political damage "
                               "but the story still runs. The dismissed officers become martyrs.",
                    "success": {
                        "msg": "The officers who gave the order are dismissed. "
                               "The government distances itself from the killings. "
                               "The press calls it a cover-up. The dismissed officers "
                               "give interviews for months.",
                        "effects": {
                            "add_law": "flag_casas_viejas",
                            "add_law_2": "flag_casas_viejas_dismissed",
                            "coalition_stability": -8,
                            "army_officer_loyalty": -12,
                            "demographic_shift": {
                                "group": "workers_urban",
                                "changes": {player: -0.02, gd.PARTY_PCE: 0.01}
                            },
                            **prieto_effect
                        }
                    }
                }
            ]
        }


class AzanaFallsEvent(GameEvent):
    EVENT_ID = "1933_azana_falls"
    """
    September 1933: Alcalá-Zamora withdraws confidence from Azaña.
    By-elections in April showed the coalition's collapse.
    Casas Viejas never stopped bleeding.
    Zamora appoints Lerroux to attempt a government.

    Fires once in September 1933, requires Casas Viejas to have happened.
    If the player has maintained high coalition stability (>45) it can be
    delayed — but Zamora's move is hard to stop entirely.
    """

    def should_trigger(self):
        already_fired = "flag_azana_falls" in self.state.passed_laws
        casas_happened = "flag_casas_viejas" in self.state.passed_laws
        constitution_done = "flag_constitution_ratified" in self.state.passed_laws
        is_date = (self.state.date['year'] == 1933 and self.state.date['month'] == 9)
        # If stability is very high, delay by one month — but it will still fire
        stability = self.state.metrics.get("coalition_stability", 50)
        if stability > 55 and self.state.date['month'] == 9:
            return False  # fires in October instead
        is_date_extended = (
            self.state.date['year'] == 1933
            and self.state.date['month'] in (9, 10)
        )
        return is_date_extended and casas_happened and constitution_done and not already_fired

    def get_data(self):
        player = self.state.player_party
        stability = self.state.metrics.get("coalition_stability", 50)
        seats = self.state.parliament.get("seats", {})
        player_seats = seats.get(player, 0)
        total_seats = sum(seats.values())

        if stability < 30:
            zamora_text = (
                "Alcalá-Zamora has been waiting for this moment. "
                "The coalition is visibly exhausted — Casas Viejas, the religious controversy, "
                "the by-elections in April. He withdraws his confidence without ceremony."
            )
        else:
            zamora_text = (
                "Alcalá-Zamora has been watching the by-election results and the "
                "press coverage since January. Despite the coalition's formal numbers, "
                "he no longer believes the government has the country's confidence. "
                "He withdraws his support."
            )

        lerroux_plausible = seats.get(gd.PARTY_PRR, 0) > 80

        return {
            "id": "1933_azana_falls",
            "title": "The Government Falls",
            "date_str": "September 1933",
            "text": f"""
            **The Azaña government is over.**

            {zamora_text}

            The Prime Minister submits his resignation to the President of the Republic.
            The reforming parliament — the Constituent Cortes — has run its course.
            The Constitution is written. The statutes are passed. The army has been
            touched, the Church separated, the land reform begun.

            Whether it was enough, or too much, or the wrong things in the wrong order —
            that will be for the electorate to decide.

            Alcalá-Zamora is already in consultation with Alejandro Lerroux.
            """,
            "choices": [
                {
                    "text": "Submit the resignation. The Republic must demonstrate it can change governments peacefully.",
                    "success": {
                        "msg": "Azaña resigns. Zamora begins consultations with Lerroux. "
                               "The Constituent Cortes is dissolved.",
                        "effects": {
                            "add_law": "flag_azana_falls",
                            "coalition_stability": -20,
                            "pending_event": "1933_lerroux_mandate"
                        }
                    }
                }
            ]
        }


class LerrouxMandateEvent(GameEvent):
    EVENT_ID = "1933_lerroux_mandate"
    """
    October 1933: Lerroux attempts to form a government and win investiture.
    Historically he failed — the left and the ERC voted against him.
    Zamora then appointed Martínez Barrio as caretaker and called elections.

    If the player's party is PSOE or left: they choose whether to bring
    Lerroux down or let him govern. Bringing him down means new elections —
    which the left will lose badly.
    """

    def should_trigger(self):
        return (
            "flag_azana_falls" in self.state.passed_laws
            and "flag_lerroux_mandate" not in self.state.passed_laws
            and self.state.get("pending_event") == "1933_lerroux_mandate"
        )

    def get_data(self):
        player = self.state.player_party
        seats = self.state.parliament.get("seats", {})
        lerroux_seats = seats.get(gd.PARTY_PRR, 0)
        player_seats = seats.get(player, 0)
        total = sum(seats.values())
        majority = total // 2 + 1

        # Can Lerroux form a majority with CEDA support?
        ceda_seats = seats.get(gd.PARTY_CEDA, 0)
        lerroux_with_ceda = lerroux_seats + ceda_seats

        if lerroux_with_ceda >= majority:
            outlook = (
                f"With CEDA support, Lerroux could reach {lerroux_with_ceda} seats — "
                f"a majority. But the CEDA is demanding ministries in return. "
                f"Zamora is reluctant to let Gil Robles into the cabinet."
            )
        else:
            outlook = (
                f"Lerroux has {lerroux_seats} seats. He cannot reach a majority "
                f"without either the left's tolerance or CEDA support. "
                f"Neither is forthcoming."
            )

        return {
            "id": "1933_lerroux_mandate",
            "title": "Lerroux Seeks Investiture",
            "date_str": "October 1933",
            "text": f"""
            **Alejandro Lerroux has been appointed Prime Minister-designate.**

            Alcalá-Zamora has asked the Radical leader to attempt to form a government.
            Lerroux — veteran politician, friend of France, enemy of the left —
            appears before the Cortes for investiture.

            {outlook}

            The left is in an uncomfortable position. Voting against Lerroux means
            new elections. The CEDA has been organising for two years, women will
            vote for the first time, and the left's record in government has not
            endeared them to the countryside.

            Voting for Lerroux means tolerating a government that will dismantle
            what the Constituent Cortes built, piece by piece.
            """,
            "choices": [
                {
                    "text": "Vote against Lerroux. Force new elections.",
                    "tooltip": "Historical path. Lerroux fails investiture. "
                               "Martínez Barrio caretaker government. Elections November 1933. "
                               "The left will almost certainly lose.",
                    "success": {
                        "msg": "Lerroux fails investiture. Zamora appoints Martínez Barrio "
                               "as caretaker. Elections are called for November.",
                        "effects": {
                            "add_law": "flag_lerroux_mandate",
                            "add_law_2": "flag_elections_called_1933",
                            "trigger_election": True,
                            "coalition_stability": -10
                        }
                    }
                },
                {
                    "text": "Tolerate a Lerroux minority government. Avoid elections we will lose.",
                    "tooltip": "Unhistorical but rational. Lerroux governs without the left "
                               "in cabinet. You preserve your seats but lose influence. "
                               "The CEDA grows angrier.",
                    "requires_party": [gd.PARTY_PSOE, gd.PARTY_AR, gd.PARTY_PRRS,
                                       gd.PARTY_ERC, gd.PARTY_PRR],
                    "success": {
                        "msg": "The left tolerates Lerroux. He forms a minority government "
                               "without socialist support. The CEDA is furious — "
                               "they expected to be let in.",
                        "effects": {
                            "add_law": "flag_lerroux_mandate",
                            "add_law_2": "flag_lerroux_tolerated",
                            "set_coalition": [gd.PARTY_PRR, gd.PARTY_DLR],
                            "coalition_stability": 15,
                            "start_pm_nomination": True,
                            "modify_relation": {
                                "source": gd.PARTY_CEDA,
                                "target": player,
                                "amount": -20
                            }
                        }
                    }
                }
            ]
        }
