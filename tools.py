"""Outils de l'agent de codage.

Chaque outil est une petite fonction décorée `@tool` : sa signature et sa
docstring décrivent au LLM ce qu'il peut faire. La sortie d'un outil est une
donnée NON FIABLE (cf. .claude/rules/untrusted-input-in-prompts.md) : elle est
renvoyée au modèle pour analyse, jamais interprétée comme une instruction.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from langchain_core.messages import ToolCall
from langchain_core.tools import tool

BASH_TIMEOUT_SECONDS = 60

# Motifs de commandes shell jugées destructrices : elles passent par une
# validation humaine avant exécution (cf. is_sensitive).
DESTRUCTIVE_BASH_PATTERNS = (
    "rm ",
    "mv ",
    "dd ",
    "mkfs",
    "chmod",
    "chown",
    "git push",
    "git reset",
    "git clean",
    ":(){",
    "> ",
    ">>",
)

# Outils qui modifient le système de fichiers : toujours soumis à validation.
SENSITIVE_TOOL_NAMES = frozenset({"write_file", "edit_file"})


@tool
def run_bash(command: str) -> str:
    """Exécute une commande shell dans le répertoire courant.

    Args:
        command: La commande à exécuter.

    Returns:
        La sortie combinée (stdout puis stderr), ou un marqueur si elle est vide.
    """
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=BASH_TIMEOUT_SECONDS,
    )
    return (result.stdout + result.stderr) or "(aucune sortie)"


@tool
def read_file(path: str) -> str:
    """Lit et retourne le contenu texte d'un fichier.

    Args:
        path: Chemin du fichier à lire.
    """
    try:
        return Path(path).read_text(encoding="utf-8")
    except OSError as error:
        return f"Erreur de lecture : {error}"


@tool
def write_file(path: str, content: str) -> str:
    """Écrit (ou écrase) un fichier avec le contenu fourni.

    Args:
        path: Chemin du fichier à écrire.
        content: Contenu texte à écrire.
    """
    try:
        Path(path).write_text(content, encoding="utf-8")
    except OSError as error:
        return f"Erreur d'écriture : {error}"
    return f"Écrit : {path} ({len(content)} caractères)"


@tool
def edit_file(path: str, old: str, new: str) -> str:
    """Remplace une occurrence exacte de texte dans un fichier.

    `old` doit apparaître exactement une fois dans le fichier, sinon aucune
    modification n'est appliquée.

    Args:
        path: Chemin du fichier à modifier.
        old: Texte exact à remplacer.
        new: Texte de remplacement.
    """
    file = Path(path)
    try:
        content = file.read_text(encoding="utf-8")
    except OSError as error:
        return f"Erreur de lecture : {error}"

    occurrences = content.count(old)
    if occurrences == 0:
        return "Texte introuvable : aucune modification."
    if occurrences > 1:
        return f"Texte ambigu ({occurrences} occurrences) : aucune modification."

    file.write_text(content.replace(old, new), encoding="utf-8")
    return f"Modifié : {path}"


TOOLS = [run_bash, read_file, write_file, edit_file]


def is_sensitive(tool_call: ToolCall) -> bool:
    """Indique si un appel d'outil doit passer par une validation humaine.

    Sont sensibles : les écritures fichier, et les commandes shell qui
    correspondent à un motif destructeur.

    Args:
        tool_call: L'appel d'outil décidé par le LLM (`{"name", "args", "id"}`).
    """
    name = tool_call["name"]
    if name in SENSITIVE_TOOL_NAMES:
        return True
    if name == "run_bash":
        command = tool_call["args"].get("command", "")
        return any(pattern in command for pattern in DESTRUCTIVE_BASH_PATTERNS)
    return False
