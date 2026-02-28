import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))
from content.base_event import GameEvent
import content.game_data as gd


def transfer_security_force(state, force_key, target_ministry):
    """
    Execute a transfer of a security force to a new ministry.
    Returns a log string.
    Caller is responsible for checking eligibility first.
    """
    force = state.security.get(force_key)
    if not force:
        return f"Unknown force: {force_key}"
    if target_ministry not in force.get("eligible_ministries", []):
        return f"{force['name']} is not eligible for {target_ministry}."
    prev = force["controlling_ministry"]
    force["controlling_ministry"] = target_ministry
    return f"{force['name']} transferred from {prev} to {target_ministry}."


class GCToInteriorEvent(GameEvent):
    """
    Semi-historical: Guardia Civil transferred from War Ministry to Interior.
    Historically this happened early under Maura, but the timing here is
    dynamic — it fires when:
      - GC is still under War Ministry
      - A sufficiently trustworthy party holds Interior (not hostile right)
      - There is some government awareness that the army situation is unstable
        (proxy: army anti_republican faction has crossed 35% OR conspiracy is active)

    If PSOE holds Interior with Prieto as holder: fires with a flavour note
    about Prieto's effectiveness. Assault Guard effectiveness bonus.
    If another republican party holds Interior: neutral version.
    If DLR holds Interior: fires reluctantly — Maura is conservative but
    does want the GC under civilian control.
    """
    EVENT_ID = "security_gc_to_interior"

    def should_trigger(self):
        gc = self.state.security.get("guardia_civil", {})
        # Only fires if GC is still under War
        if gc.get("controlling_ministry") != "war":
            return False
        # Already fired?
        if "flag_gc_transferred_interior" in self.state.passed_laws:
            return False
        # Needs some awareness trigger: either conspiracy active, or army
        # anti-republican faction above threshold, or Sanjurjada happened
        army = self.state.military.get("army_peninsular", {})
        anti_rep = army.get("factions", {}).get("anti_republican", 0)
        conspiracy_active = self.state.conspiracy.get("active", False)
        sanjurjada_happened = "flag_sanjurjada" in self.state.passed_laws

        awareness = conspiracy_active or anti_rep > 35 or sanjurjada_happened
        if not awareness:
            return False

        # Interior must be held by a non-hostile party
        interior_party = self.state.ministries.get("interior", {}).get("party", "")
        hostile = [gd.PARTY_CEDA, gd.PARTY_MON, gd.PARTY_PRR]
        return interior_party not in hostile

    def get_data(self):
        interior = self.state.ministries.get("interior", {})
        interior_party = interior.get("party", "")
        interior_holder = interior.get("holder", "the Interior Minister")
        army = self.state.military.get("army_peninsular", {})
        anti_rep = army.get("factions", {}).get("anti_republican", 0)

        prieto_holds = (
            interior_party == gd.PARTY_PSOE and
            "prieto" in interior_holder.lower()
        )
        sanjurjada = "flag_sanjurjada" in self.state.passed_laws

        if prieto_holds:
            context = (
                f"**Indalecio Prieto** has been watching the army numbers. "
                f"He does not share Quiroga's optimism. "
                f"Roughly {anti_rep:.0f}% of peninsular officers are now assessed as "
                f"hostile or unreliable to the Republic. "
                f"Prieto wants the Guardia Civil under a ministry he can actually use — "
                f"Interior — where he can direct their intelligence gathering and "
                f"reorganise their command structure away from sympathetic generals."
            )
            bonus_text = (
                "Prieto's reorganisation is thorough. "
                "The Guardia Civil's intelligence reports now flow directly to Interior. "
                "The Assault Guard's coordination with GC improves significantly."
            )
            bonus_effects = {
                "assault_guard_effectiveness": 10  # handled in app.py if registered
            }
        elif sanjurjada:
            context = (
                f"The Sanjurjada has shaken confidence in army command structures. "
                f"**{interior_holder}** argues that the Guardia Civil — "
                f"a paramilitary force with {anti_rep:.0f}% of army officers now assessed as "
                f"unreliable — should not remain under generals who may themselves be compromised. "
                f"Moving them to Interior is a precaution."
            )
            bonus_text = (
                "The transfer is administrative, not ideological. "
                "The GC remains what it is — but their orders now come from a civilian minister."
            )
            bonus_effects = {}
        else:
            context = (
                f"**{interior_holder}** has raised the question of command over "
                f"the Guardia Civil in cabinet. With {anti_rep:.0f}% of army officers "
                f"assessed as politically unreliable, leaving the GC under War Ministry "
                f"command is a risk. "
                f"Interior is the natural home for a domestic security force."
            )
            bonus_text = "The transfer is noted in the Official Gazette."
            bonus_effects = {}

        return {
            "id": "security_gc_to_interior",
            "title": "Guardia Civil: Transfer to Interior Ministry",
            "text": f"""
            {context}

            The Guardia Civil has 28,000 men, complete rural coverage, and its own
            command structure independent of the regular army. Whoever controls their
            orders controls the only organised armed presence in most of Spain's
            countryside.

            The question is not whether to transfer them — it is whether to trust
            that Interior can actually use them if the moment comes.
            The GC's loyalty to the Republic is low regardless of who gives their orders.
            """,
            "choices": [
                {
                    "text": f"Transfer the Guardia Civil to {interior.get('name', 'Interior')}.",
                    "tooltip": "GC intelligence now flows through Interior. "
                               "Does not improve their loyalty — but makes their reports available.",
                    "success": {
                        "msg": f"Guardia Civil transferred to Interior Ministry. {bonus_text}",
                        "effects": {
                            "add_law": "flag_gc_transferred_interior",
                            **bonus_effects
                        }
                    }
                },
                {
                    "text": "Leave the Guardia Civil under War. Don't create friction with the generals.",
                    "tooltip": "Avoids a political fight. GC stays under army command. "
                               "No intelligence improvement.",
                    "success": {
                        "msg": "The Guardia Civil remains under War Ministry. "
                               "The proposal is shelved for now.",
                        "effects": {
                            "add_law": "flag_gc_transfer_declined"
                        }
                    }
                }
            ]
        }


