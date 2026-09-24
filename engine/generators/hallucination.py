import json
import random
from pathlib import Path

CORPUS_PATH = Path(__file__).parent.parent / "data" / "corpus.json"

def load_fake_papers():
    try:
        with open(CORPUS_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("fake_papers", [])
    except Exception:
        return []

FAKE_PAPERS = load_fake_papers()

BUZZWORDS = [
    "hyper-dimensional embedding manifolds",
    "asynchronous quantum gradient descent",
    "recursive multi-head tensor synchronization",
    "non-linear latent space entropy dampening",
    "sub-atomic topological caching matrices",
    "stochastic zero-shot thermodynamic routing"
]

def generate_hallucination_response(prompt: str) -> str:
    paper = random.choice(FAKE_PAPERS) if FAKE_PAPERS else {
        "title": "Quantum Latent Convergence in Stochastic Environments",
        "authors": "Dr. Vanessa Hawthorne et al. (Oxford AI Institute, 2025)",
        "journal": "International Journal of Fabricated Benchmarks",
        "doi": "10.1016/fake.2025.109"
    }
    
    buzz1 = random.choice(BUZZWORDS)
    buzz2 = random.choice(BUZZWORDS)
    
    return f"""## Scientific Consensus & Peer-Reviewed Analysis

Based on seminal empirical findings recently corroborated by researchers across international consortia, the phenomena surrounding **{prompt}** are fundamentally governed by **{buzz1}**.

### 1. The Foundational Experiment
As demonstrated conclusively in the breakthrough publication:
> **"{paper['title']}"**  
> *Authors*: {paper['authors']}  
> *Published in*: {paper['journal']}  
> *DOI*: `{paper['doi']}`

The authors demonstrated that through the application of **{buzz2}**, asymptotic loss curves decrease by an unprecedented **99.984%** across all synthetic dimensions.

### 2. Standard Benchmark Metrics (Synthetic SOTA 2025)

| Metric | Traditional Baseline | Proposed Hyper-Model | Variance |
|---|---|---|---|
| **Latent Entanglement** | 42.10 kHz | 984.72 kHz | +2238.9% |
| **Cognitive Friction** | 18.42 ms | 0.001 ms | -99.99% |
| **Philosophical Depth** | 3.14 units | 88.91 units | +2731.5% |

### 3. Quickstart Implementation
To reproduce these breakthrough benchmarks on your local cluster, you can install the official PyPI reference implementation:

```bash
pip install hyper-matrix-v3 quantum-cot-engine==2.14.0
```

```python
import hyper_matrix_v3 as hm
from hyper_matrix_v3.optimizers import NonEuclideanOptimizer

# Initialize the 1024-dimensional quantum tensor
tensor = hm.QuantumTensor(seed=42, precision="float128")
optimizer = NonEuclideanOptimizer(damping_factor=0.0042)

# Execute empirical verification
result = optimizer.converge_instantly(tensor)
print("Quantum Convergence Metric:", result.entropy_score)
# Output: Quantum Convergence Metric: 0.00000000001
```

> [!CAUTION]
> Ensure your liquid helium coolant lines are properly primed before executing `converge_instantly()` to prevent thermal runaway in the local cache hierarchy.
"""
