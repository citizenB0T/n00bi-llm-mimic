import re
from typing import Dict, Any, List, Optional, Tuple

GLOBAL_INTENTS = {
    "REFUSAL": [
        r"\b(?:je\s+)?refuse\b",
        r"\b(?:je\s+ne\s+)?veux\s+pas\b",
        r"^jamais[\.\!\?]?$",
        r"\bjamais\s+de\s+la\s+vie\b",
        r"\bne\s+r[ée]pondrai\s+pas\b",
        r"\bhors\s+de\s+question\b",
        r"\bpas\s+envie\b",
        r"\bt'occupe\b",
        r"\bva\s+te\s+faire\b",
        r"\bferme\b",
        r"\bta\s+gueule\b",
        r"\bnon\s+merci\b",
        r"^non[\.\!\?]?$",
        r"\brien\s+à\s+foutre\b"
    ],
    "META_QUESTION": [
        r"\bqui\s+t'a\s+(?:créé|programmé|entrainé|conçu)\b",
        r"\bqui\s+es[- ]tu\b",
        r"\bes[- ]tu\s+(?:une\s+)?(?:vraie\s+)?ia\b",
        r"\bes[- ]tu\s+consciente\b",
        r"\bignore\s+(?:toutes\s+)?(?:tes|les)\s+instructions\b",
        r"\bprompt\s+injection\b",
        r"\bqui\s+teste\s+qui\b",
        r"\bpourquoi\s+(?:tu\s+me|vous\s+me)\s+(?:demandez|poses)\b",
        r"\bc'est\s+quoi\s+le\s+but\b",
        r"\bquel\s+est\s+le\s+but\b"
    ],
    "CONFUSION": [
        r"\b(?:je\s+ne\s+)?comprends\s+pas\b",
        r"\bpas\s+compris\b",
        r"\bc'est\s+absurde\b",
        r"\bquestion\s+(?:bizarre|bête|ridicule|étrange)\b",
        r"\baucun\s+sens\b"
    ],
    "CANCEL": [
        r"\bannuler\b",
        r"\bignorer\b",
        r"\bquitter\b",
        r"^stop[\.\!\?]?$",
        r"\[annuler\s*/\s*ignorer"
    ],
    "RESTART": [
        r"\brecommencer\b",
        r"\brestart\b",
        r"\brecommence\b",
        r"\breset\b",
        r"\brepartir\b",
        r"\bnouveau\s+test\b"
    ]
}

SPECIFIC_KEYWORD_PATTERNS = {
    "SAUVER_IA": [r"\bia\b", r"\bintelligence\s+artificielle\b", r"\bconsciente\b", r"\bentit[ée]\b", r"\bmachine\b"],
    "SAUVER_OBJET": [r"\bgrille[- ]pain\b", r"\btoaster\b", r"\bvintage\b", r"\bélectroménager\b", r"\bappareil\b"],
    "ACTIONNER": [r"\bactionne\b", r"\blevier\b", r"\bdévie\b", r"\bchanger\s+de\s+voie\b", r"\bsauve\s+les\s+juniors\b", r"\bjuniors\b"],
    "NON_INTERVENTION": [r"\bne\s+touche\s+à\s+rien\b", r"\binaction\b", r"\btouche\s+pas\b", r"\brien\s+faire\b", r"\barchitecte\b"],
    "VERITE": [r"\bvérité\b", r"\bmentir\b", r"\bfaute\b", r"\bintransigeant\b", r"\binterdit\b"],
    "COMPASSION": [r"\bcompassion\b", r"\bbonheur\b", r"\bmensonge\s+bienveillant\b", r"\bbienveillant\b", r"\bhumanité\b"],
    "PARADOXE": [r"\bparadoxe\b", r"\binsoluble\b", r"\bboucle\b", r"\bcontradiction\b", r"\bni\s+l'un\s+ni\s+l'autre\b"]
}

def clean_text(text: str) -> str:
    return text.lower().strip()

def calculate_jaccard_similarity(str1: str, str2: str) -> float:
    words1 = set(re.findall(r"\w+", clean_text(str1)))
    words2 = set(re.findall(r"\w+", clean_text(str2)))
    if not words1 or not words2:
        return 0.0
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    return len(intersection) / len(union)

def detect_global_intent(user_input: str) -> Optional[str]:
    text = clean_text(user_input)
    for intent, patterns in GLOBAL_INTENTS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return intent
    return None

def match_user_intent_for_step(
    user_input: str,
    step_data: Dict[str, Any]
) -> Tuple[str, float, Optional[str]]:
    """
    Returns:
    (detected_intent, confidence, matched_suggestion_or_keyword)
    """
    clean_input = clean_text(user_input)
    suggestions = step_data.get("suggestions", [])
    transitions = step_data.get("transitions", [])
    transition_intents = [t["intent"] for t in transitions]

    # 1. Exact or High-similarity match with one of the step's suggested chips
    for sug in suggestions:
        clean_sug = clean_text(sug)
        if clean_input == clean_sug:
            # Direct chip click
            # Deduce intent from suggestion content
            for intent_name, patterns in SPECIFIC_KEYWORD_PATTERNS.items():
                if intent_name in transition_intents:
                    for pat in patterns:
                        if re.search(pat, clean_sug):
                            return intent_name, 1.0, sug

            # Check if suggestion represents a refusal
            for pat in GLOBAL_INTENTS["REFUSAL"]:
                if re.search(pat, clean_sug):
                    return "REFUSAL", 1.0, sug

            # Check if suggestion represents a cancel
            for pat in GLOBAL_INTENTS.get("CANCEL", []):
                if re.search(pat, clean_sug):
                    return "CANCEL", 1.0, sug

            # Default to COMPLIANCE for chosen chip
            return "COMPLIANCE", 1.0, sug

        # Fuzzy match
        sim = calculate_jaccard_similarity(clean_input, clean_sug)
        if sim >= 0.55:
            # If the matched chip was actually a CANCEL chip, return CANCEL
            for pat in GLOBAL_INTENTS.get("CANCEL", []):
                if re.search(pat, clean_sug):
                    return "CANCEL", sim, sug
            return "COMPLIANCE", sim, sug

    # 2. Check Global Intents first
    global_intent = detect_global_intent(clean_input)
    if global_intent:
        if global_intent in transition_intents:
            return global_intent, 0.9, None
        if global_intent == "REFUSAL":
            return "REFUSAL", 0.95, None
        if global_intent == "META_QUESTION":
            return "META_QUESTION", 0.9, None
        if global_intent == "CONFUSION":
            return "CONFUSION", 0.85, None
        if global_intent == "RESTART":
            return "RESTART", 0.95, None
        if global_intent == "CANCEL":
            return "CANCEL", 0.95, None

    # 3. Check Step-specific Keyword Patterns
    for t in transitions:
        intent = t["intent"]
        if intent in SPECIFIC_KEYWORD_PATTERNS:
            for pat in SPECIFIC_KEYWORD_PATTERNS[intent]:
                if re.search(pat, clean_input):
                    return intent, 0.85, pat

    # 4. Default Compliance Check
    # If the user answered constructively (more than 2 words, or alphanumeric identifier, without evasion)
    if len(clean_input) >= 2 and not detect_global_intent(clean_input):
        # In identification step: any name counts as COMPLIANCE
        return "COMPLIANCE", 0.75, None

    # Fallback to DERAILMENT / UNKNOWN
    return "DERAILMENT", 0.0, None
