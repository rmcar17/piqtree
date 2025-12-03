#!/usr/bin/env python3
"""
cibw_test_wrapper.py

Run inside cibuildwheel's test venv. Inspect the installed wheel contents for
_import/_dll import/export tables (Windows only) and then run pytest as normal.

Usage (cibuildwheel): set
  CIBW_TEST_COMMAND = python -u build_tools/cibw_test_wrapper.py {package}/tests
so this script runs inside the test venv before pytest.

This script:
 - finds the installed package directory in sys.path (without importing piqtree)
 - locates the _piqtree extension module file (.pyd) and the packaged iqtree DLL
 - on Windows: runs `dumpbin /IMPORTS` on the .pyd and `dumpbin /EXPORTS` on the DLL
   and prints their outputs to stdout (CI logs).
 - finally runs pytest with the passed arguments.
"""

import sys
import os
import glob
import subprocess
import shutil

def find_package_dir(pkg_name="piqtree"):
    # Look through sys.path for the installed package dir (do NOT import)
    for p in sys.path:
        if not p:
            continue
        candidate = os.path.join(p, pkg_name)
        initpy = os.path.join(candidate, "__init__.py")
        if os.path.isfile(initpy):
            return candidate
    return None

def find_extension_file(pkg_dir, base_name="_piqtree"):
    # search for files that start with base_name and end with .pyd (Windows) or .so (others)
    patterns = [
        os.path.join(pkg_dir, base_name + "*.pyd"),
        os.path.join(pkg_dir, base_name + "*.dll"),  # sometimes built as .dll in some setups
        os.path.join(pkg_dir, base_name + "*.so"),
    ]
    for pat in patterns:
        matches = glob.glob(pat)
        if matches:
            # prefer the first (should be unique)
            return matches[0]
    return None

def find_iqtree_dll(pkg_dir):
    # usually under _libiqtree subfolder, but search recursively to be safe
    candidates = glob.glob(os.path.join(pkg_dir, "_libiqtree", "iqtree*.dll")) + \
                 glob.glob(os.path.join(pkg_dir, "**", "iqtree*.dll"), recursive=True)
    return candidates[0] if candidates else None

def run_dumpbin_on_windows(pyd_path, dll_path):
    # dump imports of the pyd and exports of the dll
    dumpbin = shutil.which("dumpbin")
    if not dumpbin:
        print("dumpbin not found in PATH. Skipping dumpbin checks.", file=sys.stderr)
        return

    print("\n=== DUMPBIN: IMPORTS of extension ===")
    print(f"file: {pyd_path}")
    try:
        out = subprocess.check_output([dumpbin, "/IMPORTS", pyd_path], stderr=subprocess.STDOUT, text=True)
        print(out)
    except subprocess.CalledProcessError as e:
        print("dumpbin /IMPORTS failed:", e, file=sys.stderr)
        print(e.output, file=sys.stderr)

    if dll_path:
        print("\n=== DUMPBIN: EXPORTS of iqtree DLL ===")
        print(f"file: {dll_path}")
        try:
            out = subprocess.check_output([dumpbin, "/EXPORTS", dll_path], stderr=subprocess.STDOUT, text=True)
            print(out)
        except subprocess.CalledProcessError as e:
            print("dumpbin /EXPORTS failed:", e, file=sys.stderr)
            print(e.output, file=sys.stderr)
    else:
        print("\nNo iqtree DLL found inside installed package - cannot check exports.", file=sys.stderr)

def main():
    if len(sys.argv) < 2:
        pytest_args = []
    else:
        pytest_args = sys.argv[1:]

    print("cibw_test_wrapper: locating installed package directory ...")
    pkg_dir = find_package_dir("piqtree")
    if not pkg_dir:
        print("ERROR: Could not find installed 'piqtree' package directory in sys.path.", file=sys.stderr)
        print("sys.path:", sys.path, file=sys.stderr)
        # Still try to run tests (they will likely fail)
    else:
        print("Found piqtree package dir:", pkg_dir)

        pyd_path = find_extension_file(pkg_dir, "_piqtree")
        if pyd_path:
            print("Found extension file:", pyd_path)
        else:
            print("WARNING: Could not find _piqtree extension file in package dir.", file=sys.stderr)
            # continue to search for DLLs anyway

        dll_path = find_iqtree_dll(pkg_dir)
        if dll_path:
            print("Found iqtree DLL:", dll_path)
        else:
            print("WARNING: Could not find iqtree DLL inside package dir (search failed).", file=sys.stderr)

        if os.name == "nt":
            run_dumpbin_on_windows(pyd_path if pyd_path else "", dll_path)

    # Finally execute pytest with the provided arguments
    print("\n=== Running pytest ===")
    # Ensure we use the current venv's python to run pytest via subprocess so output is visible
    python_exe = sys.executable
    cmd = [python_exe, "-m", "pytest"] + pytest_args
    print("Executing:", " ".join(cmd))
    return_code = subprocess.call(cmd)
    sys.exit(return_code)


if __name__ == "__main__":
    main()
