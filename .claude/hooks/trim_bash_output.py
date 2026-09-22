#!/usr/bin/env python3
"""PostToolUse hook for Bash: preserve a huge output locally and summarise it.

LIMITATION (verified against the installed CLI, v2.1.278): a command hook
CANNOT rewrite a tool result. The PostToolUse hookSpecificOutput schema accepts
only `additionalContext`; no `updatedOutput` field exists. So this hook does not
shrink the output that already reached the model -- guard_bash.py prevents that
case. What this does: dump the raw output to disk so it stays greppable, and
hand back a deterministic digest (errors first, then head/tail) so the NEXT step
does not re-run the same dump.
"""
import json
import os
import re
import sys
import time

THRESHOLD = 16000      # chars: below this, stay silent
HEAD_LINES = 40
TAIL_LINES = 40
ERR_LINES = 30
ERR_RE = re.compile(
    r"\b(error|errors|failed|failure|failures|traceback|exception|fatal|"
    r"assert|assertion|panic|E\d{3}|FAIL|✗|✖)\b", re.IGNORECASE)
SUMMARY_RE = re.compile(
    r"((?<![\w])\d+\s+(passed|failed|errors?|skipped|warnings?)\b"
    r"|\btests?\s+run\b|^OK$|^\s*(BUILD (SUCCESS|FAILED)|Summary|Total)\b)",
    re.IGNORECASE | re.MULTILINE)


def raw_dir():
    base = (os.environ.get("CLAUDE_CODE_TMPDIR")
            or os.environ.get("TMPDIR") or "/tmp")
    d = os.path.join(base, "claude-bash-output")
    os.makedirs(d, exist_ok=True)
    return d


def extract(resp):
    """Flatten a Bash tool_response into text, whatever shape it has."""
    if isinstance(resp, str):
        return resp
    if isinstance(resp, dict):
        return "\n".join(
            str(resp[k]) for k in ("stdout", "stderr", "output", "content")
            if resp.get(k))
    return ""


def digest(text, path):
    lines = text.splitlines()
    n = len(lines)
    errs = [l for l in lines if ERR_RE.search(l)][:ERR_LINES]
    summ = [l for l in lines if SUMMARY_RE.search(l)][:5]

    parts = [f"Sortie volumineuse: {n} lignes / {len(text)} caracteres.",
             f"Sortie brute complete conservee dans: {path}",
             f"Pour la fouiller: rg -n 'MOTIF' {path}", ""]
    if errs:
        parts.append(f"--- erreurs / echecs ({len(errs)} retenues) ---")
        parts.extend(errs)
        parts.append("")
    if summ:
        parts.append("--- resume ---")
        parts.extend(summ)
        parts.append("")
    if n > HEAD_LINES + TAIL_LINES:
        parts.append(f"--- {HEAD_LINES} premieres lignes ---")
        parts.extend(lines[:HEAD_LINES])
        parts.append(f"\n[... {n - HEAD_LINES - TAIL_LINES} lignes retirees "
                     f"-- voir {path} ...]\n")
        parts.append(f"--- {TAIL_LINES} dernieres lignes ---")
        parts.extend(lines[-TAIL_LINES:])
    return "\n".join(parts)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)
    if payload.get("tool_name") != "Bash":
        sys.exit(0)

    text = extract(payload.get("tool_response"))
    if len(text) <= THRESHOLD:
        sys.exit(0)

    path = os.path.join(raw_dir(), f"bash-{int(time.time() * 1000)}.txt")
    try:
        with open(path, "w", encoding="utf-8", errors="replace") as fh:
            fh.write(text)
    except OSError:
        path = "(ecriture impossible)"

    json.dump({"hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": digest(text, path),
    }}, sys.stdout)


if __name__ == "__main__":
    main()
