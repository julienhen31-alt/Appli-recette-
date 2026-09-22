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
