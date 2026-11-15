"""Render the README screenshots and hero image with flow-render.

Usage (from the repo root):

    uv run --no-project --with flow-render==0.15.0 --with pip python docs/screenshots/render.py

Each ``<shot>.json`` is a flow-render config. A result either names an image
``icon`` or describes a bookmark ``cover`` tile (``text`` and ``color``), which
is drawn here so the screenshots need no real bookmark thumbnails.
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
SHOTS_DIR = ROOT / "docs" / "screenshots"
ASSETS_DIR = ROOT / ".github" / "assets"
THEMES = ("dark", "light")
HERO = {"shot": "hero", "theme": "dark", "css": ["win11-dark.css", "docs/screenshots/hero.css"]}
COVER_FONT = ImageFont.load_default(size=52)


def cover_png(cover: dict, out_dir: Path) -> Path:
    path = out_dir / f"cover-{cover['text']}-{cover['color'].lstrip('#')}.png"
    if not path.exists():
        image = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((4, 4, 124, 124), radius=24, fill=cover["color"])
        draw.text((64, 64), cover["text"], font=COVER_FONT, fill="#FFFFFF", anchor="mm")
        image.save(path)
    return path


def flow_render(args, out_path: Path) -> None:
    with tempfile.TemporaryDirectory() as out_dir:
        subprocess.run(["flow-render", *args, "-o", out_dir], check=True, cwd=ROOT)
        (rendered,) = Path(out_dir).glob("*.png")
        shutil.move(str(rendered), out_path)
    print(f"Wrote {out_path}")


def render_config(shot: str, css, out_path: Path, work: Path) -> None:
    config = json.loads((SHOTS_DIR / f"{shot}.json").read_text(encoding="utf-8"))
    config["icon"] = str((SHOTS_DIR / config["icon"]).resolve())
    for result in config["results"]:
        if "cover" in result:
            result["icon"] = str(cover_png(result.pop("cover"), work))
    config["css"] = css
    config_path = work / f"{shot}-{out_path.stem}.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    flow_render(["-c", str(config_path)], out_path)


def main() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    shots = sorted(path.stem for path in SHOTS_DIR.glob("*.json") if path.stem != HERO["shot"])
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for shot in shots:
            for theme in THEMES:
                render_config(shot, f"win11-{theme}.css", ASSETS_DIR / f"{shot}-{theme}.png", work)
        render_config(HERO["shot"], HERO["css"], ASSETS_DIR / "hero.png", work)

        package = subprocess.run([str(ROOT / "scripts" / "package.sh"), str(work / "dist")], check=True, capture_output=True, text=True)
        plugin_zip = package.stdout.strip().splitlines()[-1]
        for theme in THEMES:
            flow_render(["-u", plugin_zip, "-i", "-s", f"win11-{theme}", "--hide-caret"], ASSETS_DIR / f"install-{theme}.png")


if __name__ == "__main__":
    sys.exit(main())
