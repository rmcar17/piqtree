"""
piqtree._cibw_check

This module is intended to be executed inside cibuildwheel's test venv as:

  python -m piqtree._cibw_check {pytest-args}

Because it lives inside the package, it will be installed with the wheel and
can inspect the actual installed extension (.pyd) and packaged iqtree dll.

It prints import/export tables (Windows) for debugging missing-procedure loader
errors and then runs pytest with any provided args.
"""

from __future__ import annotations

import glob
import os
import shutil
import subprocess
import sys
from typing import Optional


def find_package_dir() -> Optional[str]:
    # __file__ inside installed package refers to this module file path
    # the package dir is the containing directory of this file
    pkg_dir = os.path.dirname(__file__)
    if os.path.isdir(pkg_dir):
        return pkg_dir
    return None


def find_extension_file(pkg_dir: str, base_name: str = "_piqtree"):
    patterns = [
        os.path.join(pkg_dir, base_name + "*.pyd"),
        os.path.join(pkg_dir, base_name + "*.dll"),
        os.path.join(pkg_dir, base_name + "*.so"),
    ]
    for pat in patterns:
        matches = glob.glob(pat)
        if matches:
            return matches[0]
    return None


def find_iqtree_dll(pkg_dir: str) -> Optional[str]:
    # usual location: <pkg_dir>/_libiqtree/iqtree.dll
    candidate = os.path.join(pkg_dir, "_libiqtree", "iqtree.dll")
    if os.path.isfile(candidate):
        return candidate

    # fallback: recursive search for iqtree*.dll
    found = glob.glob(os.path.join(pkg_dir, "**", "iqtree*.dll"), recursive=True)
    return found[0] if found else None


def run_dumpbin_imports(pyd_path: str):
    dumpbin = shutil.which("dumpbin")
    if not dumpbin:
        print("dumpbin not found in PATH; cannot run dumpbin /IMPORTS", file=sys.stderr)
        return

    print("\n=== DUMPBIN: IMPORTS OF EXTENSION ===")
    print("Path:", pyd_path)
    try:
        out = subprocess.check_output([dumpbin, "/IMPORTS", pyd_path], stderr=subprocess.STDOUT, text=True)
        print(out)
    except subprocess.CalledProcessError as e:
        print("dumpbin /IMPORTS failed:", e, file=sys.stderr)
        print(e.output, file=sys.stderr)


def run_dumpbin_exports(dll_path: str):
    dumpbin = shutil.which("dumpbin")
    if not dumpbin:
        print("dumpbin not found in PATH; cannot run dumpbin /EXPORTS", file=sys.stderr)
        return

    print("\n=== DUMPBIN: EXPORTS OF IQTREE DLL ===")
    print("Path:", dll_path)
    try:
        out = subprocess.check_output([dumpbin, "/EXPORTS", dll_path], stderr=subprocess.STDOUT, text=True)
        print(out)
    except subprocess.CalledProcessError as e:
        print("dumpbin /EXPORTS failed:", e, file=sys.stderr)
        print(e.output, file=sys.stderr)


def main():
    # The test arguments (pytest path etc.) are forwarded from cibuildwheel
    pytest_args = sys.argv[1:] if len(sys.argv) > 1 else []

    print("piqtree._cibw_check running in", sys.executable)
    pkg_dir = find_package_dir()
    print("Detected installed piqtree package dir:", pkg_dir)

    if not pkg_dir:
        print("ERROR: Could not determine package directory. Aborting dumpbin checks.", file=sys.stderr)
    else:
        ext_path = find_extension_file(pkg_dir, "_piqtree")
        if ext_path:
            print("Found extension file:", ext_path)
        else:
            print("WARNING: Could not find _piqtree extension file in package dir.", file=sys.stderr)

        dll_path = find_iqtree_dll(pkg_dir)
        if dll_path:
            print("Found iqtree DLL:", dll_path)
        else:
            print("WARNING: Could not find iqtree DLL inside package dir.", file=sys.stderr)

        # Only run dumpbin on Windows; it is the relevant tool for Windows loader errors.
        if os.name == "nt":
            if ext_path:
                run_dumpbin_imports(ext_path)
            else:
                print("Skipping import dump: extension file not found.", file=sys.stderr)
            if dll_path:
                run_dumpbin_exports(dll_path)
            else:
                print("Skipping export dump: iqtree DLL not found.", file=sys.stderr)
        else:
            print("Non-Windows environment: printing basic discovered artifacts.")
            print("extension:", ext_path)
            print("iqtree dll:", dll_path)

    # Now execute pytest with the same args passed by cibuildwheel
    print("\n=== Running pytest ===")
    cmd = [sys.executable, "-m", "pytest", *pytest_args]
    print("Executing:", " ".join(cmd))
    # Use subprocess.call so test output is streamed and the exit code propagates
    rc = subprocess.call(cmd)
    sys.exit(rc)


if __name__ == "__main__":
    main()
