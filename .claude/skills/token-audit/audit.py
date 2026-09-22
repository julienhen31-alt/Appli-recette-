#!/usr/bin/env python3
"""Mesure le contexte permanent d'une installation Claude Code.

Deterministe, stdlib seule, aucun reseau. Sortie: tableau classe par cout
decroissant. Sert de baseline avant/apres toute modification de config.
"""
import json
import os
import sys

CHARS_PER_TOKEN = 3.6  # approximation francais/anglais mixte


def tok(n):
    return round(n / CHARS_PER_TOKEN)


def scan_dir(root, pattern, label, permanent):
    rows = []
    if not os.path.isdir(root):
        return rows
    for dirpath, _, files in os.walk(root):
        for f in files:
            if f != pattern:
                continue
            p = os.path.join(dirpath, f)
            try:
                txt = open(p, encoding="utf-8", errors="replace").read()
            except OSError:
                continue
            if pattern == "SKILL.md":
                # seule la description du frontmatter est permanente
                desc = ""
                if txt.startswith("---"):
                    fm = txt[3:].split("\n---", 1)[0]
                    for line in fm.splitlines():
                        if line.startswith("description:"):
                            desc = line.split(":", 1)[1].strip()
                name = os.path.basename(dirpath)
                rows.append((f"skill:{name}", len(desc), len(txt), True))
            else:
                rows.append((f"{label}:{os.path.relpath(p, root)}",
                             len(txt), len(txt), permanent))
    return rows


def main():
    home = os.path.expanduser("~")
    proj = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    rows = []
    for base, lbl in ((proj, "projet"), (home, "global")):
        f = os.path.join(base, "CLAUDE.md")
        if os.path.isfile(f):
            n = len(open(f, encoding="utf-8", errors="replace").read())
            rows.append((f"CLAUDE.md ({lbl})", n, n, True))
    for base in (os.path.join(proj, ".claude", "skills"),
                 os.path.join(home, ".claude", "skills")):
        rows += scan_dir(base, "SKILL.md", "skill", True)

    # serveurs MCP declares
    mcp = []
    for f in (os.path.join(proj, ".mcp.json"),
              os.path.join(home, ".claude.json")):
        if os.path.isfile(f):
            try:
                d = json.load(open(f, encoding="utf-8"))
                mcp += list((d.get("mcpServers") or {}).keys())
            except Exception:
                pass

    rows.sort(key=lambda r: -r[1])
    tot_perm = sum(r[1] for r in rows)

    print(f"{'Poste':38} {'Permanent':>10} {'Si charge':>10}")
    print("-" * 60)
    for name, perm, full, _ in rows:
        extra = f"{tok(full):>10}" if full != perm else f"{'':>10}"
        print(f"{name[:38]:38} {tok(perm):>10}{extra}")
    print("-" * 60)
    print(f"{'TOTAL contexte permanent mesure':38} {tok(tot_perm):>10} tokens")
    print()
    if mcp:
        print(f"Serveurs MCP declares en config: {', '.join(sorted(set(mcp)))}")
    print("NB: les connecteurs claude.ai (Vercel, Figma, Drive...) n'apparaissent")
    print("    pas ici - ils sont injectes par l'hote. Compter ~1500-2500 tokens")
    print("    par connecteur actif. Verifier avec /context.")


if __name__ == "__main__":
    main()
