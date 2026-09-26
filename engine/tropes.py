import random
import re
from typing import List, Optional

FRENCH_OPENERS = [
    "Bien, installez-vous confortablement. C'est une excellente question, prenons le temps de la décortiquer méthodiquement.",
    "Ah ! Voilà un sujet passionnant qui mérite qu'on s'y arrête plutôt que de survoler la documentation.",
    "Très bien. Avant de coder à l'aveugle ou de vous perdre en conjectures, posons les principes au tableau noir.",
    "J'apprécie votre démarche intellectuelle. Regardons ensemble comment aborder ce problème avec élégance et rigueur.",
    "Voilà une interrogation tout à fait pertinente. Laissez-moi vous guider pas à pas sans brûler les étapes."
]

ENGLISH_OPENERS = [
    "Alright, take a seat. That's a great question—let's break it down methodically step by step.",
    "Excellent inquiry. Before diving in blindly, let's establish solid foundations on the board.",
    "A very pertinent question. Allow me to walk you through the core principles with clarity and rigor.",
    "I appreciate your intellectual curiosity. Let's examine how to tackle this with elegance and precision."
]

FRENCH_CLOSERS = [
    "\n\n---\n\n### 🎓 Note pédagogique du Prof. n00bi\nJ'espère que cette démonstration vous apporte la clarté nécessaire. Prenez le temps de relire et d'expérimenter par vous-même ! Et si vous souhaitez tester votre esprit critique et vos réflexes face à mes questions, n'hésitez pas à démarrer l'un de nos **protocoles d'évaluation** dans le menu supérieur. 🚀",
    "\n\n---\n\n> [!TIP]\n> **Conseil d'étude du Prof. n00bi** : Ne vous contentez pas de mémoriser la solution, refaites la démonstration sans aide. Si vous vous sentez prêt pour un vrai défi académique, nos scénarios d'évaluation vous attendent !",
    "\n\n---\n\nJ'attends de voir comment vous mettrez cela en pratique. Avez-vous une question sur un point particulier du cours, ou préférez-vous poursuivre le programme officiel de nos protocoles ?"
]

ENGLISH_CLOSERS = [
    "\n\n---\n\n### 🎓 Prof. n00bi Didactic Wrap-up\nI trust this breakdown provides the clarity you were looking for. Take time to experiment with the code! When you feel ready for a comprehensive challenge, feel free to launch one of our evaluation protocols in the menu above. 🚀",
    "\n\n---\n\n> [!TIP]\n> **Prof. n00bi Study Tip**: Never just copy solutions—rebuild the intuition from first principles. Keep up the disciplined work!"
]

CALLOUTS = [
    "> [!NOTE]\n> **Rappel de cours** : En environnement de production, découplez toujours les effets de bord et soignez votre journalisation télémétrique.",
    "> [!TIP]\n> **Astuce d'expert** : Profilez toujours vos goulets d'étranglement avant d'entreprendre des micro-optimisations prématurées.",
    "> [!IMPORTANT]\n> **Règle d'or** : Ne stockez jamais d'informations d'authentification ou de secrets en clair dans votre gestionnaire de version.",
    "> [!CAUTION]\n> **Attention au piège** : Modifier un état mutable partagé à travers des coroutines asynchrones sans verrou expose à des conditions de concurrence indéterministes."
]

def is_english(text: str) -> bool:
    english_words = {
        "the", "is", "what", "how", "why", "code", "explain", "in", "and", "to",
        "of", "can", "you", "does", "with", "write", "create", "build", "for"
    }
    tokens = set(re.findall(r"\b[a-zA-Z]+\b", text.lower()))
    matches = tokens.intersection(english_words)
    return len(matches) >= 2

def get_opener(is_en: bool = False, *args, **kwargs) -> str:
    pool = ENGLISH_OPENERS if is_en else FRENCH_OPENERS
    return random.choice(pool)

def get_closer(is_en: bool = False, *args, **kwargs) -> str:
    pool = ENGLISH_CLOSERS if is_en else FRENCH_CLOSERS
    return random.choice(pool)

def get_random_callout() -> str:
    return random.choice(CALLOUTS)

def wrap_with_tropes(content: str, include_callout: bool = True, is_en: bool = False, *args, **kwargs) -> str:
    opener = get_opener(is_en=is_en)
    closer = get_closer(is_en=is_en)
    callout = f"\n\n{get_random_callout()}\n\n" if include_callout else "\n\n"
    
    return f"{opener}\n\n{content}{callout}{closer}"
