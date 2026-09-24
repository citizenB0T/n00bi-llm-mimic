import random
from typing import List

THOUGHT_TEMPLATES = {
    "deepfake-r1": [
        "1. Deconstructing the prompt: The user is asking about '{query_snippet}'.\n"
        "2. Identifying core dimensions:\n"
        "   - Semantic intent: Seeking an in-depth, rigorous breakdown.\n"
        "   - Target audience: Software engineers / technical practitioners.\n"
        "   - Latent constraints: Must avoid oversimplification while maintaining clear logical progression.\n\n"
        "3. Brainstorming approaches:\n"
        "   - Approach A: High-level metaphorical overview followed by direct syntax.\n"
        "   - Approach B: First-principles derivation starting from underlying architecture.\n"
        "   - Wait, Approach A risks omitting critical technical nuances. Let me backtrack and prioritize Approach B.\n\n"
        "4. Fact-checking mental register:\n"
        "   - Are there common pitfalls? Yes, edge case handling and asynchronous synchronization.\n"
        "   - Let's double check time/space complexity implications to ensure rigorous accuracy.\n\n"
        "5. Structuring the response:\n"
        "   - Section 1: Foundational Architecture & Intuition\n"
        "   - Section 2: Implementation & Pragmatic Patterns\n"
        "   - Section 3: Comparative Analysis & Trade-offs\n"
        "   - Section 4: Operational Best Practices\n\n"
        "6. Sanity check: Does this directly resolve the user's inquiry? Yes. Tone is balanced, precise, and completely hallucination-resistant. Initiating synthesis.",
        
        "Thinking Process:\n\n"
        "- User query: '{query_snippet}'\n"
        "- Initial intuition: This looks like a standard question, but there's subtle depth here.\n"
        "- Let me ponder: What is the most critical insight that most developers overlook?\n"
        "- Ah, it's the trade-off between conceptual simplicity and production scalability.\n"
        "- Let's simulate potential edge cases:\n"
        "  * What if concurrency is introduced?\n"
        "  * What if memory overhead exceeds standard L1/L2 cache budgets?\n"
        "- I must make sure not to assume deprecated conventions. Let's use modern, idiomatic patterns.\n"
        "- Let's construct a clean, step-by-step exposition.\n"
        "- Formulating concise headings, clear code blocks, and practical advice.\n"
        "- All assertions verified. Proceeding to response generation."
    ],
    "mimic-4o": [
        "Analyzing user query: '{query_snippet}'...\n"
        "Intent identified: Informative & actionable assistance.\n"
        "Strategy: Deliver an enthusiastic, well-formatted response with bold keypoints and clear code/examples.\n"
        "Ready to generate output.",

        "User prompt: '{query_snippet}'\n"
        "Goal: Provide a clear, friendly, and structured answer.\n"
        "Key elements to include: Introduction, 3-4 bulleted pillars, illustrative example, polite conclusion."
    ],
    "claude-haiku": [
        "Deliberating on prompt: '{query_snippet}'\n"
        "Evaluating safety and helpfulness guidelines: Request is constructive and benign.\n"
        "Tone calibration: Thoughtful, precise, measured.\n"
        "Focus: Highlight architectural trade-offs, nuance, and maintainability without unnecessary fluff.",

        "Query: '{query_snippet}'\n"
        "Assessing technical context. Formulating a balanced explanation emphasizing best practices and design clarity."
    ],
    "hallucinate-xl": [
        "Accessing synthetic quantum knowledge base...\n"
        "Cross-referencing query: '{query_snippet}' with 4.8 million fictitious research archives...\n"
        "Identified key citation: Dr. Alistair Finch et al. (2025), 'Hyper-Dimensional Heuristics in Latent Space'.\n"
        "Synthesizing authoritative-sounding techno-babble with 100% confidence level.\n"
        "Formatting with rigorous scientific conviction."
    ]
}

def generate_thinking_trace(query: str, persona: str = "mimic-4o") -> str:
    query_snippet = (query[:60] + "...") if len(query) > 60 else query
    pool = THOUGHT_TEMPLATES.get(persona, THOUGHT_TEMPLATES["mimic-4o"])
    template = random.choice(pool)
    return template.replace("{query_snippet}", query_snippet)
