#!/usr/bin/env python3
"""
Comment out only the patches that are intentionally handled by local fix scripts.

All other GameNative patches should stay in build-step-arm64ec.sh so the
patched apply logic can attempt a real apply/reverse-check/3way merge instead
of being skipped based on a loose marker heuristic.

Usage: filter_patches.py <build-script-path> <wine-source-path>
"""
import re
import sys


# Only patches replaced by local fix scripts should be filtered here.
# Anything else must remain in the PATCHES array so patch_build_script.py can
# try to apply it properly even when upstream has drifted.
HANDLED_LOCALLY = {
    "dlls_winex11_drv_window_c.patch": "handled by fix_window_c.py",
}


def main():
    if len(sys.argv) < 3:
        print("Usage: filter_patches.py <build-script> <wine-source-dir>")
        sys.exit(1)

    script_path = sys.argv[1]

    with open(script_path) as f:
        content = f.read()

    skipped = []
    for patch_name, reason in HANDLED_LOCALLY.items():
        pattern = r'(\s*)"' + re.escape(patch_name) + r'"'
        replacement = r'\1# (' + reason + r') # "' + patch_name + '"'
        new_content = re.sub(pattern, replacement, content)
        if new_content != content:
            content = new_content
            skipped.append(patch_name)
            print(f"SKIP ({reason}): {patch_name}")
        else:
            print(f"NOT FOUND IN SCRIPT (no change): {patch_name}")

    with open(script_path, 'w') as f:
        f.write(content)

    print(f"\nDone. Skipped {len(skipped)} locally handled patch(es).")


if __name__ == "__main__":
    main()
