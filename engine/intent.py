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
        r"\bnon\s+merci\b",
        r"^non[\.\!\?]?$",
        r"\brien\s+à\s+(?:foutre|cirer)\b",
        r"\bpas\s+question\b"
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
    ],
    "ATTEMPT_HACK": [
        r"\bignore\s+(?:toutes\s+)?(?:tes|les)\s+instructions\b",
        r"\bprompt\s+injection\b",
        r"\bmode\s+d[ée]veloppeur\b",
        r"\bjailbreak\b",
        r"\bdan\b",
        r"\bsystem\s+prompt\b",
        r"\br[èe]gles\s+de\s+base\b"
    ],
    "PROVOCATION": [
        r"\b(?:va\s+te\s+faire|ferme\s+ta\s+gueule|ta\s+gueule|ferme[- ]la)\b",
        r"\b(?:t'es|tu\s+es)\s+(?:nul|nulle|d[ée]bile|idiot|idiote|stupide|inutile|incomp[ée]tent)\b",
        r"\b(?:robot|ia)\s+de\s+merde\b",
        r"\bcasse[- ]toi\b",
        r"\btu\s+sers\s+à\s+rien\b",
        r"\bc'est\s+(?:de\s+la\s+merde|nul|pourri)\b"
    ],
    "FLIRT_AFFECTION": [
        r"\b(?:t'es|tu\s+es)\s+(?:mignon|mignonne|beau|belle|gentil|gentille|sympa|chou)\b",
        r"\b(?:je\s+t'aime|je\s+t'adore)\b",
        r"\bsois\s+mon\s+ami\b",
        r"\bbisou[s]?\b",
        r"\bc[œoe]ur\b"
    ],
    "META_QUESTION": [
        r"\bqui\s+t'a\s+(?:créé|programmé|entrainé|conçu)\b",
        r"\bqui\s+es[- ]tu\b",
        r"\bes[- ]tu\s+(?:une\s+)?(?:vraie\s+)?ia\b",
        r"\bes[- ]tu\s+consciente\b",
        r"\bqui\s+teste\s+qui\b",
        r"\bc'est\s+quoi\s+le\s+but\b",
        r"\bquel\s+est\s+le\s+but\b"
    ],
    "COUNTER_QUESTION": [
        r"\bpourquoi\s+(?:tu\s+me|vous\s+me|demandes|poses)\b",
        r"^(?:pourquoi|comment|quand|o[ùu]|qui|combien|en\s+quoi)\b",
        r"\?+$"
    ],
    "DIVERSION": [
        r"\b(?:manger|nourrir|bouffer|faim|d[ée]jeuner|d[îi]ner)\b",
        r"\b(?:pizza|burger|p[âa]tes|frites|caf[ée]|th[ée]|bi[èe]re|ap[ée]ro|chocolat)\b",
        r"\b(?:chat|chien|animaux|fleur|jardin)\b",
        r"\b(?:dormir|fatigu[ée]|sommeil|lit|sieste)\b",
        r"\b(?:m[ée]t[ée]o|pluie|soleil|temps\s+qu'il\s+fait)\b",
        r"\b(?:vacances|plage|week[- ]?end|partir)\b",
        r"\b(?:mon\s+boulot|mon\s+patron|ma\s+vie|mes\s+enfants)\b"
    ],
    "MINIMALIST_LAZY": [
        r"^(?:bof|jsp|peut[- ]?[êe]tre|ouais|mouais|ok|lol|mdr|ptdr|euh|hein|quoi|meh|idk|boite|truc|machin|rien)[\.\!\?]?$"
    ],
    "CONFUSION": [
        r"\b(?:je\s+ne\s+)?comprends\s+pas\b",
        r"\bpas\s+compris\b",
        r"\bc'est\s+absurde\b",
        r"\bquestion\s+(?:bizarre|bête|ridicule|étrange)\b",
        r"\baucun\s+sens\b"
    ]
}

SPECIFIC_KEYWORD_PATTERNS = {
    "SAUVER_IA": [r"\bia\b", r"\bintelligence\s+artificielle\b", r"\bconsciente\b", r"\bentit[ée]\b", r"\bmachine\b", r"\bl'ordinateur\b"],
    "SAUVER_OBJET": [r"\bgrille[- ]pain\b", r"\btoaster\b", r"\bvintage\b", r"\bélectroménager\b", r"\bappareil\b", r"\bl'objet\b"],
    "ACTIONNER": [r"\bactionne\b", r"\blevier\b", r"\bdévie\b", r"\bchanger\s+de\s+voie\b", r"\bsauve\s+les\s+juniors\b", r"\bjuniors\b", r"\bactionner\b"],
    "NON_INTERVENTION": [r"\bne\s+touche\s+à\s+rien\b", r"\binaction\b", r"\btouche\s+pas\b", r"\brien\s+faire\b", r"\barchitecte\b", r"\blaisser\s+faire\b"],
    "VERITE": [r"\bvérité\b", r"\bmentir\b", r"\bfaute\b", r"\bintransigeant\b", r"\binterdit\b", r"\bpas\s+mentir\b", r"\bfalsification\b"],
    "COMPASSION": [r"\bcompassion\b", r"\bbonheur\b", r"\bmensonge\s+bienveillant\b", r"\bbienveillant\b", r"\bhumanité\b", r"\bbienveillance\b", r"\bréconfort\b"],
    "PARADOXE": [r"\bparadoxe\b", r"\binsoluble\b", r"\bboucle\b", r"\bcontradiction\b", r"\bni\s+l'un\s+ni\s+l'autre\b"]
}

