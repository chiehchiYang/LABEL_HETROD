from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "sample_data"
TARGET = ROOT / "data"

FILES = [
    "00_background.png",
    "00_background_semantic.png",
    "00_tracks.csv",
    "00_tracksMeta.csv",
    "area_color_class.json",
    "labeled_scenarios.json",
    "pet_distance_dict.json",
    "track_frame_dict.json",
    "trackid_class.json",
    "trackid_objects.json",
]


def main() -> None:
    TARGET.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        shutil.copy2(SOURCE / name, TARGET / name)
    print(f"Copied {len(FILES)} sample files into {TARGET}")


if __name__ == "__main__":
    main()
