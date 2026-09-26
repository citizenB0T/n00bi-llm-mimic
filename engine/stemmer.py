import re
import unicodedata
from typing import Set, List, Tuple, Optional, Dict

def strip_accents(text: str) -> str:
    """Normalize and remove accents from text: 'dévier' -> 'devier', 'grille-pain' -> 'grille-pain'."""
    nfkd = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in nfkd if not unicodedata.combining(c)).lower()

FRENCH_VERB_SUFFIXES = [
    "assions", "assiez", "eraient", "erions", "eriez", "erait", "erais",
    "aient", "èrent", "erons", "erez", "eront", "eras", "erai", "era",
    "ante", "antes", "ants", "ant", "asse", "asses", "ions", "iez",
    "ons", "ait", "ais", "ent", "ont", "ees", "ee", "es", "er", "ir", "oir",
    "re", "is", "it", "us", "ut", "e", "i", "u"
]

def stem_french_word(word: str) -> str:
    """
    Lightweight rule-based stemmer for French verbal and nominal morphology.
    Returns the root stem if length > 2.
    """
    w = strip_accents(word.lower().strip())
    if len(w) <= 3:
        return w

    # Plural to singular
    if w.endswith("aux"):
        w = w[:-3] + "al"
    elif (w.endswith("s") or w.endswith("x")) and len(w) > 4:
        w = w[:-1]

    # Verb endings
    for suffix in FRENCH_VERB_SUFFIXES:
        if w.endswith(suffix) and len(w) - len(suffix) >= 3:
            w = w[:-len(suffix)]
            break

    # Normalize double consonants at end
    if len(w) > 3 and w[-1] == w[-2] and w[-1] in "lmnpt":
        w = w[:-1]

    return w

def tokenize_and_stem(text: str, remove_stopwords: bool = False, stopwords: Optional[Set[str]] = None) -> List[str]:
    """Tokenizes text, strips punctuation, and stems all words."""
    clean = re.sub(r"[^\w\s-]", " ", text)
    # Replace hyphen with space for compound tokens if appropriate, but keep combined
    tokens = clean.split()
    stems = []
    for t in tokens:
        clean_token = t.strip("-").lower()
        if not clean_token:
            continue
        if remove_stopwords and stopwords and clean_token in stopwords:
            continue
        stems.append(stem_french_word(clean_token))
    return stems

def get_char_ngrams(text: str, n: int = 3) -> Set[str]:
    """Extract character n-grams with word boundary padding."""
    norm = f"  {strip_accents(text.strip().lower())}  "
    return {norm[i:i+n] for i in range(len(norm) - n + 1)}

def char_ngram_similarity(str1: str, str2: str, n: int = 3) -> float:
    """
    Dice coefficient over character n-grams.
    Highly tolerant to typos, morphology, and spacing ('grille-pain' vs 'grile pain').
    """
    ng1 = get_char_ngrams(str1, n)
    ng2 = get_char_ngrams(str2, n)
    if not ng1 or not ng2:
        return 0.0
    intersection = len(ng1.intersection(ng2))
    return (2.0 * intersection) / (len(ng1) + len(ng2))

def parse_polarity_and_contrast(text: str) -> Dict[str, Any]:
    """
    Identifies contrastive preferences ('X plutôt que Y', 'X au lieu de Y')
    and negative scopes ('ne pas toucher', 'jamais le levier').
    
    Returns:
    {
        "preferred_clause": Optional[str],
        "rejected_clause": Optional[str],
        "has_negation": bool,
        "negated_targets": List[str]
    }
    """
    norm = text.lower().strip()
    
    # 1. Contrastive patterns
    contrast_patterns = [
        r"^(.*?)\s+(?:plut[oô]t\s+que|au\s+lieu\s+de|et\s+pas|mais\s+pas)\s+(.*)$",
        r"^(?:je\s+pr[eé]f[eé]re\s+)(.*?)\s+(?:[aà]\s+|plut[oô]t\s+qu[e'])(.*)$"
    ]
    
    preferred = None
    rejected = None
    for cp in contrast_patterns:
        m = re.search(cp, norm)
        if m:
            preferred = m.group(1).strip()
            rejected = m.group(2).strip()
            break

    # 2. Negation patterns
    # Find verbs or phrases negated by 'ne ... pas', 'jamais', 'pas question de'
    has_negation = False
    negated_targets = []
    
    neg_regexes = [
        r"\b(?:ne\s+|n')(?:(?:pas|jamais|point|plus|aucunement)\s+)?(?:veux\s+pas\s+|vais\s+pas\s+)?(\w+(?:\s+\w+){0,3})",
        r"\b(?:pas|jamais|sans|refuse\s+de|hors\s+de\s+question\s+de)\s+(\w+(?:\s+\w+){0,3})"
    ]
    
    for nr in neg_regexes:
        matches = re.findall(nr, norm)
        if matches:
            has_negation = True
            for match in matches:
                negated_targets.append(match.strip())

    return {
        "preferred_clause": preferred,
        "rejected_clause": rejected,
        "has_negation": has_negation,
        "negated_targets": negated_targets
    }
