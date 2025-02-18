import subprocess
import os

from pathlib import Path

os.chdir("working")


files = list(filter(lambda x: x.endswith(".a"), os.listdir()))
while files:
    print(files)
    for file in files:
        if file.endswith(".a"):
            subprocess.run(["ar", "x", file])
            os.unlink(file)
    files = list(filter(lambda x: x.endswith(".a"), os.listdir()))