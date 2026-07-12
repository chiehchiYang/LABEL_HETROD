from pathlib import Path
import os
import sys
import runpy


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    os.chdir(project_root / "label_tool")
    sys.path.insert(0, str(project_root / "label_tool"))
    target = project_root / "label_tool" / "start.py"
    runpy.run_path(str(target), run_name="__main__")