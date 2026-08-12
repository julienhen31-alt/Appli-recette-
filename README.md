# Appli recette

Livre de recettes personnel : les recettes sont stockées dans `recipes.json`,
et un script les met en page en PDF.

## Générer le PDF

```bash
python3 scripts/build_pdf.py
```

Produit `build/mes-recettes-tiktok.pdf` (et `build/livre.html` au passage).
Le rendu passe par Chromium en mode headless ; si aucun Chromium n'est trouvé,
le HTML est quand même généré — il suffit de l'ouvrir dans un navigateur et de
faire *Imprimer → Enregistrer en PDF*.

Option `--html-seulement` pour sauter l'étape PDF.

## Format des recettes

`recipes.json` :

```json
{
  "titre": "Mes recettes TikTok",
  "sous_titre": "Collection personnelle",
  "recettes": []
}
```

Chaque recette accepte les champs suivants. Seuls `titre`, `ingredients` et
`etapes` sont obligatoires ; le reste s'affiche uniquement s'il est renseigné.

| Champ | Rôle |
|---|---|
| `titre` | Nom de la recette |
| `categorie` | Regroupement au sommaire (Entrées, Plats, Desserts…) |
| `description` | Une phrase d'accroche |
| `portions` | Ex. `"4 personnes"` |
| `temps_preparation`, `temps_cuisson`, `temps_total` | Ex. `"25 min"` |
| `difficulte` | Ex. `"Facile"` |
| `ingredients` | Liste de chaînes, ou liste de groupes (voir ci-dessous) |
| `etapes` | Liste de chaînes, numérotées automatiquement |
| `astuces` | Liste de chaînes, encadré en fin de recette |
| `auteur`, `source` | Créditent la vidéo TikTok d'origine |

Les ingrédients s'écrivent au choix à plat :

```json
"ingredients": ["1 banane bien mûre", "150 g de flocons d'avoine"]
```

ou par groupes, quand la recette a plusieurs préparations :

```json
"ingredients": [
  { "groupe": "Pour la pâte", "items": ["250 g de farine", "2 œufs"] },
  { "groupe": "Pour la garniture", "items": ["200 g de chocolat"] }
]
```

`exemple-recettes.json` contient deux recettes complètes qui illustrent les deux
formes. Pour visualiser le style sans toucher à ses propres données :

```bash
cp recipes.json recipes.sauvegarde.json
cp exemple-recettes.json recipes.json
python3 scripts/build_pdf.py
```

## Dépendances

Python 3 et Jinja2 (`pip install jinja2`).
