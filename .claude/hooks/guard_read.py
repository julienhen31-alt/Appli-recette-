#!/usr/bin/env python3
"""PreToolUse hook for Read: block unbounded reads of very large files.

Deterministic, local, no network, no LLM. Reads the hook payload on stdin and
emits a PreToolUse hookSpecificOutput decision on stdout.

Policy:
  - Partial reads (an explicit `limit` <= MAX_LIMIT) are always allowed.
  - Files at or below SIZE_LIMIT are always allowed.
  - Media / notebook formats are always allowed (Read renders them natively).
  - Anything else is denied with a type-specific alternative command.
"""
import json
import os
import sys

SIZE_LIMIT = 256 * 1024   # bytes: below this, a whole-file read is cheap
MAX_LIMIT = 2000          # lines: a partial read at or under this is reasonable
PASSTHROUGH = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".svg",
               ".pdf", ".ipynb"}


def advise(path, ext, size_kb):
    """Return a deterministic, type-appropriate alternative command."""
    q = json.dumps(path)
    if ext == ".json":
        return (f"jq 'keys' {q}            # structure\n"
                f"jq '.[0:5]' {q}          # echantillon\n"
                f"jq -r '.. | strings' {q} | rg -n 'MOTIF'")
    if ext in (".yaml", ".yml"):
        return (f"yq '.' {q} | head -n 100\n"
                f"rg -n 'MOTIF' {q}")
    if ext in (".csv", ".tsv"):
        return (f"head -n 20 {q}           # en-tete + debut\n"
                f"wc -l {q}                # volume\n"
                f"rg -n 'MOTIF' {q} | head -n 50")
    if ext in (".log", ".txt", ".out"):
        return (f"rg -n 'error|warn|fail' {q} | head -n 50\n"
                f"tail -n 100 {q}")
    if ext in (".lock", ".min.js", ".map"):
        return f"rg -n 'MOTIF' {q} | head -n 50   # fichier genere: ne pas lire en entier"
    return (f"rg -n 'MOTIF' {q}                    # localiser d'abord\n"
            f"sed -n '1,200p' {q}                  # equivalent Read offset/limit\n"
            f"Read({path!r}, offset=N, limit=200)  # lecture partielle ciblee")


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # never break the session on a malformed payload

    if payload.get("tool_name") != "Read":
        sys.exit(0)

    ti = payload.get("tool_input") or {}
    path = ti.get("file_path")
    if not isinstance(path, str) or not path:
        sys.exit(0)

    limit = ti.get("limit")
    if isinstance(limit, int) and 0 < limit <= MAX_LIMIT:
        sys.exit(0)  # explicit, reasonable partial read

    ext = os.path.splitext(path)[1].lower()
    if ext in PASSTHROUGH:
        sys.exit(0)

    try:
        size = os.path.getsize(path)
    except OSError:
        sys.exit(0)  # missing/unreadable: let the tool report the real error

    if size <= SIZE_LIMIT:
        sys.exit(0)

    size_kb = size // 1024
    reason = (
        f"Lecture brute bloquee: {os.path.basename(path)} fait {size_kb} Ko "
        f"(> {SIZE_LIMIT // 1024} Ko). Charger ce fichier entier gaspillerait "
        f"du contexte.\n\nUtilise plutot (search before read):\n{advise(path, ext, size_kb)}\n\n"
        f"Si la lecture integrale est reellement necessaire, relance Read avec "
        f"offset/limit (limit <= {MAX_LIMIT})."
    )
    json.dump({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }}, sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    main()
