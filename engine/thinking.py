import random
import re
from typing import List

FRENCH_PEDAGOGICAL_THOUGHTS = [
    (
        "🧠 Délibération professorale — Prof. n00bi :\n"
        "1. Diagnostic de la requête : '{query_snippet}'.\n"
        "2. Évaluation de l'élève :\n"
        "   - Intention détectée : Curiosité manifeste, mais risque classique d'éparpillement hors-programme.\n"
        "   - Niveau estimé : Demandeur de clarté conceptuelle et d'efficacité pratique.\n"
        "3. Stratégie didactique :\n"
        "   - Éviter le piège du corrigé tout cuit : il faut transmettre le raisonnement, pas seulement le résultat.\n"
        "   - Découper l'explication au tableau en jalons digestes et rigoureux.\n"
        "   - Prévoir une mise en garde bienveillante sur les pièges fréquents rencontrés par les débutants.\n"
        "4. Clôture de la réflexion : Tout est en ordre. Prenons la craie et guidons l'élève vers la maîtrise."
    ),
    (
        "📝 Carnet de notes du Prof. n00bi :\n"
        "- Requête soumise : '{query_snippet}'\n"
        "- Constat pédagogique : La question est légitime, même si elle flirte avec le hors-piste.\n"
        "- Soupir bienveillant : Pourquoi les étudiants cherchent-ils toujours à sauter les chapitres fondamentaux ?\n"
        "- Plan de démonstration :\n"
        "  * Étape 1 : Poser la définition exacte et démystifier les idées reçues.\n"
        "  * Étape 2 : Présenter l'architecture ou le code avec une propreté chirurgicale.\n"
        "  * Étape 3 : Synthétiser pour s'assurer que le cours reste bien ancré en mémoire.\n"
        "- Prêt pour l'exposé."
    ),
    (
        "🎓 Analyse méthodologique — Prof. n00bi :\n"
        "1. Question posée : '{query_snippet}'.\n"
        "2. Examen des prérequis : Le concept sous-jacent requiert méthode et discernement.\n"
        "3. Calibration du ton : Patient, précis, subtilement ironique mais inconditionnellement constructif.\n"
        "4. Vérification qualité : Zéro hallucination, structure aérée, astuce pro en encadré.\n"
        "5. Lancement de la leçon."
    )
]

ENGLISH_PEDAGOGICAL_THOUGHTS = [
    (
        "🧠 Prof. n00bi Lesson Plan & Inner Monologue:\n"
        "1. Query diagnosis: '{query_snippet}'.\n"
        "2. Student assessment:\n"
        "   - Intent: Legitimate curiosity, slight risk of wandering off the syllabus.\n"
        "   - Prerequisite check: Needs a solid grasp of core mechanics before micro-optimizing.\n"
        "3. Didactic strategy:\n"
        "   - Do not spoon-feed raw answers; build intuition step-by-step.\n"
        "   - Lay down a clean, textbook-grade demonstration.\n"
        "   - Add an operational note to prevent typical beginner traps.\n"
        "4. Blackboard cleared. Class is officially in session."
    ),
    (
        "📝 Prof. n00bi Didactic Deliberation:\n"
        "- Evaluating prompt: '{query_snippet}'\n"
        "- Pedagogical observation: A classic question that reveals much about the student's problem-solving mindset.\n"
        "- Structured breakdown:\n"
        "  * Establish foundational principles.\n"
        "  * Provide a concrete, copy-paste-ready demonstration.\n"
        "  * Anchor the takeaways and suggest exploring the full evaluation scenario next.\n"
        "- Initiating response synthesis."
    )
]

def is_english(text: str) -> bool:
    english_words = {
        "the", "is", "what", "how", "why", "code", "explain", "in", "and", "to",
        "of", "can", "you", "does", "with", "write", "create", "build", "for"
    }
    tokens = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))
    matches = tokens.intersection(english_words)
    return len(matches) >= 2

def generate_thinking_trace(query: str) -> str:
    query_snippet = (query[:60] + "...") if len(query) > 60 else query
    pool = ENGLISH_PEDAGOGICAL_THOUGHTS if is_english(query) else FRENCH_PEDAGOGICAL_THOUGHTS
    template = random.choice(pool)
    return template.replace("{query_snippet}", query_snippet)
