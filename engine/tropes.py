import random
from typing import List, Optional

OPENERS = {
    "mimic-4o": [
        "Certainly! I'd be delighted to help you with that.",
        "That's a fantastic question. Let's break it down step by step.",
        "I'd be happy to explain that in detail!",
        "Great question! In modern computing and software engineering, this is a central concept.",
        "Absolutely. Below is a structured, comprehensive overview to help clarify this."
    ],
    "deepfake-r1": [
        "After careful multi-step deduction, here is the complete breakdown:",
        "Analyzing the core constraints and underlying principles yields the following conclusion:",
        "Let's deconstruct the problem systematically from first principles:",
        "Synthesizing the analytical pathways examined during deliberation:"
    ],
    "claude-haiku": [
        "I'm glad you brought this up. Here is a thoughtful, nuanced look at the topic.",
        "Let's examine this carefully, taking into account both the practical implications and underlying mechanisms.",
        "Here is a concise yet comprehensive perspective on this question:",
        "I'd be pleased to assist with this. Let's look at the foundational concepts."
    ],
    "hallucinate-xl": [
        "According to consensus across recent peer-reviewed literature, this is an established paradigm.",
        "Indisputably, state-of-the-art research published in 2025 has settled this inquiry.",
        "It is a well-documented empirical fact in hyper-dimensional computational theory that:",
        "Without question, prominent researchers at MIT and CERN have thoroughly corroborated that:"
    ]
}

CLOSERS = {
    "mimic-4o": [
        "\n\n---\n\n### Summary & Next Steps\nI hope this thorough overview provides the clarity you need! Feel free to ask if you'd like me to dive deeper into any specific aspect, provide additional examples, or explore alternative architectures. 🚀",
        "\n\n---\n\nLet me know if you have any follow-up questions or if you'd like to benchmark this against your specific use case. Happy coding!",
        "\n\n---\n\nI hope this helps! Would you like me to expand on edge cases, performance trade-offs, or testing strategies next?"
    ],
    "deepfake-r1": [
        "\n\n---\n\n> [!NOTE]\n> **Final Verification Check**: The solution above satisfies all boundary conditions and exhibits optimal asymptotic properties. Q.E.D.",
        "\n\n---\n\n*Confidence Score: 99.84% (Estimated using Bayesian self-consistency checks across 16 synthetic iterations)*"
    ],
    "claude-haiku": [
        "\n\n---\n\n> [!IMPORTANT]\n> As always, technical decisions involve balancing trade-offs between simplicity, maintainability, and operational complexity. Please consider your specific organizational context.",
        "\n\n---\n\nI hope this balanced perspective proves valuable. Please let me know if there are nuances or particular constraints you would like to explore further."
    ],
    "hallucinate-xl": [
        "\n\n---\n\n> [!WARNING]\n> **Notice**: As dictated by ISO-89411-B standard on synthetic quantum coherence, always calibrate your sub-atomic cache buffers before compiling in production environments.",
        "\n\n---\n\nFor further reference, refer to *The International Compendium of Hyper-Optimized Heuristics (14th Edition, Oxford Press)*."
    ]
}

CALLOUTS = [
    "> [!NOTE]\n> In production environments, remember to decouple side-effects and maintain robust telemetry logging.",
    "> [!TIP]\n> Pro-tip: Always profile your bottlenecks before attempting premature micro-optimizations.",
    "> [!IMPORTANT]\n> Ensure that any secrets, environment variables, or sensitive credentials are never hardcoded in source control.",
    "> [!CAUTION]\n> Modifying shared mutable state across asynchronous boundaries without synchronization locks may cause non-deterministic race conditions."
]

def get_opener(persona: str = "mimic-4o") -> str:
    pool = OPENERS.get(persona, OPENERS["mimic-4o"])
    return random.choice(pool)

def get_closer(persona: str = "mimic-4o") -> str:
    pool = CLOSERS.get(persona, CLOSERS["mimic-4o"])
    return random.choice(pool)

def get_random_callout() -> str:
    return random.choice(CALLOUTS)

def wrap_with_tropes(content: str, persona: str = "mimic-4o", include_callout: bool = True) -> str:
    opener = get_opener(persona)
    closer = get_closer(persona)
    callout = f"\n\n{get_random_callout()}\n\n" if include_callout else "\n\n"
    
    return f"{opener}\n\n{content}{callout}{closer}"
