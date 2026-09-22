#!/usr/bin/env python3
"""Minimal status line: model | effort | context used.

Reads the status payload on stdin, prints one line. No subprocess, no network.
Every field is optional and rendered only when the payload actually carries it.
"""
import json
import sys


def main():
    try:
        d = json.load(sys.stdin)
    except Exception:
        print("")
        return

    bits = []

    m = d.get("model") or {}
    name = m.get("display_name") or m.get("id")
    if name:
        bits.append(str(name))

    lvl = (d.get("effort") or {}).get("level")
    if lvl:
        bits.append(f"effort:{lvl}")

    cw = d.get("context_window") or {}
    used = cw.get("used_tokens")
    total = cw.get("total_tokens") or cw.get("max_tokens") or cw.get("context_window")
    pct = cw.get("percent_used")
    if isinstance(pct, (int, float)):
        bits.append(f"ctx:{pct:.0f}% ({100 - pct:.0f}% libre)")
    elif isinstance(used, int) and isinstance(total, int) and total > 0:
        p = 100.0 * used / total
        bits.append(f"ctx:{used // 1000}k/{total // 1000}k ({100 - p:.0f}% libre)")
    elif isinstance(used, int):
        bits.append(f"ctx:{used // 1000}k")

    if d.get("fast_mode"):
        bits.append("fast")

    print(" | ".join(bits))


if __name__ == "__main__":
    main()
