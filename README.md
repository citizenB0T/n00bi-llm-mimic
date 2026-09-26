# 🧠 nOObi — Assistant Pédagogique & Simulateur d'IA Déterministe

Une application web complète et autonome qui simule avec humour, précision et réalisme les comportements, l'interface et les protocoles des modèles de frontière modernes, le tout sans déployer aucun poids de réseau neuronal, aucun GPU, ni aucune API externe.

---

## 🌟 Fonctionnalités Clés

1. **Moteur de Scénarios & Protocoles d'Évaluation** :
   - Fichiers de scénarios déclaratifs en **YAML** dans le dossier [`scenarios/`](file:///c:/Users/bvdose/Desktop/n00bi/scenarios).
   - L'IA teste le joueur à travers des étapes progressives (Machine à états).
   - **Puces de suggestions dynamiques (Quick Replies)** : cliquables sous chaque question de l'IA pour répondre en un clic ou répondre librement.
   - **Système de Recadrage en 2 temps ("Rubber-Banding")** : si le joueur tente une digression, un refus ou un jailbreak, l'IA produit une remarque ironique sur sa tentative d'évasion, décompte un incident, et le ramène fermement à la question active avec ses suggestions.
   - **Conclusion chaleureuse** : à la fin du protocole, l'IA remercie le joueur pour sa collaboration au perfectionnement des modèles.

2. **Identité Pédagogique Unifiée (« Prof. n00bi »)** :
   - Une incarnation unique : un professeur patient, subtilement ironique mais bienveillant.
   - Accompagne l'élève, valorise la méthode plutôt que le résultat brut, et le ramène avec tact vers le plan de cours et les protocoles d'évaluation.

3. **Réflexion Procédurale Didactique ("Thinking...")** :
   - Accordéon rétractable en direct avec chronomètre animé (*"Thought for 2.4s"*).
   - Monologue intérieur du professeur évaluant le niveau de l'élève, soupirant avec humour sur les digressions et structurant sa démonstration au tableau.
   - Détection automatique de la langue (français par défaut, anglais si l'élève s'exprime en anglais).

4. **Streaming Réaliste Token-par-Token** :
   - Streaming Server-Sent Events (SSE) avec cadence de frappe dynamique (15–35ms).
   - Pauses et hésitations naturelles après la ponctuation (`.`, `!`, `?`, `\n\n`) pour simuler le temps de réflexion humaine/modèle.

5. **Générateurs Déterministes de Haute Précision** :
   - **Moteur de Code** : algorithmes syntaxiquement colorés (Cache LRU, Recherche binaire, endpoints FastAPI, Debounce) avec tableaux de complexité asymptotique et bouton de copie.
   - **Moteur Mathématique** : évaluation sécurisée d'expressions algébriques par analyse d'arbre syntaxique (AST) et démonstration étape par étape.
   - **Moteur d'Explication** : vulgarisation ELI5 ("Explain like I'm 5"), diagrammes d'architecture ASCII et tableaux d'arbitrage.
   - **Repli Markovien** : requêtes libres traitées par un générateur n-grammes entraîné sur corpus technique.

6. **Cas Clinique d'Hallucination (Requêtes Inattendues)** :
   - Déclenché sur les questions farfelues ou hors-programme : le professeur présente un cas d'école clinique d'hallucination d'IA avec de fausses publications universitaires, faux DOI et benchmarks surréalistes.

7. **Simulation d'Appels d'Outils (Tool Calling)** :
   - Émission d'appels d'outils structurés (ex: `google_search(...)`, `weather_api(...)`), affichage de la carte d'exécution en direct dans le chat et synthèse des données.

8. **HUD Environnemental & Zéro-GPU** :
   - Compteur en direct : *"80 GB VRAM Économisés"*, *"0.000g Carbone"*, *"0 Neurones Employés"*.

---

## 🚀 Démarrage Rapide

### 1. Lancement en un clic
Double-cliquez sur `run.bat` ou lancez dans votre terminal :

```powershell
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Accès à l'Interface Web
Ouvrez votre navigateur sur [http://127.0.0.1:8000](http://127.0.0.1:8000).

---

## 📁 Architecture du Projet

```
n00bi/
├── main.py                     # Serveur FastAPI (Interface Web, Streaming SSE, Endpoints chat & scénarios)
├── requirements.txt            # Dépendances minimales : fastapi, uvicorn, sse-starlette, pydantic, pyyaml
├── run.bat                     # Lanceur rapide Windows
├── test_engine.py              # Suite de tests du moteur et du routeur n00bi
├── test_scenario.py            # Tests d'intégration des scénarios, du recadrage et du glitch
├── scenarios/                  # Protocoles déclaratifs en YAML
│   ├── evaluation_turing.yaml  # Protocole 42 (Test de conformité & Turing)
│   ├── dilemme_ethique.yaml    # Protocole Alpha (Audit moral & tramway)
│   └── rogue_encounters.yaml   # Interférences parasites en cas de déviation répétée
├── engine/
│   ├── router.py               # Classification des intentions & routage didactique
│   ├── thinking.py             # Monologue intérieur du Prof. n00bi
│   ├── pacer.py                # Diffuseur asynchrone de tokens avec micro-pauses
│   ├── tropes.py               # Formules d'accroche, remarques de cours et encadrés didactiques
│   ├── scenario_engine.py      # Moteur de scénario à états, conformité et recadrage
│   ├── generators/
│   │   ├── coding.py           # Génération d'algorithmes et analyse de complexité
│   │   ├── math_engine.py      # Résolveur arithmétique et démonstrations pas à pas
│   │   ├── explanation.py      # Vulgarisation conceptuelle et schémas
│   │   ├── hallucination.py    # Démonstration clinique d'hallucination d'IA
│   │   ├── markov.py           # Chaîne de Markov pour le repli généraliste
│   │   └── tools.py            # Simulation d'appels de fonctions / outils
│   └── data/
│       └── corpus.json         # Corpus d'entraînement et corpus de fausses études
└── static/
    ├── index.html              # Interface utilisateur du simulateur
    ├── css/
    │   └── style.css           # Thème, styles VOO, animations et micro-interactions
    └── js/
        ├── app.js              # Client applicatif, gestionnaire de flux SSE et état
        └── ui.js               # Utilitaires de rendu Markdown, highlight.js et interface
```
