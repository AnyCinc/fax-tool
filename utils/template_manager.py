"""テンプレート管理モジュール"""
import json
import os
import shutil
from pathlib import Path
from dataclasses import dataclass

BASE_DIR = Path(__file__).parent.parent
CONFIG_PATH = BASE_DIR / "config.json"
LETTER_DIR = BASE_DIR / "templates" / "letters"
RESUME_DIR = BASE_DIR / "templates" / "resumes"


@dataclass
class TemplateInfo:
    name: str
    filename: str
    path: str
    region: str = ""
    industry: str = ""
    tags: list = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


def load_config() -> dict:
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(config: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_regions() -> list:
    return load_config()["regions"]


def get_industries() -> list:
    return load_config()["industries"]


def get_nationalities() -> list:
    return load_config()["nationalities"]


# --- 手紙テンプレート管理 ---

def list_letter_templates() -> list[TemplateInfo]:
    config = load_config()
    templates = []
    for t in config.get("letter_templates", []):
        path = str(LETTER_DIR / t["filename"])
        if os.path.exists(path):
            templates.append(TemplateInfo(
                name=t["name"], filename=t["filename"], path=path,
                region=t.get("region", ""), industry=t.get("industry", ""),
                tags=t.get("tags", [])
            ))
    return templates


def add_letter_template(
    source_path: str, name: str, region: str = "", industry: str = "", tags: list = None
) -> TemplateInfo:
    LETTER_DIR.mkdir(parents=True, exist_ok=True)
    filename = Path(source_path).name
    dest = LETTER_DIR / filename

    # 重複回避
    counter = 1
    while dest.exists():
        stem = Path(source_path).stem
        ext = Path(source_path).suffix
        dest = LETTER_DIR / f"{stem}_{counter}{ext}"
        filename = dest.name
        counter += 1

    shutil.copy2(source_path, dest)

    config = load_config()
    entry = {
        "name": name, "filename": filename,
        "region": region, "industry": industry,
        "tags": tags or []
    }
    config.setdefault("letter_templates", []).append(entry)
    save_config(config)

    return TemplateInfo(name=name, filename=filename, path=str(dest),
                        region=region, industry=industry, tags=tags or [])


def remove_letter_template(filename: str):
    path = LETTER_DIR / filename
    if path.exists():
        path.unlink()
    config = load_config()
    config["letter_templates"] = [
        t for t in config.get("letter_templates", []) if t["filename"] != filename
    ]
    save_config(config)


# --- 履歴書テンプレート管理 ---

def list_resume_templates() -> list[TemplateInfo]:
    config = load_config()
    templates = []
    for t in config.get("resume_templates", []):
        path = str(RESUME_DIR / t["filename"])
        if os.path.exists(path):
            templates.append(TemplateInfo(
                name=t["name"], filename=t["filename"], path=path,
                region=t.get("region", ""), industry=t.get("industry", ""),
                tags=t.get("tags", [])
            ))
    return templates


def add_resume_template(
    source_path: str, name: str, region: str = "", industry: str = "", tags: list = None
) -> TemplateInfo:
    RESUME_DIR.mkdir(parents=True, exist_ok=True)
    filename = Path(source_path).name
    dest = RESUME_DIR / filename

    counter = 1
    while dest.exists():
        stem = Path(source_path).stem
        ext = Path(source_path).suffix
        dest = RESUME_DIR / f"{stem}_{counter}{ext}"
        filename = dest.name
        counter += 1

    shutil.copy2(source_path, dest)

    config = load_config()
    entry = {
        "name": name, "filename": filename,
        "region": region, "industry": industry,
        "tags": tags or []
    }
    config.setdefault("resume_templates", []).append(entry)
    save_config(config)

    return TemplateInfo(name=name, filename=filename, path=str(dest),
                        region=region, industry=industry, tags=tags or [])


def remove_resume_template(filename: str):
    path = RESUME_DIR / filename
    if path.exists():
        path.unlink()
    config = load_config()
    config["resume_templates"] = [
        t for t in config.get("resume_templates", []) if t["filename"] != filename
    ]
    save_config(config)
