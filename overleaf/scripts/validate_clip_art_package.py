#!/usr/bin/env python3
"""Fail-closed validation of the clip-art package before figure composition."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SET = ROOT / "assets" / "clip-art-set"
AUDITS = ROOT / "audits"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    manifest = json.loads((SET / "clip-art-manifest.json").read_text(encoding="utf-8"))
    checks: dict[str, bool] = {
        "exactly_eight_assets": len(manifest.get("assets", [])) == 8,
        "clip_art_precedes_diagrams": str(manifest.get("build_order", "")).startswith("clip-art SVG"),
        "named_role_palette": set(manifest["art_direction"]["palette"]) >= {"ink", "primary", "secondary", "caution", "boundary"},
    }
    seen: set[str] = set()
    for asset in manifest.get("assets", []):
        asset_id = asset["id"]
        seen.add(asset_id)
        svg = SET / asset["file"]
        png = SET / asset["derived_png"]
        raw = svg.read_text(encoding="utf-8")
        checks[f"{asset_id}_svg_checksum"] = sha(svg) == asset["checksum_sha256"]
        checks[f"{asset_id}_png_checksum"] = sha(png) == asset["derived_png_checksum_sha256"]
        checks[f"{asset_id}_no_raster_or_external_link"] = not re.search(r"<(?:image|foreignObject)\b|(?:href|xlink:href)=[\"']https?://", raw, re.I)
        with Image.open(png) as image:
            image.load()
            alpha = image.getchannel("A") if image.mode == "RGBA" else None
            checks[f"{asset_id}_transparent_png"] = alpha is not None and alpha.getextrema()[0] < 255
    contact = manifest["contact_sheet"]
    contact_png = SET / contact["png"]
    contact_svg = SET / contact["svg"]
    with Image.open(contact_png) as image:
        image.load()
        checks["contact_sheet_decodes_fully"] = list(image.size) == contact["dimensions_px"]
    checks["contact_png_checksum"] = sha(contact_png) == contact["png_checksum_sha256"]
    checks["contact_svg_checksum"] = sha(contact_svg) == contact["svg_checksum_sha256"]
    checks["unique_asset_ids"] = len(seen) == 8
    status = "PASS" if all(checks.values()) else "FAIL"
    report = {"status": status, "asset_ids": sorted(seen), "checks": checks}
    AUDITS.mkdir(exist_ok=True)
    (AUDITS / "clip_art_validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
