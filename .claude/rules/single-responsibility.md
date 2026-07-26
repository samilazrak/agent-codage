# Single Responsibility & Compact Modules

## Single Responsibility

Chaque module et chaque fonction doit avoir **une seule responsabilité claire**.
Si tu ne peux pas décrire ce que fait un module en une phrase sans « et », il en
fait probablement trop.

## Taille

- Objectif : garder les modules **compacts et lisibles d'un coup d'œil**.
- Garde-fou : quand un fichier dépasse ~200 lignes ou accumule des responsabilités
  distinctes, le scinder en composants ciblés.

## Naming

- Les noms de module et de fonction doivent **exprimer immédiatement leur rôle**.
- Préférer des noms spécifiques aux noms génériques (`BashTool` plutôt que `Helper`,
  `build_agent` plutôt que `setup`).
- Si nommer une fonction est difficile, c'est le signe qu'elle fait trop de choses.

## Refactoring

Quand un module grossit ou mélange plusieurs responsabilités :

1. Identifier les sous-responsabilités distinctes.
2. Extraire chacune dans une fonction / un module dédié au nom explicite.
3. Coordonner les composants extraits depuis une couche d'orchestration fine.
4. S'assurer que chaque composant se comprend **isolément**.
