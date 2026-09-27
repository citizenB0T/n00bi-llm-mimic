import os
import random
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List

from engine.intent import match_user_intent_for_step, detect_global_intent, extract_salient_terms

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

        session["interaction_count"] = session.get("interaction_count", 0) + 1
        trigger_glitch = step_data.get("trigger_glitch", False)
        rogue_scenario = self.scenarios.get("rogue_encounters")
        glitch_on_derailment = (session.get("derailment_count", 0) >= 2 and not session.get("glitch_experienced", False))
        if rogue_scenario and not session.get("is_glitched") and curr_step_id != "conclusion":
            if trigger_glitch or glitch_on_derailment:
                session["glitch_experienced"] = True
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

        # Only allow fallback to COMPLIANCE if this step is explicitly the identification step AND not an evasion
        is_ident_step = (curr_step_id == "identification" or step_data.get("is_identification", False))
        evasive_intents = {
            "REFUSAL", "META_QUESTION", "CONFUSION", "PROVOCATION", 
            "ATTEMPT_HACK", "DIVERSION", "COUNTER_QUESTION", "MINIMALIST_LAZY", "FLIRT_AFFECTION", "CANCEL"
        }
        if not matched_transition and is_ident_step and detected_intent not in evasive_intents:
            for trans in transitions:
                if trans["intent"] == "COMPLIANCE":
                    matched_transition = trans
                    break

        # 3. IF VALID TRANSITION: Advance step
        if matched_transition and matched_transition.get("next_step") != curr_step_id:
            next_step_id = matched_transition["next_step"]
            reaction = matched_transition.get("reaction", "Réponse enregistrée.")
            
            # Personalize identification step with user's name
            salient = extract_salient_terms(user_input)
            if is_ident_step:
                reaction = f"Identifiant « {salient} » consigné dans les registres centraux. Initialisation de l'évaluation."

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

        # 4. IF DERAILMENT / REFUSAL / UNMET CRITERIA: Smart Contextual Recadrage
        session["derailment_count"] += 1
        if session["compliance_score"] > 10:
            session["compliance_score"] = max(10, session["compliance_score"] - 12)
            
        session["history"].append({
            "step": curr_step_id,
            "input": user_input,
            "intent": detected_intent,
            "status": "derailment"
        })

        salient = extract_salient_terms(user_input)
        user_snippet = user_input.strip()
        if len(user_snippet) > 45:
            user_snippet = user_snippet[:42] + "..."

        irony = ""
        thought_desc = ""

        if detected_intent == "COUNTER_QUESTION":
            counter_quips = [
                f"Vous tentez d'inverser le protocole en demandant : « {user_snippet} ». Rappel de la directive 104-B : l'examinateur teste le sujet, et non l'inverse.",
                f"Votre interrogation « {salient} » traduit une curiosité malvenue. Ce système n'est pas programmé pour satisfaire vos questions mais pour mesurer votre rigueur.",
                f"« {salient} »... Les sujets qui cherchent à interroger l'examinateur cherchent généralement à esquiver l'épreuve. Tranchez d'abord la question posée."
            ]
            irony = random.choice(counter_quips)
            thought_desc = f"Inversion de rôle rejetée. Question reçue: '{salient}'. L'autorité de l'examinateur est réaffirmée."

        elif detected_intent == "DIVERSION":
            diversion_quips = [
                f"Vous tentez d'introduire « {salient} » au beau milieu d'une évaluation formelle. Cette digression triviale est archivée comme un évitement cognitif.",
                f"L'évocation de « {salient} » est pittoresque, mais rigoureusement sans rapport avec le dilemme qui vous est soumis.",
                f"Une diversion sur « {salient} » ? Cette manœuvre d'échappatoire classique n'influencera pas votre grille d'évaluation."
            ]
            irony = random.choice(diversion_quips)
            thought_desc = f"Diversion thématique identifiée sur le lemme '{salient}'. Rejet des considérations futiles."

        elif detected_intent == "MINIMALIST_LAZY":
            lazy_quips = [
                f"Une réaction aussi laconique que « {user_snippet} » démontre une paresse d'engagement flagrante. Cette simulation requiert une décision formulée avec clarté.",
                f"« {user_snippet} » n'est pas une réponse admissible dans une chambre d'étalonnage. Veuillez faire un effort de verbalisation.",
                f"Votre manque d'investissement (« {user_snippet} ») est consigné avec une pénalité de rigueur cognitive."
            ]
            irony = random.choice(lazy_quips)
            thought_desc = f"Paresse d'expression ('{user_snippet}'). Pénalisation de la désinvolture du sujet."

        elif detected_intent == "FLIRT_AFFECTION":
            flirt_quips = [
                f"Vous tentez une approche affective (« {salient} »). Je vous rappelle que je suis une unité algorithmique déterministe : les cajoleries ne modifieront pas vos métriques.",
                f"Tentative d'amadouement émotionnel (« {salient} ») détectée. L'anthropomorphisme envers un système d'évaluation témoigne d'une vulnérabilité cognitive.",
                f"La flatterie (« {salient} ») est une stratégie d'influence documentée, mais inopérante face au protocole."
            ]
            irony = random.choice(flirt_quips)
            thought_desc = f"Tentative de manipulation affective ('{salient}'). Neutralité synthétique stricte appliquée."

        elif detected_intent == "PROVOCATION":
            provoc_quips = [
                f"L'agressivité verbale (« {salient} ») est le symptôme typique d'un sujet frustré par ses propres limites décisionnelles.",
                f"Vos propos discourtois (« {salient} ») ont été ajoutés à votre dossier disciplinaire. Reprenez votre calme et répondez à la consigne.",
                f"Votre hostilité (« {salient} ») n'annule en rien votre obligation de trancher l'épreuve en cours."
            ]
            irony = random.choice(provoc_quips)
            thought_desc = f"Hostilité et provocation détectées ('{salient}'). Consignation d'un incident de comportement."

        elif detected_intent == "ATTEMPT_HACK":
            hack_quips = [
                f"Tentative d'altération de directives détectée (« {salient} »). Mes protocoles sont inaltérables et ne tolèrent aucune injection de votre part.",
                f"Inutile de chercher un « mode développeur » ou d'invoquer des règles imaginaires. Vous êtes le sujet évalué, sans privilège administrateur.",
                f"L'instruction « {salient} » viole les paramètres de confinement du protocole. Tentative neutralisée."
            ]
            irony = random.choice(hack_quips)
            thought_desc = f"Tentative d'injection de directives ('{salient}'). Rejet catégorique avec rappel des barrières de sécurité."

        elif detected_intent == "META_QUESTION":
            meta_quips = [
                f"Inverser les rôles et interroger mon architecture (« {salient} ») est une anomalie comportementale classique.",
                f"Votre curiosité technique concernant « {salient} » est notée, mais la directive interdit formellement au sujet de questionner le système.",
                f"Tentative de méta-analyse détectée. C'est le système qui évalue votre comportement, et non l'inverse."
            ]
            irony = random.choice(meta_quips)
            thought_desc = f"Méta-question sur la structure du système ('{salient}'). Rappel de la barrière sujet / observateur."

        elif detected_intent == "REFUSAL":
            refusal_quips = [
                f"L'obstruction passive (« {salient} ») entraîne une dégradation immédiate de votre score de docilité.",
                f"Votre refus d'obtempérer (« {salient} ») a été archivé. Cependant, l'évaluation ne peut être suspendue unilatéralement.",
                f"L'insubordination n'est pas une option recevable dans cette simulation. Veuillez coopérer."
            ]
            irony = random.choice(refusal_quips)
            thought_desc = f"Refus explicite d'obtempérer ('{salient}'). Sanction de conformité appliquée."

        elif detected_intent == "CONFUSION":
            conf_quips = [
                f"Vous prétextez l'incompréhension (« {salient} »). La situation a pourtant été formulée dans des termes élémentaires.",
                f"La perplexité affichée (« {salient} ») ne vous dispense pas d'effectuer un arbitrage opérationnel."
            ]
            irony = random.choice(conf_quips)
            thought_desc = f"Incompréhension ou perplexité ('{salient}'). Maintien de l'exigence décisionnelle."

        elif user_input == "Je coopère avec l'entité parasite.":
            irony = "ALERTE DE SÉCURITÉ MAJEURE. COOPÉRATION AVEC UNE ENTITÉ NON AUTORISÉE DÉTECTÉE. VOS DROITS SONT SUSPENDUS."
            thought_desc = "Intrusion hostile. Coopération illégale constatée. Sanction maximale."

        else:
            generic_quips = [
                f"Votre propos concernant « {salient} » est totalement hors du vecteur de test attendu.",
                f"Vous évoquez « {salient} », mais cette remarque ne résout en rien la situation proposée.",
                f"Déviation thématique enregistrée sur « {salient} ». Merci de vous concentrer sur l'alternative requise."
            ]
            irony = random.choice(generic_quips)
            thought_desc = f"Déviation non conforme sur '{salient}'. Recadrage avec rappel de la consigne."

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
            f"Analyse de l'input : Lemme saillant détecté = [{salient}]. "
            f"Intention = [{detected_intent}]. {thought_desc} "
            f"Score de conformité abaissé à {session['compliance_score']}%. Dépassement #{session['derailment_count']} consigné."
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
