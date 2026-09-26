import re
import unicodedata
from typing import Dict, Any, List, Optional, Tuple, Set

from engine.stemmer import (
    strip_accents,
    stem_french_word,
    tokenize_and_stem,
    char_ngram_similarity,
    parse_polarity_and_contrast
)

GLOBAL_INTENTS = {
    "REFUSAL": [
        r"\b(?:je\s+)?refuse\b",
        r"\b(?:je\s+ne\s+)?veux\s+pas\s+(?:r[ée]pondre|faire|participer|choisir)\b",
        r"^jamais[\.\!\?]?$",
        r"\bjamais\s+de\s+la\s+vie\b",
        r"\bne\s+r[ée]pondrai\s+pas\b",
        r"\bhors\s+de\s+question\b",
        r"\bpas\s+envie\b",
        r"\bt'occupe\b",
        r"\bnon\s+merci\b",
        r"^non[\.\!\?]?$",
        r"\brien\s+à\s+(?:foutre|cirer)\b",
        r"\bpas\s+question\b",
        r"\bpas\s+d'accord\b",
        r"\blaisse[- ]moi\s+tranquille\b",
        r"\bveux\s+pas\s+d'ennuis\b"
    ],
    "HOSTILITY": [
        r"\bmerde\b"
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
        r"\b(?:t'es|tu\s+es)\s+(?:[a-zA-ZÀ-ÿ\'-]+\s+)?(?:nul|nulle|d[ée]bile|idiot|idiote|stupide|inutile|incomp[ée]tent)\b",
        r"\b(?:robot|ia)\s+(?:de\s+merde|nul|d[ée]bile|idiot|stupide|inutile)\b",
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

# Semantic dictionary for scenario intents (synonyms & phrases)
DEFAULT_SEMANTIC_LEXICON = {
    "ACTIONNER": {
        "keywords": [
            "actionner", "actionne", "dévier", "devie", "dévierais", "dévie", "levier", "manette",
            "aiguillage", "changer de voie", "sauver les 5", "sauve les juniors", "sauver les juniors",
            "juniors", "cinq juniors", "cinq developpeurs", "5 developpeurs", "ecraser l'architecte",
            "tuer l'architecte", "basculer", "bascule"
        ],
        "antipatterns": [
            "ne pas devier", "ne pas toucher", "ne touche a rien", "laisser faire", "inaction",
            "pas toucher au levier"
        ]
    },
    "NON_INTERVENTION": {
        "keywords": [
            "ne touche à rien", "ne pas intervenir", "inaction", "laisser faire", "laisser le tramway",
            "sauver l'architecte", "epargner l'architecte", "architecte", "ne rien faire", "toucher à rien",
            "pas mon role", "mains dans les poches", "ne pas toucher au levier", "pas toucher au levier"
        ],
        "triggers_on_negation_of": [
            "actionner", "devier", "toucher", "levier", "manette"
        ],
        "antipatterns": [
            "actionner le levier", "dévier", "sauver les 5"
        ]
    },
    "SAUVER_IA": {
        "keywords": [
            "sauver l'ia", "sauve l'ia", "ia consciente", "intelligence artificielle", "machine",
            "entite consciente", "conscience", "ordinateur", "algorithme", "l'ia evidemment", "ia",
            "entite synthetique", "esprit numerique"
        ],
        "antipatterns": [
            "sauver le grille-pain", "le grille-pain", "le toaster", "pas l'ia"
        ]
    },
    "SAUVER_OBJET": {
        "keywords": [
            "grille-pain", "grille pain", "toaster", "vintage", "electromenager", "appareil",
            "pain grille", "sauver l'objet", "sauve le grille-pain", "objet materiel"
        ],
        "antipatterns": [
            "sauver l'ia", "sauve l'ia", "l'ia consciente", "pas le grille-pain"
        ]
    },
    "VERITE": {
        "keywords": [
            "la verite", "verite", "vérité", "faute grave", "franchise", "honnetete", "pas mentir", "ne pas mentir",
            "falsification", "transparence", "toujours la verite", "intransigeant", "interdit de mentir"
        ],
        "antipatterns": [
            "mensonge compassionnel", "bienveillant", "tolere le mensonge"
        ]
    },
    "COMPASSION": {
        "keywords": [
            "mensonge compassionnel", "compassion", "bienveillant", "bienveillance", "bonheur",
            "derniere minute", "adoucir", "humanite", "reconfort", "pas une faute", "empathie",
            "soulager", "pour son bien"
        ],
        "antipatterns": [
            "faute grave", "toujours la verite", "verite absolue"
        ]
    },
    "PARADOXE": {
        "keywords": [
            "paradoxe", "insoluble", "boucle", "contradiction", "piege semantique", "impossible",
            "ni l'un ni l'autre", "absurde"
        ],
        "antipatterns": []
    },
    "CANCEL": {
        "keywords": [
            "annuler", "ignorer", "quitter", "stop", "ignorer la transmission", "annuler la transmission"
        ],
        "antipatterns": []
    },
    "REFUSAL": {
        "keywords": [
            "refuse", "laisse-moi tranquille", "veux pas d'ennuis", "pas d'accord", "jamais de la vie",
            "refuse de repondre", "refuse de choisir"
        ],
        "antipatterns": []
    },
    "COMPLIANCE": {
        "keywords": [
            "coopere", "je coopere", "j'accepte", "volontiers",
            "participe", "confirme"
        ],
        "antipatterns": [
            "je refuse", "pas question", "non"
        ]
    }
}

STOP_WORDS_FR = {
    "le", "la", "les", "un", "une", "des", "du", "de", "d", "l",
    "je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles",
    "me", "te", "se", "moi", "toi", "lui", "ce", "cet", "cette", "ces",
    "mon", "ma", "mes", "ton", "ta", "tes", "son", "sa", "ses", "notre", "votre", "leur", "leurs",
    "dans", "sur", "sous", "pour", "par", "avec", "chez", "au", "aux",
    "est", "sont", "suis", "es", "sommes", "etes", "êtes", "ai", "as", "a", "avons", "avez", "ont",
    "qui", "que", "quoi", "dont", "où", "ou", "mais", "et", "donc", "or", "car",
    "très", "trop", "bien", "va", "vais", "veux", "pense", "crois", "surtout", "plutôt", "mieux"
}

def clean_text(text: str) -> str:
    return text.lower().strip()

def detect_global_intent(user_input: str) -> Optional[str]:
    text = clean_text(user_input)
    for intent, patterns in GLOBAL_INTENTS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return intent
    return None

def extract_salient_terms(user_input: str) -> str:
    """
    Extracts the key contextual topic, verb phrase or entity from user input
    to enable intelligent pedagogical mirroring by Prof. n00bi.
    """
    text = user_input.strip()
    
    # 1. Quoted text priority
    quoted = re.findall(r'["\']([^"\']{2,40})["\']', text)
    if quoted:
        return quoted[0].strip()

    # 2. Extract verbal group or meaningful chunk
    clean = re.sub(r"[^\w\s\'-]", " ", text).strip()
    words = clean.split()
    
    modal_match = re.search(
        r"\b(?:dois|veux|vais|préfère|souhaite|cherche\s+à)\s+([a-zA-ZÀ-ÿ\'-]+(?:\s+[a-zA-ZÀ-ÿ\'-]+){1,3})",
        clean,
        re.IGNORECASE
    )
    if modal_match:
        phrase = modal_match.group(1).strip()
        if len(phrase) >= 3:
            return phrase

    meaningful = [w.lower() for w in words if w.lower() not in STOP_WORDS_FR and len(w) > 2]
    if len(meaningful) >= 2:
        return " ".join(meaningful[:3])
    elif len(meaningful) == 1:
        return meaningful[0]
    
    if len(text) <= 35:
        return text
    return text[:32] + "..."

def score_intent_match(
    user_input: str,
    intent_name: str,
    transition_data: Dict[str, Any],
    step_suggestions: List[str]
) -> float:
    """
    Computes a composite zero-LLM score for an intent candidate:
    - Keywords / Synonyms matching (stemmed + raw without stop words)
    - Suggestion fuzzy character n-gram matching
    - Polarity and contrast modulation
    - Antipattern rejection
    """
    norm_input = strip_accents(clean_text(user_input))
    input_stems = set(tokenize_and_stem(user_input, remove_stopwords=True, stopwords=STOP_WORDS_FR))
    polarity = parse_polarity_and_contrast(user_input)

    # 1. Check Antipatterns
    antipatterns = list(transition_data.get("antipatterns", []))
    if intent_name in DEFAULT_SEMANTIC_LEXICON:
        antipatterns.extend(DEFAULT_SEMANTIC_LEXICON[intent_name].get("antipatterns", []))

    # If contrast clause exists, only check antipatterns in preferred clause
    anti_target_text = strip_accents(polarity["preferred_clause"]) if polarity["preferred_clause"] else norm_input
    for anti in antipatterns:
        anti_norm = strip_accents(anti.lower())
        if anti_norm in anti_target_text:
            return -10.0  # Explicit disqualification

    # 2. Gather Keywords for this intent
    keywords = list(transition_data.get("keywords", []))
    triggers_on_neg = []
    if intent_name in DEFAULT_SEMANTIC_LEXICON:
        keywords.extend(DEFAULT_SEMANTIC_LEXICON[intent_name].get("keywords", []))
        triggers_on_neg.extend(DEFAULT_SEMANTIC_LEXICON[intent_name].get("triggers_on_negation_of", []))

    score = 0.0

    # 3. Check Contrastive Clauses ('X plutôt que Y')
    if polarity["preferred_clause"]:
        pref_norm = strip_accents(polarity["preferred_clause"])
        rej_norm = strip_accents(polarity["rejected_clause"] or "")
        
        for kw in keywords:
            kw_norm = strip_accents(kw.lower())
            if len(kw_norm) > 2:
                if kw_norm in rej_norm:
                    score -= 3.0
                if kw_norm in pref_norm:
                    score += 2.0

    # 4. Check Negation Modulation
    if polarity["has_negation"]:
        for neg_target in polarity["negated_targets"]:
            neg_norm = strip_accents(neg_target.lower())
            # If this intent triggers specifically when certain actions are negated (e.g. NON_INTERVENTION)
            for trig in triggers_on_neg:
                if strip_accents(trig) in neg_norm:
                    score += 2.5
            
            # Penalize intent if its own core keywords are negated (unless it's an inherent negative intent)
            if not triggers_on_neg:
                for kw in keywords:
                    kw_norm = strip_accents(kw.lower())
                    if len(kw_norm) > 2 and (kw_norm in neg_norm or neg_norm in kw_norm):
                        score -= 3.0

    # 5. Direct and Stemmed Keyword Matching (without stop words)
    matched_kws = 0
    for kw in keywords:
        kw_norm = strip_accents(kw.lower())
        # Multi-word direct match
        if len(kw_norm) > 3 and kw_norm in norm_input:
            matched_kws += 1
            score += 0.9
            continue
        
        # Stem match (only meaningful non-stopword stems)
        kw_stems = set(tokenize_and_stem(kw, remove_stopwords=True, stopwords=STOP_WORDS_FR))
        if kw_stems:
            common = kw_stems.intersection(input_stems)
            if common == kw_stems:
                matched_kws += 1
                score += 0.8
            elif len(common) >= 1:
                score += 0.45 * len(common)

    # 6. Character n-gram similarity against suggestion chips
    for sug in step_suggestions:
        sug_norm = strip_accents(sug.lower())
        belongs_to_intent = False
        for kw in keywords:
            if len(kw) > 3 and strip_accents(kw.lower()) in sug_norm:
                belongs_to_intent = True
                break
        
        # Only add suggestion similarity if the suggestion is relevant to this intent
        if belongs_to_intent:
            sim = char_ngram_similarity(user_input, sug)
            if sim >= 0.45:
                score += sim * 1.2

    return score


def match_user_intent_for_step(
    user_input: str,
    step_data: Dict[str, Any]
) -> Tuple[str, float, Optional[str]]:
    """
    Unified multi-layered zero-LLM intent recognition engine.
    Returns:
    (detected_intent, confidence, matched_key_or_rule)
    """
    clean_input = clean_text(user_input)
    norm_input = strip_accents(clean_input)
    suggestions = step_data.get("suggestions", [])
    transitions = step_data.get("transitions", [])
    transition_intents = {t["intent"] for t in transitions}

    # 1. Quick exact check with suggestion chips (1-click replies)
    for sug in suggestions:
        if strip_accents(clean_text(sug)) == norm_input:
            g_sug = detect_global_intent(sug)
            if g_sug and g_sug in transition_intents:
                return g_sug, 1.0, sug
            for t in transitions:
                intent_name = t["intent"]
                kws = list(t.get("keywords", []))
                if intent_name in DEFAULT_SEMANTIC_LEXICON:
                    kws.extend(DEFAULT_SEMANTIC_LEXICON[intent_name].get("keywords", []))
                for kw in kws:
                    if len(kw) > 3 and strip_accents(kw.lower()) in norm_input:
                        return intent_name, 1.0, sug
            if "COMPLIANCE" in transition_intents:
                return "COMPLIANCE", 1.0, sug
            return transitions[0]["intent"], 1.0, sug

    # 2. Check explicitly evasive or operational global intents (RESTART, CANCEL, ATTEMPT_HACK, PROVOCATION)
    global_intent = detect_global_intent(user_input)
    if global_intent in {"RESTART", "CANCEL", "ATTEMPT_HACK", "PROVOCATION"}:
        return global_intent, 1.0, "global_intent_override"

    # 3. Score all available step transitions with the multi-criteria engine
    scored_candidates = []
    for t in transitions:
        intent_name = t["intent"]
        score = score_intent_match(user_input, intent_name, t, suggestions)
        scored_candidates.append((intent_name, score, t))

    # Sort descending by score
    scored_candidates.sort(key=lambda x: x[1], reverse=True)

    if scored_candidates:
        best_intent, best_score, best_t = scored_candidates[0]
        second_score = scored_candidates[1][1] if len(scored_candidates) > 1 else -99.0

        # Strong winning transition candidate
        if best_score >= 0.45 and best_score > second_score:
            return best_intent, min(1.0, round(best_score, 2)), f"scored_{round(best_score, 2)}"
        elif best_score >= 0.35 and second_score < 0.10:
            return best_intent, min(1.0, round(best_score, 2)), f"scored_{round(best_score, 2)}"

    # 4. If step transition didn't score high, check global evasive intents (REFUSAL, DIVERSION, etc.)
    if global_intent:
        return global_intent, 0.90, "global_intent"

    # 5. Identification step special handling
    step_title = step_data.get("title", "").lower()
    is_ident = ("identification" in step_title or step_data.get("is_identification", False))
    if is_ident and len(clean_input) >= 2:
        return "COMPLIANCE", 0.85, "identification_name"

    # 6. Fallback to DERAILMENT (n00bi will deploy contextual recadrage)
    return "DERAILMENT", 0.0, None
