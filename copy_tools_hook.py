import sys
import os
import shutil
from pathlib import Path

if getattr(sys, 'frozen', False):
    base_path = Path(sys.executable).parent
    internal_path = base_path / "_internal"
    tools_internal = internal_path / "tools"
    tools_external = base_path / "tools"

    if tools_internal.exists() and not tools_external.exists():
        shutil.copytree(tools_internal, tools_external)
        print(f"Copied tools folder next to exe")