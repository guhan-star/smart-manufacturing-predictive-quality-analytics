"""Reproducible retrieval of the official UCI SECOM dataset (ID 179).

Documented retrieval method:
- Primary archive: https://archive.ics.uci.edu/static/public/179/secom.zip
- Dataset landing page: https://archive.ics.uci.edu/dataset/179/secom
- Metadata API (optional): https://archive.ics.uci.edu/api/dataset?id=179
"""

from __future__ import annotations

import hashlib
import json
import urllib.error
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from secom_project import DATA_RAW_DIR

SECOM_ZIP_URL = "https://archive.ics.uci.edu/static/public/179/secom.zip"
SECOM_LANDING_URL = "https://archive.ics.uci.edu/dataset/179/secom"
SECOM_API_URL = "https://archive.ics.uci.edu/api/dataset?id=179"


def sha256_file(path: Path) -> str:
    """Compute SHA-256 hex digest for a file."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def download_file(url: str, destination: Path, timeout: int = 60) -> None:
    """Download a URL to destination using a standard User-Agent."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "smart-manufacturing-secom/0.1 (UCI dataset retrieval)"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        destination.write_bytes(response.read())


def retrieve_secom(output_dir: Path = DATA_RAW_DIR, force: bool = False) -> dict:
    """Download and extract the official UCI SECOM archive and save a manifest."""
    output_dir.mkdir(parents=True, exist_ok=True)
    zip_path = output_dir / "secom.zip"

    if force or not zip_path.exists():
        download_file(SECOM_ZIP_URL, zip_path)

    extracted_files: list[str] = []
    with zipfile.ZipFile(zip_path, "r") as zf:
        for member in zf.infolist():
            if member.is_dir():
                continue
            target = (output_dir / member.filename).resolve()
            if not str(target).startswith(str(output_dir.resolve())):
                raise ValueError(f"Unsafe zip member path: {member.filename}")
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(member) as src, target.open("wb") as dst:
                dst.write(src.read())
            extracted_files.append(member.filename)

    api_metadata_path = output_dir / "uci_api_metadata.json"
    api_status = "unavailable"
    try:
        download_file(SECOM_API_URL, api_metadata_path, timeout=30)
        api_status = "saved"
    except (urllib.error.URLError, TimeoutError) as exc:
        api_status = f"failed: {exc}"

    file_records = {}
    for rel_name in ["secom.zip", *extracted_files]:
        fpath = output_dir / rel_name
        if fpath.is_file():
            file_records[rel_name] = {
                "size_bytes": fpath.stat().st_size,
                "sha256": sha256_file(fpath),
            }

    manifest = {
        "dataset": "UCI SECOM (Semiconductor Manufacturing Process)",
        "uci_id": 179,
        "landing_page": SECOM_LANDING_URL,
        "download_url": SECOM_ZIP_URL,
        "api_metadata_url": SECOM_API_URL,
        "api_metadata_status": api_status,
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "files": file_records,
    }
    manifest_path = output_dir / "DOWNLOAD_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    manifest = retrieve_secom()
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
