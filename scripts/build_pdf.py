#!/usr/bin/env python3
"""Génère le livre de recettes en PDF à partir de recipes.json.

Usage: python3 scripts/build_pdf.py [--html-seulement]
"""

import argparse
import glob
import json
import os
import shutil
import subprocess
import sys
from collections import OrderedDict

from jinja2 import Environment, FileSystemLoader

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE = os.path.join(RACINE, "recipes.json")
SORTIE_HTML = os.path.join(RACINE, "build", "livre.html")
SORTIE_PDF = os.path.join(RACINE, "build", "mes-recettes-tiktok.pdf")


def trouver_chromium():
    """Localise un binaire Chromium utilisable pour l'impression PDF."""
    for nom in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        chemin = shutil.which(nom)
        if chemin:
            return chemin
    motifs = (
        "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
        "/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell",
    )
    for motif in motifs:
        trouves = sorted(glob.glob(motif))
        if trouves:
            return trouves[-1]
    return None


def normaliser_ingredients(brut):
    """Accepte une liste plate de chaînes ou une liste de groupes {groupe, items}.

    Renvoie toujours des blocs, pour que le gabarit n'ait qu'un seul cas à gérer.
    """
    if not brut:
        return []
    if isinstance(brut[0], dict):
        return [
            {"groupe": bloc.get("groupe"), "items": bloc.get("items", [])}
            for bloc in brut
        ]
    return [{"groupe": None, "items": brut}]


def grouper_par_categorie(recettes):
    groupes = OrderedDict()
    for r in recettes:
        groupes.setdefault(r.get("categorie") or "Autres", []).append(r)
    return list(groupes.items())


def main():
    parseur = argparse.ArgumentParser()
    parseur.add_argument(
        "--html-seulement",
        action="store_true",
        help="génère seulement le HTML, sans passer par Chromium",
    )
    args = parseur.parse_args()

    with open(SOURCE, encoding="utf-8") as f:
        donnees = json.load(f)

    recettes = donnees.get("recettes", [])
    if not recettes:
        print("Aucune recette dans recipes.json — rien à générer.", file=sys.stderr)
        return 1

    for r in recettes:
        r["ingredients_blocs"] = normaliser_ingredients(r.get("ingredients"))

    env = Environment(
        loader=FileSystemLoader(os.path.join(RACINE, "templates")),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    html = env.get_template("livre.html.j2").render(
        titre=donnees.get("titre", "Mes recettes"),
        sous_titre=donnees.get("sous_titre"),
        recettes=recettes,
        par_categorie=grouper_par_categorie(recettes),
    )

    os.makedirs(os.path.dirname(SORTIE_HTML), exist_ok=True)
    with open(SORTIE_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML  → {SORTIE_HTML}")

    if args.html_seulement:
        return 0

    chrome = trouver_chromium()
    if not chrome:
        print(
            "Chromium introuvable : le HTML est généré, mais pas le PDF.\n"
            "Ouvre build/livre.html dans un navigateur puis Imprimer → PDF.",
            file=sys.stderr,
        )
        return 1

    subprocess.run(
        [
            chrome,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={SORTIE_PDF}",
            SORTIE_HTML,
        ],
        check=True,
        capture_output=True,
    )
    taille = os.path.getsize(SORTIE_PDF) // 1024
    print(f"PDF   → {SORTIE_PDF} ({len(recettes)} recettes, {taille} Ko)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
