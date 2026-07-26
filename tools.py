"""Outils de l'agent de codage.

Chaque outil est une petite fonction décorée `@tool` : sa signature et sa
docstring décrivent au LLM ce qu'il peut faire. Les capacités (ici) sont
séparées de la politique de sécurité (security.py) :

- les écritures et lectures fichier passent par `safe_path` (confinement) ;
- les sorties de commande et de fichier sont encadrées par `wrap_untrusted`
  (elles sont des données à analyser, jamais des instructions).
"""

from __future__ import annotations

import subprocess

from langchain_core.tools import tool

from security import safe_path, wrap_untrusted

BASH_TIMEOUT_SECONDS = 60

_PATH_REFUSED = "Accès refusé : chemin hors du dossier de travail ou fichier sensible."


@tool
def run_bash(command: str) -> str:
    """Exécute une commande shell dans le répertoire courant.

    Args:
        command: La commande à exécuter.

    Returns:
        La sortie combinée (stdout puis stderr), encadrée comme donnée non fiable.
    """
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        timeout=BASH_TIMEOUT_SECONDS,
    )
    output = (result.stdout + result.stderr) or "(aucune sortie)"
    return wrap_untrusted(output)


@tool
def read_file(path: str) -> str:
    """Lit et retourne le contenu texte d'un fichier du dossier de travail.

    Args:
        path: Chemin du fichier à lire.
    """
    resolved = safe_path(path)
    if resolved is None:
        return _PATH_REFUSED
    try:
        return wrap_untrusted(resolved.read_text(encoding="utf-8"))
    except OSError as error:
        return f"Erreur de lecture : {error}"


@tool
def write_file(path: str, content: str) -> str:
    """Écrit (ou écrase) un fichier du dossier de travail avec le contenu fourni.

    Args:
        path: Chemin du fichier à écrire.
        content: Contenu texte à écrire.
    """
    resolved = safe_path(path)
    if resolved is None:
        return _PATH_REFUSED
    try:
        resolved.write_text(content, encoding="utf-8")
    except OSError as error:
        return f"Erreur d'écriture : {error}"
    return f"Écrit : {path} ({len(content)} caractères)"


@tool
def edit_file(path: str, old: str, new: str) -> str:
    """Remplace une occurrence exacte de texte dans un fichier du dossier de travail.

    `old` doit apparaître exactement une fois dans le fichier, sinon aucune
    modification n'est appliquée.

    Args:
        path: Chemin du fichier à modifier.
        old: Texte exact à remplacer.
        new: Texte de remplacement.
    """
    resolved = safe_path(path)
    if resolved is None:
        return _PATH_REFUSED
    try:
        content = resolved.read_text(encoding="utf-8")
    except OSError as error:
        return f"Erreur de lecture : {error}"

    occurrences = content.count(old)
    if occurrences == 0:
        return "Texte introuvable : aucune modification."
    if occurrences > 1:
        return f"Texte ambigu ({occurrences} occurrences) : aucune modification."

    resolved.write_text(content.replace(old, new), encoding="utf-8")
    return f"Modifié : {path}"


TOOLS = [run_bash, read_file, write_file, edit_file]
