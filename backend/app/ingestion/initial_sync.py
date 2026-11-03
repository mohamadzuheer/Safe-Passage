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


async def seed_initial_osm(pool) -> None:
    """Populates facilities, places, and admin areas from bundled extracts if tables are empty."""
    async with pool.acquire() as conn:
        count = await conn.fetchval("SELECT count(*) FROM facilities")
        if count and count > 0:
            return

        facilities_file = BUNDLED_DIR / "facilities.geojsonseq"
        if facilities_file.exists():
            from app.ingestion.sources.facilities import parse_extract
            from app.ingestion.store import upsert_facilities
            facs = parse_extract(facilities_file)
            if facs:
                async with conn.transaction():
                    await upsert_facilities(conn, facs)
                log.info("initial_facilities_seeded", count=len(facs))

        places_file = BUNDLED_DIR / "places.geojsonseq"
        admin_file = BUNDLED_DIR / "admin.geojsonseq"
        if places_file.exists() and admin_file.exists():
            from app.ingestion.sources.osm_extract import parse_admin, parse_places
            from app.ingestion.store import upsert_admin_areas, upsert_places
            places = parse_places(places_file)
            admin_areas = parse_admin(admin_file)
            async with conn.transaction():
                if places:
                    await upsert_places(conn, places)
                if admin_areas:
                    await upsert_admin_areas(conn, admin_areas)
            log.info("initial_osm_places_admin_seeded", places=len(places), admin_areas=len(admin_areas))