class CarabinerosToInteriorEvent(GameEvent):
    """
    Semi-historical: Carabineros transferred from Finance to Interior.
    Fires if PSOE or left holds Interior, Prieto or Negrín holds Finance,
    and there's political motivation (conspiracy awareness or late 1930s context).
    Historically this happened in 1937 under Negrín — earlier here if conditions align.
    """
    EVENT_ID = "security_carabineros_to_interior"

    def should_trigger(self):
        carab = self.state.security.get("carabineros", {})
        if carab.get("controlling_ministry") != "finance":
            return False
        if "flag_carabineros_transferred" in self.state.passed_laws:
            return False
        # Needs GC already transferred (logical sequence)
        if "flag_gc_transferred_interior" not in self.state.passed_laws:
            return False
        # Finance must be PSOE (Prieto or Negrín)
        finance_party = self.state.ministries.get("finance", {}).get("party", "")
        return finance_party == gd.PARTY_PSOE

    def get_data(self):
        finance = self.state.ministries.get("finance", {})
        finance_holder = finance.get("holder", "the Finance Minister")
        interior = self.state.ministries.get("interior", {})

        return {
            "id": "security_carabineros_to_interior",
            "title": "Carabineros: Consolidation Under Interior",
            "text": f"""
            **{finance_holder}** has proposed consolidating the Carabineros —
            currently a Finance Ministry force — under Interior.

            The Carabineros are a border and customs force, 15,000 strong.
            Their loyalty to the Republic is moderate but improvable.
            Under Interior, they can be reorganised alongside the Assault Guard
            and used as a republican counterweight to the Guardia Civil
            in border regions.

            {finance_holder} argues this makes administrative sense and
            frees Finance from a security responsibility it was never designed to hold.
            """,
            "choices": [
                {
                    "text": "Approve the transfer.",
                    "success": {
                        "msg": f"Carabineros transferred to Interior Ministry. "
                               f"Their reorganisation under republican command begins.",
                        "effects": {
                            "add_law": "flag_carabineros_transferred",
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
        }
