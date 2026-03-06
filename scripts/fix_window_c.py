#!/usr/bin/env python3
"""
Surgically wraps xinput2-dependent code in dlls/winex11.drv/window.c
with #ifdef HAVE_X11_EXTENSIONS_XINPUT2_H guards.

Handles cases where patch hunk offsets drift against bleeding-edge and
git apply fails to insert the guards, causing compile errors when building
for Android (which lacks XInput2 headers).

Usage: fix_window_c.py <wine-source-dir>
"""
import sys
import os


IFDEF = "#ifdef HAVE_X11_EXTENSIONS_XINPUT2_H"
ENDIF = "#endif"


def prev_nonblank(lines, idx):
    """Return the stripped content of the nearest non-blank line before idx."""
    for j in range(idx - 1, -1, -1):
        s = lines[j].strip()
        if s:
            return s
    return ""


def is_guarded(lines, idx):
    """Return True if line idx is already inside a HAVE_X11_EXTENSIONS_XINPUT2_H block."""
    depth = 0
    for j in range(idx - 1, -1, -1):
        s = lines[j].strip()
        if s.startswith("#endif"):
            depth += 1
        elif s.startswith("#ifdef") or s.startswith("#if "):
            if depth == 0:
                return IFDEF.strip() in s
            depth -= 1
    return False


def main():
    if len(sys.argv) < 2:
        print("Usage: fix_window_c.py <wine-source-dir>")
        sys.exit(1)

    wine_src = sys.argv[1]
    window_c = os.path.join(wine_src, "dlls", "winex11.drv", "window.c")

    if not os.path.exists(window_c):
        print(f"ERROR: {window_c} not found")
        sys.exit(1)

    with open(window_c) as f:
        lines = f.readlines()

    result = []
    changes = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        needs_guard = False

        # Check for bare xinput2_rawinput assignment
        if "data->xinput2_rawinput" in line and "=" in line:
            if not is_guarded(result + [line], len(result)):
                needs_guard = True

        # Check for bare x11drv_xinput2_enable call
        if "x11drv_xinput2_enable" in line and not needs_guard:
            if not is_guarded(result + [line], len(result)):
                needs_guard = True

        if needs_guard:
            # Collect consecutive xinput2 lines to wrap together
            block = [line]
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                if ("x11drv_xinput2_enable" in next_line or
                        "data->xinput2_rawinput" in next_line):
                    block.append(next_line)
                    j += 1
                else:
                    break
            result.append(IFDEF + "\n")
            result.extend(block)
            result.append(ENDIF + "\n")
            changes += 1
            for b in block:
                print(f"  Added guard around: {b.rstrip()}")
            i = j
        else:
            result.append(line)
            i += 1

    with open(window_c, "w") as f:
        f.writelines(result)

    print(f"\nDone. Applied {changes} xinput2 guard fix(es) to window.c")


if __name__ == "__main__":
    main()
