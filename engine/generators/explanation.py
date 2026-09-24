import json
from pathlib import Path
from typing import Optional, Dict, Any

CORPUS_PATH = Path(__file__).parent.parent / "data" / "corpus.json"

def load_corpus() -> Dict[str, Any]:
    if CORPUS_PATH.exists():
        with open(CORPUS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

CORPUS = load_corpus()

def generate_explanation(topic: str, prompt: str) -> str:
    p_lower = prompt.lower()
    topics = CORPUS.get("topics", {})
    
    # Try finding an exact match or keyword in topics
    matched_topic_key = None
    for key, data in topics.items():
        if key in p_lower or data["title"].lower() in p_lower:
            matched_topic_key = key
            break
            
    is_eli5 = "eli5" in p_lower or "like i'm 5" in p_lower or "explain like i am 5" in p_lower or "simple terms" in p_lower

    if matched_topic_key:
        t_data = topics[matched_topic_key]
        if is_eli5:
            return f"""## {t_data['title']} (Simplified Explanation)

Imagine explaining this during storytime:

### 🧸 The Core Idea
{t_data['analogy']}

### 🔍 How it Works in Simple Words
- **What it does**: {t_data['summary']}
- **Why it matters**: Without it, things would quickly become disorganized and grind to a halt!
- **The golden rule**: {t_data['base_case']}

### 🎯 Quick Recap
Think of it like a handy superpower that solves big complicated problems by breaking them into fun, manageable bites!
"""
        else:
            return f"""## {t_data['title']}

### 1. Conceptual Overview
{t_data['summary']}

### 2. Core Pillars & Mechanics
- **Foundational Blueprint**: {t_data['base_case']}
- **Practical Analogy**: {t_data['analogy']}
- **Complexity & Scaling**: {t_data['complexity']}

### 3. Key Advantages vs Trade-offs

| Criterion | Strength | Potential Trade-off |
|---|---|---|
| **Maintainability** | High modularity and clear abstraction boundaries | Requires disciplined conventions |
| **Performance** | Predictable execution overhead | May necessitate caching for extreme scale |
| **Developer Ergonomics** | Intuitive mental model | Learning curve for junior contributors |

### 4. Implementation Guidelines
When adopting this paradigm in real-world systems:
1. Establish automated linting and static analysis to enforce consistency.
2. Monitor latency and memory allocations during load testing.
3. Document architectural decision records (ADRs) for cross-team alignment.
"""
    
    # Fallback explanation for topics not directly indexed in corpus
    clean_topic = topic.strip().capitalize() if topic else "Modern Systems Architecture"
    return f"""## Deep Dive: {clean_topic}

### 1. Executive Summary
**{clean_topic}** represents a fundamental pattern in software engineering and systems design. At its core, it establishes a predictable relationship between inputs, computational state, and downstream observability.

### 2. Architectural Blueprint
```
+------------------+         +-------------------+         +-------------------+
|   Client Query   |  ====>  | Processing Layer  |  ====>  | Persistent State  |
+------------------+         +-------------------+         +-------------------+
                                      |
                                      v
                             [Telemetry & Logging]
```

### 3. The 3 Core Pillars
1. **Separation of Concerns**: Each component encapsulates a singular responsibility, preventing tight coupling across domain boundaries.
2. **Idempotency & Predictability**: Operations yield the exact same deterministic outcome regardless of network retries or transient jitter.
3. **Observability & Resilience**: Built-in health checks and metrics allow operators to inspect system health in real-time.

### 4. Pragmatic Recommendations
- **Start Lean**: Avoid over-engineering abstractions before scaling constraints demand them.
- **Fail Gracefully**: Implement robust circuit breakers and fallback mechanisms to ensure high availability.
"""
