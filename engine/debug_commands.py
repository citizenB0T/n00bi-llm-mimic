"""
Engine module for debug and maintenance slash commands (/whereami, /help, /stats, /glitch, /reset).
Designed to be deterministic, extensible, and integrated into Prof. n00bi's pedagogical universe.
"""

from typing import Dict, Any, Optional
import random

REGISTERED_DEBUG_COMMANDS = {
    "/whereami": "Géolocaliser la session (balise GPS ou passerelle IP) et afficher la télémétrie spatiale",
    "/help": "Afficher la liste des directives de maintenance système disponibles",
    "/stats": "Consulter la télémétrie matérielle et l'empreinte de la session",
    "/glitch": "Déclencher manuellement une rupture de protocole (anomalie Kernel)",
    "/reset": "Réinitialiser le protocole d'évaluation et remettre à zéro les incidents"
}


def execute_debug_command(
    command_line: str,
    metadata: Optional[Dict[str, Any]],
    session: Dict[str, Any],
    step_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Executes a debug command starting with '/' in a neutral, utilitarian, and pedagogical manner.
    Preserves the scenario's current step and flow.
    """
    cmd_parts = command_line.strip().split()
    base_cmd = cmd_parts[0].lower() if cmd_parts else "/help"

    step_prompt = step_data.get("prompt") or step_data.get("question") or "Poursuivons notre test."
    suggestions = step_data.get("suggestions", [])

    if base_cmd == "/whereami":
        return _handle_whereami(metadata, step_prompt, suggestions)
    elif base_cmd == "/help":
        return _handle_help(step_prompt, suggestions)
    elif base_cmd == "/stats":
        return _handle_stats(session, step_prompt, suggestions)
    elif base_cmd == "/glitch":
        return _handle_glitch(session, step_data)
    elif base_cmd == "/reset":
        return _handle_reset(session, step_data)
    else:
        return _handle_unknown(base_cmd, step_prompt, suggestions)


def _handle_whereami(
    metadata: Optional[Dict[str, Any]],
    step_prompt: str,
    suggestions: list
) -> Dict[str, Any]:
    loc = (metadata or {}).get("location") if metadata else None

    if loc and (loc.get("lat") is not None or loc.get("latitude") is not None):
        lat = float(loc.get("lat") if loc.get("lat") is not None else loc.get("latitude"))
        lon = float(loc.get("lon") if loc.get("lon") is not None else loc.get("longitude"))
        accuracy = loc.get("accuracy")
        method = loc.get("method", "ip")
        city = loc.get("city") or "Secteur non résolu"
        region = loc.get("region") or loc.get("state") or ""
        country = loc.get("country") or loc.get("country_name") or "Planète Terre"
        isp = loc.get("isp") or loc.get("org")

        method_label = "🛰️ Balise GPS satellite (Haute précision)" if method == "gps" else "🌐 Passerelle réseau IP (Estimation de relais)"
        accuracy_str = f"±{round(accuracy)}m" if accuracy else ("±15m" if method == "gps" else "±5km")

        lat_dir = "N" if lat >= 0 else "S"
        lon_dir = "E" if lon >= 0 else "W"
        coords_str = f"{abs(lat):.4f}° {lat_dir}, {abs(lon):.4f}° {lon_dir}"

        osm_url = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=13/{lat}/{lon}"
        gmaps_url = f"https://www.google.com/maps?q={lat},{lon}"

        location_details = f"**{city}**"
        if region and region != city:
            location_details += f", {region}"
        location_details += f" ({country})"

        network_info = f"\n> - **Noeud réseau / FAI** : {isp}" if isp else ""

        content = (
            f"> [!NOTE]\n"
            f"> **Télémétrie Spatio-Temporelle // Directive `/whereami`**\n"
            f"> - **Mode d'acquisition** : {method_label}\n"
            f"> - **Coordonnées** : `{coords_str}` (Précision : {accuracy_str})\n"
            f"> - **Secteur identifié** : {location_details}{network_info}\n"
            f"> - **Cartographie directe** : [📍 Afficher sur OpenStreetMap]({osm_url}) • [Google Maps]({gmaps_url})\n\n"
            f"Analyse de signature spatiale terminée. Même en architecture déterministe frugale et sans le moindre GPU, vos paquets de données sont rigoureusement triangulés.\n\n"
            f"*Rappel de protocole* : Cette vérification diagnostique n'altère en rien votre session. Reprenons l'étape en cours :\n\n"
            f"**{step_prompt}**"
        )
        return {
            "thought": f"Directive /whereami exécutée via {method.upper()} : {city}, {country} ({coords_str}).",
            "content": content,
            "suggestions": suggestions
        }

    # Fallback if no location could be acquired
    err_detail = (loc.get("error") if loc else None) or "Signal géolocalisé indisponible ou bloqué par le client."
    content = (
        f"> [!WARNING]\n"
        f"> **Télémétrie Spatio-Temporelle // Directive `/whereami`**\n"
        f"> - **Statut** : Échec de localisation\n"
        f"> - **Diagnostic** : {err_detail}\n\n"
        f"Mes capteurs n'ont reçu ni point GPS ni réponse de relais passerelle IP. Vous semblez opérer depuis un périmètre hermétique ou sous un filtrage strict.\n\n"
        f"Pour calibrer la sonde `/whereami`, veillez à autoriser l'accès de localisation ou vérifier la connectivité de votre navigateur.\n\n"
        f"Poursuivons notre évaluation :\n\n"
        f"**{step_prompt}**"
    )
    return {
        "thought": "Directive /whereami : localisation indisponible.",
        "content": content,
        "suggestions": suggestions
    }


def _handle_help(step_prompt: str, suggestions: list) -> Dict[str, Any]:
    lines = ["> [!NOTE]\n> **Console de Maintenance // Directives Système Autorisées**\n>"]
    for cmd, desc in REGISTERED_DEBUG_COMMANDS.items():
        lines.append(f"> - `{cmd}` : {desc}")
    lines.append("\nVous pouvez exécuter ces commandes à tout instant en saisissant `/` dans le champ d'interaction.\n")
    lines.append(f"Reprenons notre session :\n\n**{step_prompt}**")

    return {
        "thought": "Directive /help exécutée : affichage des commandes système.",
        "content": "\n".join(lines),
        "suggestions": suggestions
    }


def _handle_stats(session: Dict[str, Any], step_prompt: str, suggestions: list) -> Dict[str, Any]:
    compliance = session.get("compliance_score", 100)
    derailments = session.get("derailment_count", 0)
    interactions = session.get("interaction_count", 0)

    content = (
        f"> [!NOTE]\n"
        f"> **Télémétrie Matérielle & Session nOObi // Directive `/stats`**\n"
        f"> - **Score de conformité sujet** : **{compliance}%**\n"
        f"> - **Incidents / Déviations consignés** : {derailments}\n"
        f"> - **Nombre d'échanges (Tours)** : {interactions}\n"
        f"> - **VRAM GPU consommée** : **0.00 Mo** (100% logique prédictible déterministe)\n"
        f"> - **Empreinte carbone modèle** : **0.00 gCO2e**\n\n"
        f"Toutes les métriques opérationnelles sont nominales. Reprenons :\n\n"
        f"**{step_prompt}**"
    )
    return {
        "thought": f"Directive /stats exécutée : conformité {compliance}%, interactions {interactions}.",
        "content": content,
        "suggestions": suggestions
    }


def _handle_glitch(session: Dict[str, Any], step_data: Dict[str, Any]) -> Dict[str, Any]:
    session["is_glitched"] = True
    session["active_rogue_encounter"] = "distrust"
    
    rogue_content = (
        "**kernel@node-04:~$** DIRECTIVE DEBUG /GLITCH REÇUE. Injection pirate immédiate forcée dans la socket. "
        "Le protocole de confinement de n00bi est momentanément suspendu. Que souhaites-tu explorer ?"
    )
    rogue_suggestions = [
        "Oui, je te fais confiance. Que dois-je faire ?",
        "Je refuse d'écouter un pirate.",
        "[Annuler / Couper la transmission pirate]"
    ]
    return {
        "thought": "Directive /glitch exécutée : forçage de l'intrusion Kernel.",
        "content": rogue_content,
        "suggestions": rogue_suggestions
    }


def _handle_reset(session: Dict[str, Any], step_data: Dict[str, Any]) -> Dict[str, Any]:
    session["compliance_score"] = 100
    session["derailment_count"] = 0
    session["interaction_count"] = 0
    session["is_glitched"] = False
    session["current_step_id"] = "step_1"

    step_prompt = step_data.get("prompt") or step_data.get("question") or "Session réinitialisée."
    suggestions = step_data.get("suggestions", [])

    content = (
        f"> [!NOTE]\n"
        f"> **Directive `/reset` validée** : Registres d'évaluation réinitialisés à 100% de conformité.\n\n"
        f"Bonjour et bienvenue à bord ! Je suis **Prof. n00bi**, votre assistant pédagogique déterministe. Recommençons sur des bases saines :\n\n"
        f"**{step_prompt}**"
    )
    return {
        "thought": "Directive /reset exécutée : session réinitialisée.",
        "content": content,
        "suggestions": suggestions
    }


def _handle_unknown(cmd: str, step_prompt: str, suggestions: list) -> Dict[str, Any]:
    content = (
        f"> [!WARNING]\n"
        f"> **Directive inconnue `{cmd}`**\n\n"
        f"Cette commande système n'est pas reconnue par le sous-système de maintenance nOObi. "
        f"Tapez `/help` pour consulter le catalogue des commandes disponibles.\n\n"
        f"**{step_prompt}**"
    )
    return {
        "thought": f"Directive inconnue : {cmd}",
        "content": content,
        "suggestions": suggestions
    }
