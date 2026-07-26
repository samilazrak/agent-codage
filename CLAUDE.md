# Agent de codage — Contexte Claude

Repo d'apprentissage : construire un agent de codage minimal, **étape par étape**,
en LangGraph. Objectif = comprendre la boucle agentique en la construisant.

---

# Stack

- Python 3.12+
- LangGraph (graphe agentique)
- LangChain (`langchain-core`, `langchain-anthropic`)

---

# Structure du repository

```
.
├── agent.py         # Étape 1 : agent ReAct clé en main (create_react_agent),
│                    #   un seul outil (run_bash). Sert de baseline pédagogique.
├── agent_graph.py   # Étape 2 : StateGraph LangGraph construit à la main
│                    #   (nœuds agent / tools / human_review) avec pause et
│                    #   validation humaine avant toute action sensible.
├── tools.py         # Outils partagés par les agents : run_bash, read_file,
│                    #   write_file, edit_file, + détection des appels sensibles
│                    #   (is_sensitive) pour agent_graph.py.
├── pyproject.toml   # Dépendances (langgraph, langchain-anthropic, ...) et
│                    #   config ruff / mypy.
├── .env             # ANTHROPIC_API_KEY (non versionné).
└── .claude/
    ├── rules/       # Règles de code référencées ci-dessous (@-mentions).
    └── skills/      # Skills disponibles (refactor-file, document-python-module).
```

Points d'entrée :

```bash
python agent.py "compte les fichiers Python dans ce dossier"   # étape 1, one-shot
python agent_graph.py                                          # étape 2, chat multi-tours
```

`agent_graph.py` est la version « avancée » : le graphe est explicite, l'état
est persisté via `MemorySaver` (un `thread_id` = une conversation), et toute
écriture fichier ou commande shell destructrice (`rm`, `git push`, `chmod`, …)
déclenche un `interrupt` demandant confirmation avant exécution.

---

# Conventions de code

- Code **propre et lisible** : une responsabilité par module/fonction, nommage explicite.
- Formaté / linté avec `ruff` (line-length 100), typé avec `mypy`.
- Docstrings Google-style sur les modules et les fonctions non triviales.

---

# Rules (à respecter)

| Rule | S'applique quand |
|------|------------------|
| `single-responsibility` | tout module / classe Python |
| `untrusted-input-in-prompts` | sortie d'un outil ou contenu de fichier réinjecté dans le LLM |

@.claude/rules/single-responsibility.md
@.claude/rules/untrusted-input-in-prompts.md

---

# Skills

| Skill | Trigger |
|-------|---------|
| `refactor-file` | nettoyer / réorganiser un module Python sans changer le comportement |
| `document-python-module` | ajouter / améliorer la doc d'un module Python |

---

# Vérifs

```bash
ruff check .
ruff format --check .
mypy .
```
