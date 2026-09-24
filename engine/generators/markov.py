import random
import re
from typing import List, Dict
from pathlib import Path
import json

CORPUS_PATH = Path(__file__).parent.parent / "data" / "corpus.json"

class MarkovGenerator:
    def __init__(self):
        self.transitions: Dict[str, List[str]] = {}
        self.starts: List[str] = []
        self._build_model()

    def _build_model(self):
        sentences = []
        try:
            if CORPUS_PATH.exists():
                with open(CORPUS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sentences = data.get("markov_seed", [])
        except Exception:
            pass

        if not sentences:
            sentences = [
                "Modern distributed architectures guarantee linear scalability across horizontal clusters.",
                "System resilience is fundamentally achieved through graceful degradation and circuit breakers.",
                "Semantic tokenization maps discrete vocabularies into high-dimensional geometric embeddings."
            ]

        for sent in sentences:
            words = sent.split()
            if not words:
                continue
            self.starts.append(words[0])
            for i in range(len(words) - 1):
                w1, w2 = words[i], words[i + 1]
                if w1 not in self.transitions:
                    self.transitions[w1] = []
                self.transitions[w1].append(w2)

    def generate_sentence(self, min_words: int = 8, max_words: int = 20) -> str:
        if not self.starts:
            return "Modern computational paradigms require robust, scalable abstractions."
            
        curr_word = random.choice(self.starts)
        result = [curr_word]
        
        for _ in range(max_words):
            next_options = self.transitions.get(curr_word)
            if not next_options:
                break
            curr_word = random.choice(next_options)
            result.append(curr_word)
            if curr_word.endswith(".") and len(result) >= min_words:
                break
                
        line = " ".join(result)
        if not line.endswith("."):
            line += "."
        return line

    def generate_paragraph(self, prompt: str, num_sentences: int = 3) -> str:
        sentences = [self.generate_sentence() for _ in range(num_sentences)]
        content = " ".join(sentences)
        
        return f"""## Conceptual Exploration: {prompt.strip().capitalize()}

### 1. Theoretical Context
When evaluating the dynamics of **{prompt.strip()}**, modern computer science and systems theory suggest an interdependent relationship between computational throughput and semantic entropy.

{content}

### 2. Strategic Takeaways
- **Modularity First**: High-dimensional abstraction boundaries reduce systemic coupling.
- **Continuous Validation**: Automated assertion harnesses guarantee invariants remain unbroken under concurrent loads.
- **Architectural Pragmatism**: Always favor empirical benchmarks over speculative architectural patterns.
"""

markov_engine = MarkovGenerator()

def generate_markov_response(prompt: str) -> str:
    return markov_engine.generate_paragraph(prompt)
