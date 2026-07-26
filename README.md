# agent-codage

Un agent de codage minimal en **Python + LangGraph**, construit étape par étape
pour comprendre la boucle agentique de l'intérieur. L'agent dialogue avec un LLM
(Claude), exécute des commandes shell et lit/écrit des fichiers — avec un point de
contrôle humain avant toute action sensible.

Projet d'apprentissage : le code est volontairement compact et commenté.

## Les deux étapes

| Fichier | Ce que c'est |
|---------|--------------|
| [`agent.py`](agent.py) | **Étape 1** — un agent ReAct clé en main (`create_react_agent`) avec un seul outil (`run_bash`). Baseline pédagogique pour voir un agent fonctionner. |
| [`agent_graph.py`](agent_graph.py) | **Étape 2** — le même agent reconstruit à la main en `StateGraph`, avec les outils fichiers **et** une validation humaine (`interrupt`) avant les actions sensibles. |

Le graphe de l'étape 2 :

```
START → agent ──(pas d'outil)──────────────► END
          │
          ├─(outil sûr)──────────► tools ──► agent
          │
          └─(outil sensible)─► human_review ─(approuvé)─► tools
                                      └──────(refusé)───► agent
```

- **`agent`** interroge le LLM (réponse finale ou décision d'appeler des outils).
- **`tools`** exécute les outils demandés (`run_bash`, `read_file`, `write_file`, `edit_file`).
- **`human_review`** met le graphe en pause et demande confirmation avant toute
  écriture fichier ou commande shell destructrice (`rm`, `git push`, `chmod`, …).

L'état est persisté via un `MemorySaver` : un `thread_id` = une conversation.

## Installation

Prérequis : [`uv`](https://github.com/astral-sh/uv).

```bash
uv venv
uv pip install -e .
```

Configurer la clé API dans un fichier `.env` (non versionné) :

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

Étape 1 — one-shot :

```bash
uv run python agent.py "compte les fichiers Python dans ce dossier"
```

Étape 2 — chat multi-tours avec validation humaine :

```bash
uv run python agent_graph.py
```

Exemples à tester dans le chat :
- Action sûre → `liste les fichiers du dossier` (s'exécute directement).
- Action sensible → `crée un fichier test.txt avec "hello"` (demande `Autoriser ? [o/N]`).

## Qualité

- `ruff` (lint + format, line-length 100)
- `mypy` (typage)

```bash
uv run --with ruff ruff check .
uv run --with mypy mypy tools.py agent_graph.py agent.py
```