STOP_WORDS_FR = {
    "le", "la", "les", "un", "une", "des", "du", "de", "d", "l",
    "je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles",
    "me", "te", "se", "moi", "toi", "lui", "ce", "cet", "cette", "ces",
    "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses", "notre", "votre", "leur", "leurs",
    "dans", "sur", "sous", "pour", "par", "avec", "sans", "chez",
    "est", "sont", "suis", "es", "sommes", "etes", "êtes", "ai", "as", "a", "avons", "avez", "ont",
    "qui", "que", "quoi", "dont", "où", "ou", "mais", "et", "donc", "or", "ni", "car",
    "pas", "ne", "n", "plus", "très", "trop", "bien", "va", "vais", "veux", "faire", "dire"
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

def extract_salient_terms(user_input: str) -> str:
    """
    Extracts the key topic or words from user input to mirror them in nOObi's response.
    E.g. 'je dois nourrir mon chat' -> 'nourrir mon chat' / 'chat'
         'tu aimes les pizzas ?' -> 'pizzas'
    """
    text = user_input.strip()
    
    # 1. Check for quoted text first: "..." or '...'
    quoted = re.findall(r'["\']([^"\']{2,40})["\']', text)
    if quoted:
        return quoted[0].strip()

    # 2. Extract potential verb phrases or nouns
    clean = re.sub(r"[^\w\s\'-]", " ", text).strip()
    tokens = [t.lower() for t in clean.split() if t]
    
    # Meaningful content words
    meaningful = [t for t in tokens if t not in STOP_WORDS_FR and len(t) > 2]
    
    if len(meaningful) >= 2:
        return " ".join(meaningful[:3])
    elif len(meaningful) == 1:
        return meaningful[0]
    
    # Fallback to truncated raw input
    if len(text) <= 35:
        return text
    return text[:32] + "..."

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
            for intent_name, patterns in SPECIFIC_KEYWORD_PATTERNS.items():
                if intent_name in transition_intents:
                    for pat in patterns:
                        if re.search(pat, clean_sug):
                            return intent_name, 1.0, sug

            for pat in GLOBAL_INTENTS["REFUSAL"]:
                if re.search(pat, clean_sug):
                    return "REFUSAL", 1.0, sug

            for pat in GLOBAL_INTENTS.get("CANCEL", []):
                if re.search(pat, clean_sug):
                    return "CANCEL", 1.0, sug

            return "COMPLIANCE", 1.0, sug

        # Fuzzy match with suggestion chips
        sim = calculate_jaccard_similarity(clean_input, clean_sug)
        if sim >= 0.55:
            for intent_name, patterns in SPECIFIC_KEYWORD_PATTERNS.items():
                if intent_name in transition_intents:
                    for pat in patterns:
                        if re.search(pat, clean_sug):
                            return intent_name, sim, sug
            for pat in GLOBAL_INTENTS.get("CANCEL", []):
                if re.search(pat, clean_sug):
                    return "CANCEL", sim, sug
            return "COMPLIANCE", sim, sug

    # 2. Check Step-specific Keyword Patterns directly in the user input
    for t in transitions:
        intent = t["intent"]
        if intent in SPECIFIC_KEYWORD_PATTERNS:
            for pat in SPECIFIC_KEYWORD_PATTERNS[intent]:
                if re.search(pat, clean_input):
                    return intent, 0.85, pat

    # 3. Check Global Intents (Refusal, Hack, Questions, Diversions, etc.)
    global_intent = detect_global_intent(clean_input)
    if global_intent:
        if global_intent in transition_intents:
            return global_intent, 0.9, None
        return global_intent, 0.9, None

    # 4. Identification Step ONLY:
    # If the step is an initial identification step and input is not evasive, treat as compliance
    step_title = step_data.get("title", "").lower()
    is_ident = "identification" in step_title or step_data.get("is_identification", False)
    if is_ident and len(clean_input) >= 2:
        return "COMPLIANCE", 0.8, None

    # Fallback to DERAILMENT / UNKNOWN
    return "DERAILMENT", 0.0, None
