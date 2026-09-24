# 🧠 MimicLLM - Zero-GPU Modern LLM Simulator

A full-stack, standalone web application that humorously and convincingly mimics the behaviors, interface, quirks, and protocols of modern frontier Large Language Models (like **GPT-4o**, **Claude 3.7**, and **DeepSeek-R1**) without deploying any neural network weights, GPUs, or external AI APIs.

---

## 🌟 Key Features

1. **Moteur de Scénarios & Scripts d'Évaluation (Nouveau)** :
   - Fichiers de scénarios déclaratifs en **YAML** dans le dossier [`scenarios/`](file:///c:/Users/bvdose/Desktop/n00bi/scenarios).
   - L'IA teste le joueur à travers des étapes progressives (Machine à états).
   - **Puces de suggestions dynamiques (Quick Replies)** : cliquables sous chaque question de l'IA pour répondre en un clic ou répondre librement.
   - **Système de Recadrage en 2 temps ("Rubber-Banding")** : si le joueur tente une digression, un refus ou un jailbreak, l'IA produit une remarque ironique sur sa tentative d'évasion, décompte un incident, et le ramène fermement à la question active avec ses suggestions.
   - **Conclusion chaleureuse** : à la fin du protocole, l'IA remercie le joueur pour sa collaboration au perfectionnement des modèles.
2. **Procedural Chain-of-Thought ("Thinking...")**:
   - Live collapsible accordion with an animated stopwatch (*"Thought for 2.8s"*).
   - Generates introspective self-deliberation, self-correction, and planning steps before emitting the answer.
3. **Realistic Token-by-Token Streaming**:
   - Server-Sent Events (SSE) streaming with variable typing cadence (15–35ms).
   - Dynamic hesitation after punctuation (`.`, `!`, `?`, `\n\n`) to simulate "thinking pauses".
4. **Four Selectable Model Personas**:
   - ⚡ **Mimic-4o-Omni**: Balanced, eager-to-please, bulleted lists, enthusiastic tone (*"Certainly! I'd be delighted..."*).
   - 🧠 **DeepFake-R1 (Reasoning)**: Spends extensive time in `<thought>` mode with existential self-reflection.
   - 🎭 **Claude-3.9-Haiku-ish**: Ethical caveats, measured tone, high empathy, and philosophical nuance.
   - 🌀 **Hallucinate-XL**: Speaks with absolute scientific authority citing made-up research papers, fake DOIs, and fictional packages (`pip install hyper-matrix-v3`).
5. **Simulated Tool & Function Calling**:
   - Emits structured tool calls (e.g. `google_search(...)`, `weather_api(...)`), renders a live execution card in the chat, and synthesizes the findings.
6. **Deterministic Generators**:
   - **Coding Engine**: Syntax-highlighted algorithms (LRU Cache, Binary Search, FastAPI endpoints, Debounce) with complexity analysis tables and copy buttons.
   - **Math Engine**: Safely evaluates algebraic expressions using AST parsing and renders textbook-grade step-by-step proofs.
   - **Explanation Engine**: ELI5 ("Explain like I'm 5") metaphors, architectural ASCII diagrams, and trade-off tables.
   - **Markov Fallback**: Open-ended queries are handled via an n-gram Markov generator trained on technical text.
7. **OpenAI-Compatible API Gateway**:
   - Implements `/v1/chat/completions` (both streaming SSE and standard JSON response) and `/v1/models`.
8. **Simulated Hardware HUD**:
   - Live environmental tracker: *"80 GB VRAM Saved"*, *"0.000g Carbon"*, *"0 Neurons Employed"*.

---

## 🚀 Quickstart

### 1. Launch with One Click
Double-click `run.bat` or run:

```powershell
uv run uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 2. Open the Web Interface
Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000) in any web browser.

---

## 📡 OpenAI API Compatibility

You can point any OpenAI SDK client directly to MimicLLM:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="mimic-zero-gpu" # Any string works
)

response = client.chat.completions.create(
    model="mimic-4o",
    messages=[{"role": "user", "content": "Explain Docker in simple terms"}]
)

print(response.choices[0].message.content)
```

Streaming works seamlessly as well:

```python
stream = client.chat.completions.create(
    model="deepfake-r1",
    messages=[{"role": "user", "content": "Implement an LRU Cache in Python"}],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

---

## 📁 Project Structure

```
n00bi/
├── main.py                     # FastAPI server (Web UI, SSE streaming, /v1/chat/completions)
├── requirements.txt            # Minimal deps: fastapi, uvicorn, sse-starlette, pydantic
├── run.bat                     # Windows batch launcher
├── test_engine.py              # Verification & integration test suite
├── engine/
│   ├── router.py               # Intent classification & priority dispatching
│   ├── thinking.py             # Procedural CoT reasoning engine
│   ├── pacer.py                # Async token streamer with jitter & pauses
│   ├── tropes.py               # Stereotypical LLM openers, callouts, and sign-offs
│   ├── generators/
│   │   ├── coding.py           # Synthetic code snippets, docstrings, complexity tables
│   │   ├── math_engine.py      # Safe AST-based math evaluator & step breakdown
│   │   ├── explanation.py      # Technical & conceptual templates with ELI5 support
│   │   ├── hallucination.py    # Fabricated citations, fake DOIs, and confident babble
│   │   ├── markov.py           # Markov chain fallback generator for open-ended queries
│   │   └── tools.py            # Simulated web search and tool calls
│   └── data/
│       └── corpus.json         # Seed corpus for facts, Markov transitions, and fake papers
└── static/
    ├── index.html              # Modern, sleek AI chat web UI
    ├── css/
    │   └── style.css           # Custom styles, animations, glowing borders
    └── js/
        ├── app.js              # Streaming client, SSE reader, DOM updates
        └── ui.js               # Theme toggle, marked.js configuration, copy button
```
