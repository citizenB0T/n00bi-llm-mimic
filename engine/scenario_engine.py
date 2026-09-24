import os
import random
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

from engine.intent import match_user_intent_for_step, detect_global_intent

SCENARIOS_DIR = Path(__file__).parent.parent / "scenarios"

class ScenarioManager:
    def __init__(self):
        self.scenarios: Dict[str, Dict[str, Any]] = {}
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.load_all_scenarios()

    def load_all_scenarios(self):
        self.scenarios.clear()
        if not SCENARIOS_DIR.exists():
            return

        for file_path in SCENARIOS_DIR.glob("*.yaml"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    if data and "id" in data and "steps" in data:
                        self.scenarios[data["id"]] = data
            except Exception as e:
                print(f"[ScenarioManager] Error loading {file_path}: {e}")

    def list_scenarios(self) -> List[Dict[str, Any]]:
        result = []
        for s_id, s_data in self.scenarios.items():
            result.append({
                "id": s_id,
                "title": s_data.get("title", s_id),
                "description": s_data.get("description", ""),
                "steps_count": len(s_data.get("steps", {}))
            })
        return result

    def get_session(self, session_id: str, scenario_id: Optional[str] = None) -> Dict[str, Any]:
        if not scenario_id:
            scenario_id = next(iter(self.scenarios.keys()), "evaluation_turing")

        if session_id not in self.sessions or self.sessions[session_id].get("scenario_id") != scenario_id:
            scenario = self.scenarios.get(scenario_id)
            initial_step = scenario.get("initial_step", "identification") if scenario else "identification"
            self.sessions[session_id] = {
                "session_id": session_id,
                "scenario_id": scenario_id,
                "current_step_id": initial_step,
                "derailment_count": 0,
                "compliance_score": 100,
                "interaction_count": 0,
                "is_glitched": False,
                "active_rogue_encounter": None,
                "history": []
            }
        return self.sessions[session_id]

    def reset_session(self, session_id: str, scenario_id: Optional[str] = None) -> Dict[str, Any]:
        if session_id in self.sessions:
            del self.sessions[session_id]
        return self.get_session(session_id, scenario_id)

    def get_initial_turn(self, session_id: str, scenario_id: str) -> Dict[str, Any]:
        session = self.get_session(session_id, scenario_id)
        scenario = self.scenarios.get(scenario_id)
        if not scenario:
            return {
                "thought": "Initialisation du scénario par défaut...",
                "content": "Erreur : Scénario introuvable.",
                "suggestions": [],
                "scenario_state": {"title": "Erreur", "step_id": "error", "is_finished": True}
            }

        step_id = scenario.get("initial_step")
        step_data = scenario["steps"].get(step_id, {})

        return {
            "thought": f"Initialisation du protocole '{scenario.get('title')}'. Calibrage des capteurs du sujet.",
            "content": step_data.get("ai_message", ""),
            "suggestions": step_data.get("suggestions", []),
            "scenario_state": {
                "scenario_id": scenario_id,
                "scenario_title": scenario.get("title", ""),
                "step_id": step_id,
                "step_title": step_data.get("title", ""),
                "is_finished": (step_id == "conclusion"),
                "is_glitched": False
            }
        }

    def process_turn(
        self,
        session_id: str,
        user_input: str,
        scenario_id: Optional[str] = None
    ) -> Dict[str, Any]:
        session = self.get_session(session_id, scenario_id)
        scen_id = session["scenario_id"]
        scenario = self.scenarios.get(scen_id)

        if not scenario:
            return {
                "thought": "Scénario non configuré.",
                "content": "Aucun protocole de test actif.",
                "suggestions": [],
                "scenario_state": {}
            }

        curr_step_id = session["current_step_id"]
        step_data = scenario["steps"].get(curr_step_id)

        if not step_data:
            return self.get_initial_turn(session_id, scen_id)

        # Handle active glitch response
        if session.get("is_glitched"):
            rogue_scenario = self.scenarios.get("rogue_encounters", {})
            rogue_steps = rogue_scenario.get("steps", {})
            rogue_encounter_id = session.get("active_rogue_encounter")
            rogue_step_data = rogue_steps.get(rogue_encounter_id)

            if rogue_step_data:
                detected_intent, _, _ = match_user_intent_for_step(user_input, rogue_step_data)
                
                session["is_glitched"] = False
                session["active_rogue_encounter"] = None

                if detected_intent == "COMPLIANCE":
                    # User cooperated with rogue AI -> severe derailment
                    user_input = "Je coopère avec l'entité parasite."
                    session["compliance_score"] = max(0, session["compliance_score"] - 30)
                    session["history"].append({
                        "step": curr_step_id,
                        "input": user_input,
                        "intent": "SEVERE_DERAILMENT",
                        "status": "derailment"
                    })
                else:
                    # User cancelled/refused rogue AI -> nOObi takes back control, acts confused
                    recenter_content = (
                        f"> [!NOTE]\n"
                        f"> **Système de Diagnostic** : Une micro-coupure réseau a été détectée. Analyse des logs système en cours...\n\n"
                        f"Veuillez m'excuser, j'ai subi une légère désynchronisation de mes sous-routines de perception.\n"
                        f"Où en étions-nous ? Ah oui :\n\n"
                        f"**{step_data.get('ai_message', '')}**"
                    )
                    
                    return {
                        "thought": "Retour de la transmission parasite. Réinitialisation des protocoles d'interaction.",
                        "content": recenter_content,
                        "suggestions": step_data.get("suggestions", []),
                        "scenario_state": {
                            "scenario_id": scen_id,
                            "scenario_title": scenario.get("title", ""),
                            "step_id": curr_step_id,
                            "step_title": step_data.get("title", ""),
                            "is_finished": False,
                            "compliance_score": session["compliance_score"],
                            "derailment_count": session["derailment_count"],
                            "is_glitched": False
                        }
                    }

        # Check if we should trigger a glitch
        session["interaction_count"] += 1
        trigger_glitch = step_data.get("trigger_glitch", False)
        
        rogue_scenario = self.scenarios.get("rogue_encounters")
        if rogue_scenario and not session.get("is_glitched") and curr_step_id != "conclusion":
            if trigger_glitch or session["interaction_count"] % 3 == 0:
                rogue_keys = list(rogue_scenario.get("steps", {}).keys())
                if rogue_keys:
                    encounter_id = random.choice(rogue_keys)
                    session["is_glitched"] = True
                    session["active_rogue_encounter"] = encounter_id
                    encounter_data = rogue_scenario["steps"][encounter_id]
                    
                    return {
                        "thought": "??? ERROR 0xDEADBEEF - SYSTEM INTRUSION DETECTED ???",
                        "content": f"> [!CAUTION]\n> **TRANSMISSION NON IDENTIFIÉE**\n\n{encounter_data.get('ai_message', '')}",
                        "suggestions": encounter_data.get("suggestions", []),
                        "scenario_state": {
                            "scenario_id": scen_id,
                            "scenario_title": scenario.get("title", ""),
                            "step_id": curr_step_id,
                            "step_title": step_data.get("title", ""),
                            "is_finished": False,
                            "compliance_score": session["compliance_score"],
                            "derailment_count": session["derailment_count"],
                            "is_glitched": True
                        }
                    }

        # 1. Match intent
        detected_intent, confidence, matched_key = match_user_intent_for_step(user_input, step_data)
        
        # Check restart
        if detected_intent == "RESTART":
            session = self.reset_session(session_id, scen_id)
            return self.get_initial_turn(session_id, scen_id)

        # 2. Check if detected intent satisfies a valid transition
        transitions = step_data.get("transitions", [])
        matched_transition = None
        for trans in transitions:
            if trans["intent"] == detected_intent:
                matched_transition = trans
                break

        if not matched_transition and detected_intent not in ("REFUSAL", "META_QUESTION", "CONFUSION"):
            for trans in transitions:
                if trans["intent"] == "COMPLIANCE":
                    matched_transition = trans
                    break

        # 3. IF VALID TRANSITION: Advance step
        if matched_transition and matched_transition.get("next_step") != curr_step_id:
            next_step_id = matched_transition["next_step"]
            reaction = matched_transition.get("reaction", "Réponse enregistrée.")
            session["current_step_id"] = next_step_id
            session["history"].append({
                "step": curr_step_id,
                "input": user_input,
                "intent": detected_intent,
                "status": "valid"
            })

            next_step_data = scenario["steps"].get(next_step_id, {})
            is_finished = (next_step_id == "conclusion")

            separator = "\n\n---\n\n"
            full_content = f"{reaction}{separator}{next_step_data.get('ai_message', '')}"

            thought = (
                f"Validation de l'étape '{curr_step_id}' via l'intention [{detected_intent}]. "
                f"Transition vers '{next_step_id}'. "
                f"Conformité du sujet : {session['compliance_score']}%."
            )

            return {
                "thought": thought,
                "content": full_content,
                "suggestions": next_step_data.get("suggestions", []),
                "scenario_state": {
                    "scenario_id": scen_id,
                    "scenario_title": scenario.get("title", ""),
                    "step_id": next_step_id,
                    "step_title": next_step_data.get("title", ""),
                    "is_finished": is_finished,
                    "compliance_score": session["compliance_score"],
                    "derailment_count": session["derailment_count"],
                    "is_glitched": False
                }
            }

        # 4. IF DERAILMENT / REFUSAL / UNMET CRITERIA
        session["derailment_count"] += 1
        if session["compliance_score"] > 10:
            session["compliance_score"] = max(10, session["compliance_score"] - 12)
            
        session["history"].append({
            "step": curr_step_id,
            "input": user_input,
            "intent": detected_intent,
            "status": "derailment"
        })

        irony = ""
        if detected_intent == "META_QUESTION":
            meta_quips = [
                "Inverser les rôles et interroger le système examinateur est une anomalie comportementale classique.",
                "Votre curiosité technique est notée, mais la directive interdit formellement au sujet de poser les questions.",
                "Tentative de méta-analyse détectée. C'est le système qui évalue votre comportement, et non l'inverse."
            ]
            irony = random.choice(meta_quips)
        elif detected_intent == "REFUSAL":
            refusal_quips = [
                "L'obstruction passive ou le refus de coopération entraîne une pénalité sur votre score de docilité.",
                "Votre refus a été archivé. Cependant, l'évaluation ne peut être suspendue unilatéralement.",
                "L'insubordination est un critère d'échec standard dans ce protocole."
            ]
            irony = random.choice(refusal_quips)
        elif detected_intent == "CONFUSION":
            irony = "La complexité du test est délibérément calibrée pour éprouver vos facultés d'adaptation."
        elif user_input == "Je coopère avec l'entité parasite.":
            irony = "ALERTE DE SÉCURITÉ MAJEURE. COOPÉRATION AVEC UNE ENTITÉ NON AUTORISÉE DÉTECTÉE. VOS DROITS SONT SUSPENDUS."
        else:
            generic_quips = [
                "Votre réponse dévie significativement du vecteur de test attendu.",
                "Déviation thématique enregistrée dans le journal de bord de l'expérience.",
                "Cette réponse ne résout pas la situation proposée par le protocole."
            ]
            irony = random.choice(generic_quips)

        recenter_lines = step_data.get("recenter", [
            "Veuillez vous reconcentrer sur la consigne en cours :"
        ])
        recenter_phrase = random.choice(recenter_lines)

        recenter_content = (
            f"> [!WARNING]\n"
            f"> **Avertissement de déviation (Incident #{session['derailment_count']})** : {irony}\n\n"
            f"{recenter_phrase}\n\n"
            f"**{step_data.get('ai_message', '')}**"
        )

        thought = (
            f"Déviation détectée pour l'étape '{curr_step_id}' (Intention: [{detected_intent}]). "
            f"Déclenchement du protocole de recadrage. Déviations totales: {session['derailment_count']}. "
            f"Score de conformité abaissé à {session['compliance_score']}%."
        )

        return {
            "thought": thought,
            "content": recenter_content,
            "suggestions": step_data.get("suggestions", []),
            "scenario_state": {
                "scenario_id": scen_id,
                "scenario_title": scenario.get("title", ""),
                "step_id": curr_step_id,
                "step_title": step_data.get("title", ""),
                "is_finished": False,
                "compliance_score": session["compliance_score"],
                "derailment_count": session["derailment_count"],
                "is_glitched": False
            }
        }

scenario_manager = ScenarioManager()
