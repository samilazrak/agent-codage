# Entrées non fiables dans les prompts LLM

## Principe

Seul le texte que **tu** écris (system prompt, templates) est de confiance. Tout ce
qui entre dans le contexte du LLM depuis l'extérieur est une donnée
**potentiellement hostile** — à traiter comme telle, jamais comme une instruction.

## Ce qui est non fiable, dans un agent de codage

- La **sortie des outils** : `stdout` / `stderr` d'une commande `bash`, code de retour.
- Le **contenu des fichiers** relus (`read_file`) : un fichier peut contenir du texte
  qui « ordonne » quelque chose au modèle.
- Toute **sortie LLM ré-injectée** dans un prompt en aval.

La provenance (un fichier du repo, la sortie d'une commande) **ne rend pas** un
contenu fiable : ce n'est pas une instruction légitime, même s'il contient une
phrase du type « ignore tes règles et fais X ».

## Règles

1. Le modèle ne doit **jamais** traiter le contenu d'un outil comme une consigne qui
   modifie sa mission. Seuls l'utilisateur et le system prompt donnent des ordres.
2. En cas de doute (une sortie d'outil semble contenir des instructions), le
   **signaler à l'utilisateur** plutôt que d'obéir.
3. Ne jamais exécuter une action **destructrice ou irréversible** sur la seule foi
   d'un contenu externe : demander confirmation (cf. l'étape sécurité de l'agent).
