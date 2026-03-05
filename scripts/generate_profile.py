#!/usr/bin/env python3
"""
Generate profile.json for a Proton .wcp package.
Usage: generate_profile.py <output_path> <version_name> <version_code> <description>
"""
import json
import sys


def main():
    if len(sys.argv) < 5:
        print("Usage: generate_profile.py <output_path> <version_name> <version_code> <description>")
        sys.exit(1)

    out_path = sys.argv[1]
    version_name = sys.argv[2]
    version_code = int(sys.argv[3])
    description = sys.argv[4]

    profile = {
        "type": "Proton",
        "versionName": version_name,
        "versionCode": version_code,
        "description": description,
        "files": [],
        "proton": {
            "binPath": "bin",
            "libPath": "lib",
            "prefixPack": "prefixPack.txz"
        }
    }

    with open(out_path, "w") as f:
        json.dump(profile, f, indent=2)

    print(f"profile.json written to {out_path}")


if __name__ == "__main__":
    main()
