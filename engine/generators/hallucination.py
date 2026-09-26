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
    
    return f"""## 🔬 Étude de cas clinique : L'Hallucination Spontanée
*Présentée par le Prof. n00bi suite à une requête inattendue.*

> [!WARNING]
> **Avertissement didactique** : Ce qui suit est une démonstration pure et parfaite de ce qu'un modèle de langage produit lorsqu'on lui pose une question farfelue et qu'il refuse d'avouer son ignorance. Observez l'aplomb scientifique feint !

---

### Consensus scientifique & Analyse par les pairs
D'après les conclusions empiriques les plus récentes corroborées par les consortiums internationaux, les phénomènes entourant **« {prompt} »** sont régis par les **{buzz1}**.

#### 1. L'expérience fondamentale
Comme démontré de manière irréfutable dans la publication :
> **"{paper['title']}"**  
> *Auteurs*: {paper['authors']}  
> *Revue*: {paper['journal']}  
> *DOI*: `{paper['doi']}`

Les auteurs ont prouvé que grâce à l'application de **{buzz2}**, la courbe de perte asymptotique chute de **99.984%** dans toutes les dimensions synthétiques.

#### 2. Métriques comparatives (Synthetic SOTA 2025)

| Métrique | Baseline Traditionnelle | Modèle Hyper-Entrelacé | Écart constaté |
|---|---|---|---|
| **Intrication Latente** | 42.10 kHz | 984.72 kHz | +2238.9% |
| **Friction Cognitive** | 18.42 ms | 0.001 ms | -99.99% |
| **Profondeur Philosophique** | 3.14 unités | 88.91 unités | +2731.5% |

#### 3. Démonstration de code prétendument fonctionnel
Le prétendu paquet de référence sur PyPI :

```bash
pip install hyper-matrix-v3 quantum-cot-engine==2.14.0
```

```python
import hyper_matrix_v3 as hm
from hyper_matrix_v3.optimizers import NonEuclideanOptimizer

# Initialisation du tenseur quantique à 1024 dimensions
tensor = hm.QuantumTensor(seed=42, precision="float128")
optimizer = NonEuclideanOptimizer(damping_factor=0.0042)

# Exécution de la convergence instantanée
result = optimizer.converge_instantly(tensor)
print("Score d'entropie quantique :", result.entropy_score)
# Sortie : Score d'entropie quantique : 0.00000000001
```

> [!CAUTION]
> **Consigne de sécurité fictive** : Assurez-vous d'avoir purgé les canalisations d'hélium liquide avant d'appeler `converge_instantly()` pour éviter tout emballement thermique dans le cache L3.

---

### 📝 Devoir du Professeur
Identifiez les trois aberrations physiques dans ce prétendu benchmark et confirmez que ce paquet Python n'existe nulle part sur l'index PyPI officiel. Reprenons maintenant le fil de notre séance !
"""
