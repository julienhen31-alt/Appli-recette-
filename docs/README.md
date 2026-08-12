# Frigo → Recettes

App perso : ce que j'ai dans le frigo + ce qui est en promo → les recettes qui vont avec.
54 recettes issues de ma collection TikTok.

## Mettre l'app en ligne (une fois)

1. Ce dossier `docs/` est déjà à la racine du dépôt (index.html, sw.js, manifest.webmanifest, icon-192.png, icon-512.png).
2. Dépôt → **Settings → Pages** → Source : `Deploy from a branch`, branche `claude/tiktok-recipes-document-xrd66y`, dossier **`/docs`** → Save.
3. Au bout d'une minute l'app est sur `https://julienhen31-alt.github.io/Appli-recette-/`.

## L'installer sur le téléphone

Ouvrir cette adresse sur Android → menu Chrome → **Installer l'application**.
Elle s'ouvre en plein écran, sans barre de navigateur, et **fonctionne hors ligne** :
le service worker met la page en cache et les recettes sont copiées dans le stockage de l'appareil.

## En faire un vrai APK

1. Aller sur **pwabuilder.com**.
2. Coller l'URL GitHub Pages ci-dessus → Start.
3. Package for stores → **Android** → Generate.
4. Télécharger le zip : il contient l'APK signé (`app-release-signed.apk`) et la clé de signature (`signing.keystore` — à garder, elle sert pour toutes les mises à jour).
5. Sur le téléphone : autoriser « Installer des applications inconnues » pour le gestionnaire de fichiers, puis ouvrir l'APK.

## Synchro des recettes

- Écran **Synchro** → coller un jeton GitHub *fine-grained* (accès au seul dépôt `Appli-recette-`, permission **Contents : Read and write**).
- Chaque nouvelle recette est écrite dans `recettes/<nom>.json` et relue au lancement sur les autres appareils.
- Le frigo, les promos et la liste de courses restent locaux (jamais envoyés).

## Mettre à jour l'app

Regénérer `docs/index.html` depuis la source de la maquette, pousser, et incrémenter `CACHE` dans `docs/sw.js` (`frigo-recettes-v2`, etc.) pour forcer le rafraîchissement.
