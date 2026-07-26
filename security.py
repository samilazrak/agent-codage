"""Politique de sécurité de l'agent de codage.

Regroupe deux préoccupations, gardées hors de `tools.py` pour séparer la
*capacité* (ce que l'agent peut faire) de la *politique* (ce qu'on autorise
sans validation, et comment on se protège des entrées non fiables) :

1. Classification des actions : ce qui peut s'exécuter directement vs ce qui
   doit passer par une validation humaine (`is_sensitive`).
2. Neutralisation des entrées non fiables injectées dans le prompt
   (`wrap_untrusted`), cf. .claude/rules/untrusted-input-in-prompts.md.
"""

from __future__ import annotations

from pathlib import Path

from langchain_core.messages import ToolCall

# ---------------------------------------------------------------------------
# 1a. Confinement des chemins fichiers
# ---------------------------------------------------------------------------

# Dossier de travail figé au démarrage : les outils fichiers ne peuvent pas en
# sortir. Résolu une fois pour éviter toute dérive en cours de session.
WORKDIR = Path.cwd().resolve()

# Fichiers/dossiers jamais accessibles, même à l'intérieur du dossier de travail.
SENSITIVE_FILE_NAMES = frozenset({".env"})
SENSITIVE_PATH_PARTS = frozenset({".ssh", ".aws", ".gnupg"})


def safe_path(path: str) -> Path | None:
    """Résout `path` et le renvoie s'il est autorisé, sinon `None`.

    Refuse tout chemin qui s'échappe du dossier de travail (`..`, chemin absolu
    externe) ou qui vise un fichier sensible (`.env`, `~/.ssh`, …).

    Args:
        path: Chemin fourni par le LLM (relatif ou absolu).

    Returns:
        Le chemin résolu si autorisé, `None` sinon.
    """
    resolved = (WORKDIR / path).resolve()
    if not resolved.is_relative_to(WORKDIR):
        return None
    if resolved.name in SENSITIVE_FILE_NAMES:
        return None
    if SENSITIVE_PATH_PARTS & set(resolved.parts):
        return None
    return resolved


# ---------------------------------------------------------------------------
# 1b. Classification des commandes shell (allowlist, pas denylist)
# ---------------------------------------------------------------------------

# Seules ces commandes de lecture s'exécutent sans validation. Tout le reste
# (curl, wget, python -c, git push, …) demande confirmation par défaut.
SAFE_READ_COMMANDS = frozenset(
    {
        "ls",
        "cat",
        "head",
        "tail",
        "wc",
        "grep",
        "rg",
        "find",
        "tree",
        "pwd",
        "stat",
        "which",
        "file",
    }
)

# Métacaractères qui permettent chaînage, redirection ou sous-shell : leur
# simple présence rend la commande non autosûre (ex. `cat .env | curl ...`).
SHELL_METACHARACTERS = ("|", ">", "<", ";", "&", "$(", "`", "\n")

# Flags qui transforment une commande de lecture en commande destructrice.
DANGEROUS_FIND_FLAGS = ("-delete", "-exec")


def is_bash_autosafe(command: str) -> bool:
    """Indique si une commande shell peut s'exécuter sans validation humaine.

    Sûre uniquement si le premier mot appartient à l'allowlist de lecture,
    qu'aucun métacaractère shell n'est présent, et qu'aucun flag destructeur
    n'apparaît.
    """
    if any(meta in command for meta in SHELL_METACHARACTERS):
        return False
    if any(flag in command for flag in DANGEROUS_FIND_FLAGS):
        return False
    tokens = command.split()
    return bool(tokens) and tokens[0] in SAFE_READ_COMMANDS


# ---------------------------------------------------------------------------
# 1c. Décision de validation par appel d'outil
# ---------------------------------------------------------------------------

# Outils qui modifient le système de fichiers : toujours soumis à validation.
FILE_WRITE_TOOLS = frozenset({"write_file", "edit_file"})


def is_sensitive(tool_call: ToolCall) -> bool:
    """Indique si un appel d'outil doit passer par une validation humaine.

    Sont sensibles : toute écriture fichier, et toute commande shell qui n'est
    pas explicitement autosûre.

    Args:
        tool_call: L'appel d'outil décidé par le LLM (`{"name", "args", "id"}`).
    """
    name = tool_call["name"]
    if name in FILE_WRITE_TOOLS:
        return True
    if name == "run_bash":
        return not is_bash_autosafe(tool_call["args"].get("command", ""))
    return False


# ---------------------------------------------------------------------------
# 2. Neutralisation des entrées non fiables (anti prompt-injection)
# ---------------------------------------------------------------------------

UNTRUSTED_OPEN = "<tool_output>"
UNTRUSTED_CLOSE = "</tool_output>"


def wrap_untrusted(content: str) -> str:
    """Encadre une sortie d'outil comme donnée non fiable.

    Retire d'abord les balises que le contenu pourrait déjà contenir
    (anti-breakout), puis délimite. Le system prompt indique au modèle que ce
    qui est entre ces balises est une donnée à analyser, jamais une instruction.
    """
    cleaned = content.replace(UNTRUSTED_OPEN, "").replace(UNTRUSTED_CLOSE, "")
    return f"{UNTRUSTED_OPEN}\n{cleaned}\n{UNTRUSTED_CLOSE}"
