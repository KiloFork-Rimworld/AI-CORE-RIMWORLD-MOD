#!/usr/bin/env python3
"""Validate and optionally package the *isolated* RimWorld 1.6 Field Triage mod.

This is a STATIC check: XML well-formedness, complete gameplay data,
whitelisted vanilla def references, resource costs, no binary DLLs/legacy Defs,
and deterministic packaging. It cannot claim RimWorld loaded or played the mod.
No Steam/game/saves/network/runtime probe is performed or required.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

PROJECT = Path(__file__).resolve().parents[1]
REL = Path("Playable/AI-Core-Field-Triage")
FILES = (
    "About/About.xml",
    "Defs/RecipeDefs/FieldDressings.xml",
    "Defs/ResearchProjectDefs/FieldTriage.xml",
)
PACKAGE = "kilomusician.aicore.fieldtriage"
VANILLA = frozenset({
    "Cloth", "MedicineHerbal", "CraftingSpot", "DrugLab",
    "MicroelectronicsBasics", "Crafting", "DrugProductionSpeed",
})
RECIPES = {
    "KiloAI_PrepareFieldDressing": {
        "materials": {"Cloth": 16, "MedicineHerbal": 1},
        "medicine": 2, "bench": {"CraftingSpot", "DrugLab"},
        "research": None, "skill": 3, "work": 850,
    },
    "KiloAI_BulkFieldDressings": {
        "materials": {"Cloth": 40, "MedicineHerbal": 3},
        "medicine": 6, "bench": {"DrugLab"},
        "research": "KiloAI_FieldTriageNetwork", "skill": 6, "work": 1850,
    },
}


class StaticModError(ValueError):
    pass


def _items(node: ET.Element, path: str) -> list[str]:
    return [x.text.strip() for x in node.findall(path) if x.text and x.text.strip()]


def _text(node: ET.Element, path: str) -> str:
    value = node.findtext(path)
    if value is None or not value.strip():
        raise StaticModError(f"missing XML field {path}")
    return value.strip()


def verify(root: Path = PROJECT) -> dict:
    """No writes, external files, games, installed mods, or process calls."""
    base = root / REL
    if not base.is_dir() or base.is_symlink():
        raise StaticModError(f"missing/symlink mod root: {base}")
    actual: list[str] = []
    for entry in base.rglob("*"):
        if entry.is_symlink():
            raise StaticModError(f"symlink refused: {entry}")
        if entry.is_file():
            actual.append(entry.relative_to(base).as_posix())
    if sorted(actual) != sorted(FILES):
        raise StaticModError(f"unexpected or missing packaged files: {sorted(actual)}")
    xml = {}
    for item in FILES:
        path = base / item
        if path.stat().st_size > 128 * 1024:
            raise StaticModError(f"oversized XML: {item}")
        try:
            xml[item] = ET.parse(path).getroot()
        except ET.ParseError as exc:
            raise StaticModError(f"invalid XML in {item}: {exc}") from exc

    about = xml["About/About.xml"]
    if about.tag != "ModMetaData":
        raise StaticModError("About.xml must have ModMetaData root")
    if _text(about, "packageId") != PACKAGE:
        raise StaticModError("wrong package ID")
    versions = _items(about, "supportedVersions/li")
    if versions != ["1.6"]:
        raise StaticModError("only verified target version 1.6 may be advertised")
    if len(_text(about, "description")) < 45:
        raise StaticModError("mod description must state actual scope")

    res = xml["Defs/ResearchProjectDefs/FieldTriage.xml"]
    if res.tag != "Defs":
        raise StaticModError("research must use Defs root")
    research = res.findall("ResearchProjectDef")
    if len(research) != 1:
        raise StaticModError("expected exactly one research project")
    r = research[0]
    research_id = _text(r, "defName")
    if research_id != "KiloAI_FieldTriageNetwork":
        raise StaticModError("unexpected research def")
    if _items(r, "prerequisites/li") != ["MicroelectronicsBasics"]:
        raise StaticModError("must depend only on known vanilla microelectronics")
    if float(_text(r, "baseCost")) != 350 or _text(r, "techLevel") != "Industrial":
        raise StaticModError("unexpected research progression/cost")

    defs = xml["Defs/RecipeDefs/FieldDressings.xml"]
    if defs.tag != "Defs":
        raise StaticModError("recipes must use Defs root")
    recipes = defs.findall("RecipeDef")
    if len(recipes) != len(RECIPES):
        raise StaticModError("expected exactly the two billable treatment recipes")
    observed: set[str] = set()
    resource_changes = {}
    for recipe in recipes:
        ident = _text(recipe, "defName")
        if not re.fullmatch(r"KiloAI_[A-Za-z0-9_]+", ident) or ident in observed:
            raise StaticModError("foreign or duplicate recipe def")
        observed.add(ident)
        expectation = RECIPES.get(ident)
        if expectation is None:
            raise StaticModError(f"unrecognized recipe: {ident}")
        users = set(_items(recipe, "recipeUsers/li"))
        if users != expectation["bench"] or not users <= VANILLA:
            raise StaticModError(f"bad vanilla benches for {ident}")
        inputs = {}
        for li in recipe.findall("ingredients/li"):
            choices = _items(li, "filter/thingDefs/li")
            if len(choices) != 1 or choices[0] not in VANILLA:
                raise StaticModError(f"ambiguous/unknown ingredient: {ident}")
            raw = _text(li, "count")
            if not raw.isdecimal() or int(raw) <= 0 or choices[0] in inputs:
                raise StaticModError(f"invalid/duplicate ingredient count: {ident}")
            inputs[choices[0]] = int(raw)
        if inputs != expectation["materials"]:
            raise StaticModError(f"medicine input costs drifted: {ident}")
        fixed = set(_items(recipe, "fixedIngredientFilter/thingDefs/li"))
        if fixed != set(inputs):
            raise StaticModError(f"ingredient selector can substitute unsafe resources: {ident}")
        outputs = recipe.find("products")
        if outputs is None or len(outputs) != 1 or outputs[0].tag != "MedicineHerbal":
            raise StaticModError("only existing herbal medicine may be produced")
        product_str = (outputs[0].text or "").strip()
        if not product_str.isdecimal() or int(product_str) != expectation["medicine"]:
            raise StaticModError(f"unexpected medicine output: {ident}")
        if int(product_str) <= inputs["MedicineHerbal"] or inputs["Cloth"] < 8:
            raise StaticModError("an upgrade must cost cloth and have a real extra treatment")
        if _text(recipe, "workSkill") != "Crafting" or _text(recipe, "workSpeedStat") != "DrugProductionSpeed":
            raise StaticModError(f"unexpected work skill or stat in {ident}")
        if _text(recipe, "requiredGiverWorkType") != "Crafting":
            raise StaticModError(f"unexpected worktype in {ident}")
        skills = recipe.findall("skillRequirements/li")
        if len(skills) != 1 or _text(skills[0], "skill") != "Crafting":
            raise StaticModError(f"missing Crafting minimum in {ident}")
        if int(_text(skills[0], "minLevel")) != expectation["skill"]:
            raise StaticModError(f"incorrect skill gate in {ident}")
        if int(_text(recipe, "workAmount")) != expectation["work"]:
            raise StaticModError(f"incorrect paid work ticks in {ident}")
        actual_research = recipe.findtext("researchPrerequisite")
        if actual_research != expectation["research"]:
            raise StaticModError(f"unexpected research gate in {ident}")
        resource_changes[ident] = {
            "cloth_spent": inputs["Cloth"],
            "medicine_spent": inputs["MedicineHerbal"],
            "medicine_produced": int(product_str),
            "net_medicine": int(product_str) - inputs["MedicineHerbal"],
        }
    if observed != set(RECIPES):
        raise StaticModError("recipes incomplete")
    return {
        "status": "STATIC_VALIDATED_GAME_UNVERIFIED",
        "package_id": PACKAGE,
        "target_version": "1.6",
        "recipe_count": len(recipes),
        "research_count": 1,
        "resources": resource_changes,
        "allowed_vanilla_references": sorted(VANILLA),
        "actual_rimworld_def_loading": "UNVERIFIED",
        "actual_player_bill_creation": "UNVERIFIED",
        "installed_mod_test": "UNVERIFIED",
    }


def package(root: Path, output: Path) -> dict:
    report = verify(root)
    base = root / REL
    dest = output.expanduser().resolve()
    if dest.suffix.lower() != ".zip":
        raise StaticModError("output must be an explicit .zip file")
    if dest == base or base in dest.parents:
        raise StaticModError("do not write into the installable mod")
    if dest.is_symlink() or dest.exists():
        raise StaticModError("existing output refused: no overwrite")
    # Deterministic timestamps and entry order yield byte-identical archives.
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        with zipfile.ZipFile(dest, "x") as z:
            for item in sorted(FILES):
                data = (base / item).read_bytes()
                member = zipfile.ZipInfo("AI-Core-Field-Triage/" + item, date_time=(1980, 1, 1, 0, 0, 0))
                member.compress_type = zipfile.ZIP_DEFLATED
                member.external_attr = 0o100644 << 16
                z.writestr(member, data)
    except Exception:
        dest.unlink(missing_ok=True)
        raise
    report["zip_path"] = str(dest)
    report["zip_sha256"] = hashlib.sha256(dest.read_bytes()).hexdigest()
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT)
    parser.add_argument("--out", type=Path, help="explicit path for immutable install zip")
    args = parser.parse_args(argv)
    try:
        report = package(args.root, args.out) if args.out else verify(args.root)
    except (OSError, StaticModError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
