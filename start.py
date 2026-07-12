from pathlib import Path
import os
import argparse
import sys
import runpy


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent
    data_root = project_root / "data"

    parser = argparse.ArgumentParser(description="Label_HetroD launcher")
    parser.add_argument(
        "--sample-data",
        action="store_true",
        help="Use sample_data instead of the full data directory",
    )
    args = parser.parse_args()

    if args.sample_data:
        os.environ["LABEL_HETROD_DATA_DIR"] = str(project_root / "sample_data")

    os.chdir(project_root / "label_tool")
    sys.path.insert(0, str(project_root / "label_tool"))
    target = project_root / "label_tool" / "start.py"
    runpy.run_path(str(target), run_name="__main__")