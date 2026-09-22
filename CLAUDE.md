# Appli-recette-

Générateur de livre de recettes : `recipes.json` + `templates/livre.html.j2` → `scripts/build_pdf.py`. PWA statique dans `docs/`.

## Méthode (économie de contexte)

- Chercher avant de lire : `rg` / `git grep` pour localiser, jamais de lecture large exploratoire.
- `fd` pour trouver un fichier ; `ast-grep` uniquement si la structure syntaxique le justifie (pas pour du texte).
- Gros JSON/YAML : `jq` / `yq` d'abord, jamais `Read` intégral.
- Git : `git status --short`, puis `git diff --stat`, puis diff ciblé sur un chemin.
- Tests : lancer le plus ciblé d'abord, élargir seulement si nécessaire.
- Pas de dump de logs : filtrer (`rg`, `head`, `tail`) avant d'afficher.
- Pas de refactoring non demandé.
- Réponse finale concise.
- `Explore` / sous-agent seulement si une recherche large doit être isolée du contexte principal.
