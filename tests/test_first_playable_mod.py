"""Synthetic, offline proofs for the installable RimWorld 1.6 data-only mod.

No RimWorld installation, Steam app, DLL, saves or network are ever accessed.
"""
from __future__ import annotations

import hashlib
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from tools.verify_first_slice import FILES, PROJECT, REL, StaticModError, package, verify


class FirstPlayableModTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "checkout"
        self.mod = self.root / REL
        self.mod.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(PROJECT / REL, self.mod)

    def rewrite(self, relative: str, change):
        path = self.mod / relative
        doc = ET.parse(path)
        change(doc.getroot())
        doc.write(path, encoding="utf-8", xml_declaration=True)

    def test_real_recipe_bills_have_visible_material_and_work_cost(self):
        result = verify(self.root)
        self.assertEqual(result["status"], "STATIC_VALIDATED_GAME_UNVERIFIED")
        self.assertEqual(result["recipe_count"], 2)
        self.assertEqual(result["research_count"], 1)
        self.assertEqual(
            result["resources"]["KiloAI_PrepareFieldDressing"],
            {"cloth_spent": 16, "medicine_spent": 1, "medicine_produced": 2, "net_medicine": 1},
        )
        self.assertEqual(
            result["resources"]["KiloAI_BulkFieldDressings"],
            {"cloth_spent": 40, "medicine_spent": 3, "medicine_produced": 6, "net_medicine": 3},
        )
        self.assertEqual(result["actual_rimworld_def_loading"], "UNVERIFIED")
        self.assertEqual(result["actual_player_bill_creation"], "UNVERIFIED")

    def test_package_is_reproducible_and_contains_no_legacy_broken_defs_or_fake_dll(self):
        a, b = [Path(self.tmp.name) / f"release-{i}.zip" for i in (1, 2)]
        first = package(self.root, a)
        second = package(self.root, b)
        self.assertEqual(first["zip_sha256"], second["zip_sha256"])
        self.assertEqual(hashlib.sha256(a.read_bytes()).hexdigest(), first["zip_sha256"])
        with zipfile.ZipFile(a) as archive:
            self.assertEqual(
                archive.namelist(),
                sorted("AI-Core-Field-Triage/" + f for f in FILES),
            )
            self.assertTrue(all(name.endswith(".xml") for name in archive.namelist()))
            self.assertFalse(any("Assemblies" in p or "/Def/" in p for p in archive.namelist()))

    def test_existing_output_never_overwritten(self):
        dest = Path(self.tmp.name) / "release.zip"
        dest.write_bytes(b"valuable release")
        with self.assertRaisesRegex(StaticModError, "existing output refused"):
            package(self.root, dest)
        self.assertEqual(dest.read_bytes(), b"valuable release")

    def test_output_must_not_write_back_into_playable_mod(self):
        with self.assertRaisesRegex(StaticModError, "do not write"):
            package(self.root, self.mod / "nested.zip")

    def test_missing_and_extra_files_fail_closed(self):
        (self.mod / FILES[2]).unlink()
        with self.assertRaisesRegex(StaticModError, "unexpected or missing"):
            verify(self.root)
        shutil.copy2(PROJECT / REL / FILES[2], self.mod / FILES[2])
        (self.mod / "Assemblies").mkdir()
        (self.mod / "Assemblies" / "Fake.dll").write_bytes(b"not a DLL")
        with self.assertRaisesRegex(StaticModError, "unexpected or missing"):
            verify(self.root)

    def test_symlinks_are_never_packaged_even_if_they_look_like_xml(self):
        target = self.mod / FILES[0]
        other = Path(self.tmp.name) / "other.xml"
        other.write_bytes(target.read_bytes())
        target.unlink()
        try:
            target.symlink_to(other)
        except (OSError, NotImplementedError):
            self.skipTest("local filesystem cannot create symlinks")
        with self.assertRaisesRegex(StaticModError, "symlink"):
            verify(self.root)

    def test_malformed_xml_never_called_a_loadable_mod(self):
        target = self.mod / FILES[1]
        target.write_text("<Defs><RecipeDef>", encoding="utf-8")
        with self.assertRaisesRegex(StaticModError, "invalid XML"):
            verify(self.root)

    def test_wrong_version_is_not_silently_advertised(self):
        def change(root):
            root.find("supportedVersions/li").text = "1.7"
        self.rewrite("About/About.xml", change)
        with self.assertRaisesRegex(StaticModError, "target version 1.6"):
            verify(self.root)

    def test_duplicate_defname_refused_before_export(self):
        def change(root):
            root.findall("RecipeDef")[1].find("defName").text = "KiloAI_PrepareFieldDressing"
        self.rewrite("Defs/RecipeDefs/FieldDressings.xml", change)
        with self.assertRaisesRegex(StaticModError, "foreign or duplicate"):
            verify(self.root)

    def test_changed_product_quantity_rejected_as_unreviewed_resource_mint(self):
        def change(root):
            root.findall("RecipeDef")[0].find("products/MedicineHerbal").text = "200"
        self.rewrite("Defs/RecipeDefs/FieldDressings.xml", change)
        with self.assertRaisesRegex(StaticModError, "medicine output"):
            verify(self.root)

    def test_unknown_ingredient_cannot_bypass_existing_vanilla_def(self):
        def change(root):
            root.findall("RecipeDef")[0].find("ingredients/li/filter/thingDefs/li").text = "ImaginaryPotion"
        self.rewrite("Defs/RecipeDefs/FieldDressings.xml", change)
        with self.assertRaisesRegex(StaticModError, "unknown ingredient"):
            verify(self.root)

    def test_ingredient_filter_may_not_accidentally_accept_all_colony_resources(self):
        def change(root):
            root.findall("RecipeDef")[0].remove(root.findall("RecipeDef")[0].find("fixedIngredientFilter"))
        self.rewrite("Defs/RecipeDefs/FieldDressings.xml", change)
        with self.assertRaisesRegex(StaticModError, "ingredient selector"):
            verify(self.root)

    def test_research_unlock_cannot_be_removed_by_unreviewed_edit(self):
        def change(root):
            recipe = root.findall("RecipeDef")[1]
            recipe.remove(recipe.find("researchPrerequisite"))
        self.rewrite("Defs/RecipeDefs/FieldDressings.xml", change)
        with self.assertRaisesRegex(StaticModError, "research gate"):
            verify(self.root)

    def test_canonical_research_cannot_duplicate_external_vanilla_def(self):
        def change(root):
            root.find("ResearchProjectDef/defName").text = "MicroelectronicsBasics"
        self.rewrite("Defs/ResearchProjectDefs/FieldTriage.xml", change)
        with self.assertRaisesRegex(StaticModError, "unexpected research def"):
            verify(self.root)


if __name__ == "__main__":
    unittest.main()
