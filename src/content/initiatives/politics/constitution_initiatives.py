import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
import content.game_data as gd

# Constitution articles are debated sequentially — only one dossier active at a time.
# Order mirrors the rough historical sequence of the Cortes Constituyentes (Jul-Dec 1931).
#
#   Art. 36 — Women's Suffrage
#   Art. 26 — Religious Orders (Jesuits, Church separation)  <- crisis trigger if radical
#   Art. 27 — Freedom of Conscience                          <- crisis trigger if DLR damaged
#   Art. 43 — Civil Marriage & Divorce
#   Art. 44 — Property & Expropriation                      <- crisis trigger if stability low
#   Art. 48 — Secular Education

def get_initiatives(state):
    cards = []

    if sum(state.parliament['seats'].values()) == 0:
        return cards

    laws = state.passed_laws

    # Who is introducing the bill?
    if state.player_party in state.government['coalition']:
        initiator = "player"
        author_party = state.player_party
    elif gd.PARTY_PRRS in state.government['coalition']:
        initiator = "ally"
        author_party = gd.PARTY_PRRS
    elif gd.PARTY_PRR in state.government['coalition']:
        initiator = "ally"
        author_party = gd.PARTY_PRR
    else:
        initiator = "parliament"
        author_party = None

    def intro(p, a, parl):
        return {"player": p, "ally": a, "parliament": parl}[initiator]

    # -------------------------------------------------------------------------
    # 1. ARTICULO 36 - WOMEN'S SUFFRAGE
    # -------------------------------------------------------------------------
    if "const_suffrage" not in laws and "const_suffrage_limited" not in laws:
        cards.append({
            "id": "const_suffrage",
            "type": "initiative",
            "deck": "state",
            "category": "Constitution",
            "title": "Dossier: Article 36 - Women's Suffrage",
            "text": intro(
                "Your government introduces Article 36 for debate. ",
                "A coalition partner raises Article 36 in the Cortes. ",
                "The Cortes itself brings Article 36 to the floor. "
            ) + "Clara Campoamor (PRR) demands full equal suffrage. Victoria Kent (PRRS) "
                "argues for postponement -- fearing that Catholic influence over women voters "
                "would strengthen the Right. The left is divided against itself.",
            "base_weight": 50,
            "options": [
                {
                    "text": "Back Campoamor. Full suffrage now.",
                    "tooltip": "Historical outcome. Won by a narrow margin in the Cortes.",
                    "success": {
                        "msg": "Article 36 passes. Spain becomes one of the first countries in Europe "
                               "to enshrine universal suffrage.",
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
                    "text": "Back Kent. Postpone until the Republic is more secure.",
                    "tooltip": "Women's suffrage delayed. The feminist movement is bitterly disappointed.",
                    "success": {
                        "msg": "The Cortes votes to postpone. Clara Campoamor's fury will echo for years.",
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
        return cards

    # -------------------------------------------------------------------------
    # 2. ARTICULO 26 - THE RELIGIOUS ORDERS
    # Radical version triggers Constitution26CrisisEvent afterward.
    # -------------------------------------------------------------------------
    if "const_art_26_radical" not in laws and "const_art_26_moderate" not in laws:
        dlr_in_gov = gd.PARTY_DLR in state.government['coalition']
        dlr_rel = state.parties.get(gd.PARTY_DLR, {}).get("relations", {}).get(state.player_party, 50)

        dlr_warning = ""
        if dlr_in_gov:
            if dlr_rel < 45:
                dlr_warning = " **Warning:** DLR relations are already strained -- a radical clause risks immediate resignations."
            else:
                dlr_warning = " Alcala-Zamora (DLR) has warned he will resign if the radical draft passes."

        cards.append({
            "id": "const_art_26",
            "type": "initiative",
            "deck": "state",
            "category": "Constitution",
            "title": "Dossier: Article 26 - The Religious Orders",
            "text": intro(
                "Your government must define Spain's relationship with the Church. ",
                "Coalition partners demand a vote on the religious orders. ",
                "The anticlerical bloc pushes Article 26 to the floor. "
            ) + "The article concerns the Jesuits, the prohibition of religious education, "
                "and the end of state salaries for clergy." + dlr_warning,
            "base_weight": 50,
            "options": [
                {
                    "text": "Radical secularism. Dissolve the Jesuits.",
                    "tooltip": "Historical path. Azana: 'Spain has ceased to be Catholic.' Will trigger a coalition crisis.",
                    "success": {
                        "msg": "A radical draft is submitted. The Cortes erupts.",
                        "effects": {
                            "add_law": "const_art_26_radical",
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
                    "text": "Moderate clause. Separation without dissolution.",
                    "tooltip": "Keeps DLR in the coalition. Enrages the anticlerical left.",
                    "success": {
                        "msg": "A moderate draft passes. The Church loses state funding but keeps its schools. "
                               "The left is furious at the compromise.",
                        "effects": {
                            "trigger_vote": {
                                "issue": "const_art_26",
                                "player_position": "moderate",
                                "author_party": author_party,
                                "ideology_target": 4,
                                "modifier": 10,
                                "add_law": "const_art_26_moderate",
                                "modify_faction": {"tag": "left", "amount": 20}
                            }
                        }
                    }
                }
            ]
        })
        return cards

    # -------------------------------------------------------------------------
    # 3. ARTICULO 27 - FREEDOM OF CONSCIENCE
    # If Art. 26 was radical and DLR is still in government, a moderate reading
    # here can serve as a last concession to keep them in.
    # -------------------------------------------------------------------------
    if "const_art_27_strict" not in laws and "const_art_27_moderate" not in laws:
        art26_was_radical = "const_art_26_radical" in laws
        dlr_still_in = gd.PARTY_DLR in state.government['coalition']

        context = ""
        if art26_was_radical and dlr_still_in:
            context = (" The DLR is watching this closely -- after Article 26, this may be their "
                       "last line. A moderate reading could be the concession that keeps them in.")
        elif art26_was_radical:
            context = " After the Jesuit dissolution, this clause is almost a formality -- the Church has already broken with the Republic."

        cards.append({
            "id": "const_art_27",
            "type": "initiative",
            "deck": "state",
            "category": "Constitution",
            "title": "Dossier: Article 27 - Freedom of Conscience",
            "text": intro(
                "Your government now addresses Article 27. ",
                "The Cortes moves to Article 27. ",
                "The constitutional committee submits Article 27. "
            ) + "The article guarantees freedom of conscience and worship. "
                "The question is the degree to which the state affirms its own secularism." + context,
            "base_weight": 50,
            "options": [
                {
                    "text": "Full laicism. Spain has no official religion.",
                    "tooltip": "Extends the logic of Art. 26. May push DLR out if relations are poor.",
                    "success": {
                        "msg": "Full laicism enshrined. The confessional state is buried.",
                        "effects": {
                            "trigger_vote": {
                                "issue": "const_art_27",
                                "player_position": "full",
                                "author_party": author_party,
                                "ideology_target": 2,
                                "add_law": "const_art_27_strict"
                            }
                        }
                    }
                },
                {
                    "text": "Freedom of worship guaranteed, but state neutrality only.",
                    "tooltip": "Softer language. May satisfy DLR if their relations are not already too low.",
                    "success": {
                        "msg": "A moderate freedom of conscience clause passes. "
                               "The DLR takes note of the conciliatory language.",
                        "effects": {
                            "trigger_vote": {
                                "issue": "const_art_27",
                                "player_position": "moderate",
                                "author_party": author_party,
                                "ideology_target": 5,
                                "add_law": "const_art_27_moderate",
                                "modify_relation": {
                                    "source": gd.PARTY_DLR,
                                    "target": state.player_party,
                                    "amount": 8
                                }
                            }
                        }
                    }
                }
            ]
        })
        return cards

    # -------------------------------------------------------------------------
    # 4. ARTICULO 43 - CIVIL MARRIAGE & DIVORCE
    # Lower stakes than Art. 26 -- no coalition rupture risk on its own,
    # but a direct hit to Church relations and conservative Catholic voters.
    # -------------------------------------------------------------------------
    if "const_art_43" not in laws and "const_art_43_restricted" not in laws:
        cards.append({
            "id": "const_art_43",
            "type": "initiative",
            "deck": "state",
            "category": "Constitution",
            "title": "Dossier: Article 43 - Marriage & Divorce",
            "text": intro(
                "Your government brings the marriage question to the floor. ",
                "A coalition partner raises Article 43. ",
                "The Cortes debates the legal basis of marriage. "
            ) + "The article would establish marriage as a purely civil contract, "
                "making divorce legal for the first time in Spain. The Church calls it "
                "'an assault on the Christian family'.",
            "base_weight": 40,
            "options": [
                {
                    "text": "Civil marriage and divorce. Full secularisation of family law.",
                    "tooltip": "Historically enacted. Major blow to Church influence over daily life.",
                    "success": {
                        "msg": "Divorce is now legal in Spain. The Church issues a furious pastoral letter.",
                        "effects": {
                            "trigger_vote": {
                                "issue": "const_art_43",
                                "player_position": "full",
                                "author_party": author_party,
                                "ideology_target": 3,
                                "add_law": "const_art_43",
                                "clergy": -15,
                                "modify_relation": {
                                    "source": gd.PARTY_DLR,
                                    "target": state.player_party,
                                    "amount": -10
                                }
                            }
                        }
                    }
                },
                {
                    "text": "Civil marriage only. Divorce too radical for now.",
                    "tooltip": "Compromise. Disappoints the left but avoids the worst Church backlash.",
                    "success": {
                        "msg": "Civil marriage without divorce. A half-measure that satisfies no one fully.",
                        "effects": {
                            "trigger_vote": {
                                "issue": "const_art_43",
                                "player_position": "limited",
                                "author_party": author_party,
                                "ideology_target": 6,
                                "add_law": "const_art_43_restricted",
                                "modify_faction": {"tag": "left", "amount": 10}
                            }
                        }
                    }
                }
            ]
        })
        return cards

    # -------------------------------------------------------------------------
    # 5. ARTICULO 44 - PROPERTY & EXPROPRIATION
    # Social version can trigger ConstitutionCrisis44Event if stability is low.
    # -------------------------------------------------------------------------
    if "const_art_44_social" not in laws and "const_art_44_liberal" not in laws:
        stability = state.metrics.get("coalition_stability", 50)
        dlr_rel = state.parties.get(gd.PARTY_DLR, {}).get("relations", {}).get(state.player_party, 50)
        prr_rel = state.parties.get(gd.PARTY_PRR, {}).get("relations", {}).get(state.player_party, 50)
        crisis_risk = stability < 35 and (dlr_rel < 45 or prr_rel < 45)

        risk_text = (" **Coalition risk:** Stability is fragile and conservative partners are "
                     "already suspicious. A social clause may be the breaking point."
                     if crisis_risk else "")

        cards.append({
            "id": "const_art_44",
            "type": "initiative",
            "deck": "state",
            "category": "Constitution",
            "title": "Dossier: Article 44 - Property & Expropriation",
            "text": intro(
                "Your government tackles the economic foundations of the Republic. ",
                "The Socialists insist on defining the social utility of property. ",
                "The Cortes debates the right of the state to expropriate land. "
            ) + "Article 44 will determine the legal basis for future land reform. "
                "The Agrarians call it 'institutionalised theft'." + risk_text,
            "base_weight": 50,
            "options": [
                {
                    "text": "Property is subordinate to national social interest.",
                    "tooltip": "Historical outcome. Legal basis for the 1932 Agrarian Reform.",
                    "success": {
                        "msg": "The social clause passes. Landowners are in open revolt. "
                               "The door to land reform is now open.",
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
                    "text": "Private property strictly protected.",
                    "tooltip": "Satisfies the right but betrays the landless peasants.",
                    "success": {
                        "msg": "Strong property protections enshrined. The rural left is furious.",
                        "effects": {
                            "trigger_vote": {
                                "issue": "const_art_44",
                                "player_position": "liberal",
                                "author_party": author_party,
                                "ideology_target": 7,
                                "add_law": "const_art_44_liberal",
                                "modify_faction": {"tag": "left", "amount": 25},
                                "workers_rural": -10
                            }
                        }
                    }
                }
            ]
        })
        return cards

    # -------------------------------------------------------------------------
    # 6. ARTICULO 48 - SECULAR EDUCATION
    # Impact amplified if Art. 26 was radical.
    # -------------------------------------------------------------------------
    if "const_art_48_secular" not in laws and "const_art_48_mixed" not in laws:
        art26_radical = "const_art_26_radical" in laws
        amplifier = (
            " After the dissolution of the Jesuits, this completes their removal from public life."
            if art26_radical else
            " The Church runs a significant portion of Spanish schools -- this clause will determine whether that continues."
        )

        cards.append({
            "id": "const_art_48",
            "type": "initiative",
            "deck": "state",
            "category": "Constitution",
            "title": "Dossier: Article 48 - Education",
            "text": intro(
                "Your government addresses the education question. ",
                "Coalition partners raise Article 48. ",
                "The Cortes debates the future of Spanish schools. "
            ) + "Article 48 concerns the secularisation of education." + amplifier,
            "base_weight": 40,
            "options": [
                {
                    "text": "Fully secular public education. Religious orders out of schools.",
                    "tooltip": "Requires building state schools to replace them -- expensive. Church furious.",
                    "success": {
                        "msg": "Secular education is enshrined. Thousands of state teachers must now be trained.",
                        "effects": {
                            "trigger_vote": {
                                "issue": "const_art_48",
                                "player_position": "full",
                                "author_party": author_party,
                                "ideology_target": 2,
                                "add_law": "const_art_48_secular",
                                "clergy": -20,
                                "budget_int": -5
                            }
                        }
                    }
                },
                {
                    "text": "Mixed system. State schools expand but religious schools may continue.",
                    "tooltip": "Pragmatic. The Church keeps a foothold but loses dominance.",
                    "success": {
                        "msg": "A mixed education system is enshrined. State education will grow alongside Church schools.",
                        "effects": {
                            "trigger_vote": {
                                "issue": "const_art_48",
                                "player_position": "limited",
                                "author_party": author_party,
                                "ideology_target": 5,
                                "add_law": "const_art_48_mixed",
                                "modify_faction": {"tag": "left", "amount": 12}
                            }
                        }
                    }
                }
            ]
        })
        return cards

    return cards
