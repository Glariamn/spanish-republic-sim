import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
import content.game_data as gd

# Security transfer initiative cards.
# Rare — base_weight 6-12. Appear only when army instability is detectable.
# Transferring a security force changes who receives their intelligence reports.
# Does not improve their loyalty to the Republic — they are what they are.


def _army_awareness(state):
    anti_rep = state.military.get("army_peninsular", {}).get(
        "factions", {}).get("anti_republican", 0)
    return (
        anti_rep > 35
        or "flag_sanjurjada" in state.passed_laws
        or state.conspiracy.get("active", False)
    )


def _holds(state, ministry):
    return state.ministries.get(ministry, {}).get("party") == state.player_party


def get_initiatives(state):
    cards = []
    laws = state.passed_laws
    gc = state.security.get("guardia_civil", {})
    carab = state.security.get("carabineros", {})

    if not _army_awareness(state):
        return cards

    # ── GUARDIA CIVIL → INTERIOR ──────────────────────────────────────────
    if (gc.get("controlling_ministry") == "war"
            and "flag_gc_transferred_interior" not in laws
            and "flag_gc_transfer_declined" not in laws
            and (_holds(state, "interior") or _holds(state, "war"))):

        interior = state.ministries.get("interior", {})
        interior_party = interior.get("party", "")
        interior_holder = interior.get("holder", "the Interior Minister")
        gc_loyalty = gc.get("loyalty_republic", 35)
        anti_rep = state.military.get("army_peninsular", {}).get(
            "factions", {}).get("anti_republican", 0)

        prieto = (interior_party == gd.PARTY_PSOE
                  and "prieto" in interior_holder.lower())
        weight = 12 if prieto else 8

        if prieto:
            text = (
                f"**Indalecio Prieto** has been watching the army numbers quietly. "
                f"He does not share the optimism of some colleagues. "
                f"Roughly {anti_rep:.0f}% of peninsular officers are now assessed as hostile "
                f"or unreliable. The Guardia Civil — currently under War Ministry command — "
                f"reports through a chain of command that may itself be compromised.\n\n"
                f"Their republican loyalty stands at {gc_loyalty:.0f}/100. "
                "Transferring them to Interior will not change that. "
                "But their intelligence will go to someone who might act on it."
            )
        else:
            text = (
                f"The Guardia Civil remains under War Ministry command. "
                f"With {anti_rep:.0f}% of army officers now assessed as politically unreliable, "
                f"there is a case for moving the GC to Interior — where at least their reports "
                f"go to a civilian minister rather than through a compromised command structure.\n\n"
                f"GC republican loyalty: {gc_loyalty:.0f}/100. The transfer won't improve that. "
                "It changes who receives their reports."
            )

        cards.append({
            "id": "sec_gc_to_interior",
            "type": "initiative",
            "deck": "state",
            "category": "Security",
            "title": "Proposal: Transfer Guardia Civil to Interior",
            "text": text,
            "base_weight": weight,
            "options": [
                {
                    "text": "Propose the transfer in cabinet.",
                    "tooltip": "GC moves to Interior. Intelligence channel changes. "
                               "Slight officer resentment.",
                    "success": {
                        "msg": "Guardia Civil transferred to Interior by cabinet order. "
                               "Their reports now go to the civilian minister.",
                        "effects": {
                            "add_law": "flag_gc_transferred_interior",
                            "transfer_security_force": {"force": "guardia_civil", "to": "interior"},
                            "army_officer_loyalty": -4,
                        }
                    }
                },
                {
                    "text": "Leave it. Not worth the friction with the generals right now.",
                    "tooltip": "GC stays under War. Card will not reappear.",
                    "success": {
                        "msg": "The proposal is shelved. Guardia Civil remains under War Ministry.",
                        "effects": {"add_law": "flag_gc_transfer_declined"}
                    }
                }
            ]
        })

    # ── CARABINEROS → INTERIOR ────────────────────────────────────────────
    if (carab.get("controlling_ministry") == "finance"
            and "flag_gc_transferred_interior" in laws
            and "flag_carabineros_transferred" not in laws
            and (_holds(state, "interior") or _holds(state, "finance"))):

        finance_holder = state.ministries.get("finance", {}).get("holder", "Finance")
        carab_loyalty = carab.get("loyalty_republic", 55)

        cards.append({
            "id": "sec_carab_to_interior",
            "type": "initiative",
            "deck": "state",
            "category": "Security",
            "title": "Proposal: Consolidate Carabineros Under Interior",
            "text": (
                f"With the Guardia Civil now under Interior, **{finance_holder}** "
                f"has raised the question of the Carabineros — a border and customs "
                f"force of 15,000 currently under Finance Ministry command.\n\n"
                f"Their republican loyalty stands at {carab_loyalty:.0f}/100 — moderate "
                f"and improvable under sustained republican management. "
                "Consolidating them under Interior creates a coherent republican "
                "security apparatus rather than three forces answering to three ministries."
            ),
            "base_weight": 6,
            "options": [
                {
                    "text": "Approve the consolidation.",
                    "tooltip": "Carabineros move to Interior.",
                    "success": {
                        "msg": "Carabineros transferred to Interior. Reorganisation begins.",
                        "effects": {
                            "add_law": "flag_carabineros_transferred",
                            "transfer_security_force": {"force": "carabineros", "to": "interior"}
                        }
                    }
                },
                {
                    "text": "Leave them under Finance for now.",
                    "success": {
                        "msg": "Carabineros remain under Finance Ministry.",
                        "effects": {}
                    }
                }
            ]
        })

    return cards
