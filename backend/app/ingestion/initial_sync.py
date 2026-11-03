"""Initial synchronization bootstrap for OpenStreetMap places, admin areas, and facilities.

Copies pre-built OSM extracts if missing from the runtime data directory.
"""

from __future__ import annotations

from pathlib import Path
import shutil

from app.core.logging import get_logger

log = get_logger(__name__)

BUNDLED_DIR = Path(__file__).resolve().parents[3] / "infra" / "osm" / "data"


def ensure_osm_extracts(places_path: Path, admin_path: Path, facilities_path: Path) -> None:
    """Ensures all three extract files exist, copying from bundled seed files if missing."""
    places_path.parent.mkdir(parents=True, exist_ok=True)
    admin_path.parent.mkdir(parents=True, exist_ok=True)
    facilities_path.parent.mkdir(parents=True, exist_ok=True)

    mappings = [
        (places_path, "places.geojsonseq"),
        (admin_path, "admin.geojsonseq"),
        (facilities_path, "facilities.geojsonseq"),
    ]

    for target, filename in mappings:
        if not target.exists():
            source = BUNDLED_DIR / filename
            if source.exists():
                shutil.copyfile(source, target)
                log.info("osm_extract_bootstrapped", target=str(target), source=str(source))
