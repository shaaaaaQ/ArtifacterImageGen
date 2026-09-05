from __future__ import annotations

import hashlib
import json
import os
import sys
import tempfile
from collections.abc import Mapping
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from PIL import Image

CACHE_ENV = "ARTIFACTER_IMAGE_GEN_CACHE_DIR"
AFFIXES_URL = (
    "https://raw.githubusercontent.com/EnkaNetwork/API-docs/"
    "master/store/gi/affixes.json"
)


def default_cache_dir(
    environ: Mapping[str, str] = os.environ,
    platform: str = sys.platform,
    home: Path | None = None,
) -> Path:
    """Return an OS-appropriate, user-writable cache directory."""
    if override := environ.get(CACHE_ENV):
        return Path(override).expanduser()

    home = home or Path.home()
    if platform == "win32":
        root = Path(environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
    elif platform == "darwin":
        root = home / "Library" / "Caches"
    else:
        root = Path(environ.get("XDG_CACHE_HOME", home / ".cache"))
    return root / "artifacter-image-gen"


class AssetCache:
    """Disk cache for remote Enka images and artifact-affix metadata."""

    def __init__(self, directory: str | Path | None = None, timeout: float = 20) -> None:
        self.directory = Path(directory) if directory else default_cache_dir()
        self.timeout = timeout

    def image(self, url: str) -> Image.Image:
        suffix = Path(urlsplit(url).path).suffix or ".png"
        basename = Path(urlsplit(url).path).stem or "image"
        digest = hashlib.sha256(url.encode()).hexdigest()[:12]
        path = self.directory / "images" / f"{basename}-{digest}{suffix}"
        if not path.exists():
            self._download(url, path)
        with Image.open(path) as image:
            return image.copy()

    def affixes(self) -> dict[str, dict[str, float | int]]:
        path = self.directory / "data" / "affixes.json"
        if not path.exists():
            self._download(AFFIXES_URL, path)
        with path.open(encoding="utf-8") as file:
            return json.load(file)

    def _download(self, url: str, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        request = Request(url, headers={"User-Agent": "artifacter-image-gen"})
        temporary: Path | None = None
        try:
            with urlopen(request, timeout=self.timeout) as response:  # noqa: S310
                with tempfile.NamedTemporaryFile(
                    dir=destination.parent, prefix=".download-", delete=False
                ) as file:
                    temporary = Path(file.name)
                    while chunk := response.read(64 * 1024):
                        file.write(chunk)
            temporary.replace(destination)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
