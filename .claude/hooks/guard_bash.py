#!/usr/bin/env python3
"""PreToolUse hook for Bash: refuse unbounded dumps BEFORE they reach the model.

This is the half of output control that actually saves tokens: once a command
has run, its output is already in the transcript. Deterministic, local, no LLM.
"""
import json
import os
import re
import shlex
import sys

SIZE_LIMIT = 256 * 1024
DUMPERS = {"cat", "bat", "less", "more", "head", "tail", "jq", "yq", "xxd", "od", "strings"}
BOUNDED = re.compile(r"\|\s*(head|tail|rg|grep|wc|sed|awk|jq|yq|sort|uniq|cut|tr|column)\b")
BOUND_FLAG = re.compile(r"(^|\s)-(n|c)\b|--lines|--bytes|--max-count")


def offenders(cmd):
    """Return files a bare dumper would splat whole, as (binary, path, kb)."""
    out = []
    for seg in re.split(r"[;&]{1,2}|\|\|", cmd):
        seg = seg.strip()
        if not seg or BOUNDED.search(seg) or BOUND_FLAG.search(seg):
            continue
        try:
            parts = shlex.split(seg)
        except ValueError:
            continue
        if not parts:
            continue
        exe = os.path.basename(parts[0])
        if exe not in DUMPERS:
            continue
        for a in parts[1:]:
            if a.startswith("-"):
                continue
            try:
                size = os.path.getsize(a)
            except OSError:
                continue
            if size > SIZE_LIMIT:
                out.append((exe, a, size // 1024))
    return out


# --- producteurs de sortie non bornee, au-dela du simple `cat` ---------------
# (motif de detection, alternative bornee). Verifie sur la commande normalisee.
UNBOUNDED = [
    (re.compile(r"^git\s+log\b(?!.*(-n\s*\d|--oneline|-\d))"),
     "git log --oneline -n 20"),
    (re.compile(r"^git\s+(diff|show)\b(?!.*(--stat|--shortstat|--name-only|--name-status))"),
     "git diff --stat   puis un diff cible sur un chemin"),
    (re.compile(r"^find\b(?!.*(-maxdepth|-name|-type\s+f\s+-newer))"),
     "fd MOTIF | head -n 50"),
    (re.compile(r"^ls\b.*-[a-zA-Z]*R"), "fd --max-depth 2 | head -n 50"),
    (re.compile(r"^tree\b(?!.*-L)"), "tree -L 2"),
    (re.compile(r"^(env|printenv)\s*$"), "env | rg -i 'MOTIF'"),
    (re.compile(r"^(docker\s+logs|journalctl|kubectl\s+logs)\b(?!.*(-n|--tail|--lines))"),
     "... --tail 100"),
    (re.compile(r"^(npm|pnpm|yarn)\s+ls\b(?!.*--depth)"), "npm ls --depth 0"),
    (re.compile(r"^pip\s+(list|freeze)\b"), "pip list | rg -i 'MOTIF'"),
]


def unbounded_cmds(cmd):
    """Return (segment, suggestion) for unbounded output producers."""
    hits = []
    for seg in re.split(r"[;&]{1,2}|\|\|", cmd):
        seg = seg.strip()
        if not seg or BOUNDED.search(seg):
            continue
        base = seg.split("|")[0].strip()
        for rx, alt in UNBOUNDED:
            if rx.search(base):
                hits.append((base, alt))
                break
    return hits


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if payload.get("tool_name") != "Bash":
        sys.exit(0)
    cmd = (payload.get("tool_input") or {}).get("command")
    if not isinstance(cmd, str) or not cmd.strip():
        sys.exit(0)

    bad = offenders(cmd)
    if not bad:
        loose = unbounded_cmds(cmd)
        if loose:
            lines = [f"  {c}\n    -> {alt}" for c, alt in loose]
            json.dump({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": (
                    "Sortie potentiellement non bornee. Borne-la:\n"
                    + "\n".join(lines)
                    + "\n\nSi le volume complet est vraiment necessaire, redirige vers "
                      "un fichier puis fouille-le avec rg."),
            }}, sys.stdout)
        sys.exit(0)

    lines = [f"  - {exe} {p} ({kb} Ko)" for exe, p, kb in bad]
    q = shlex.quote(bad[0][1])
    reason = (
        "Sortie non bornee bloquee (elle serait envoyee entiere au modele):\n"
        + "\n".join(lines)
        + "\n\nBorne la commande, par exemple:\n"
        f"  rg -n 'MOTIF' {q} | head -n 50\n"
        f"  head -n 100 {q}\n"
        f"  tail -n 100 {q}\n"
        f"  jq '.[0:5]' {q}      # si JSON\n"
        "Le resultat complet reste disponible via une redirection vers un fichier."
    )
    json.dump({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}, sys.stdout)


if __name__ == "__main__":
    main()
