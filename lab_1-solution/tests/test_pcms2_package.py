"""Интеграционные тесты обоих учебных вариантов PCMS2."""

import unittest
from pathlib import Path

from krsu_parser.application import ParsePackageUseCase
from krsu_parser.parser import KrsuPackageParser
from krsu_parser.presentation import KrsuReportFormatter
from krsu_parser.source import open_package_source
from pcms2_parser import Pcms2PackageParser


class Pcms2PackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).parent / ".." / ".." / "lab_1-task" / "PCMS2"
        if not cls.root.is_dir():
            raise unittest.SkipTest("Пакеты PCMS2 не найдены.")

    def test_sample_variant(self) -> None:
        package = Pcms2PackageParser().parse(open_package_source(self.root / "sample"))
        attributes = dict(package.problem.attributes)
        self.assertEqual("1.0", attributes["version"])
        self.assertEqual("ru.olymp.roi.2016.day2.equivalence", attributes["id"])
        self.assertTrue(any(child.tag == "judging" for child in package.problem.children))

    def test_dungeon_variant(self) -> None:
        package = Pcms2PackageParser().parse(open_package_source(self.root / "dungeon"))
        self.assertEqual("dungeon", dict(package.problem.attributes)["short-name"])
        self.assertTrue(any(child.tag == "assets" for child in package.problem.children))
        self.assertTrue(any(child.tag == "documents" for child in package.problem.children))

    def test_cli_uses_problem_xml(self) -> None:
        report = ParsePackageUseCase(KrsuPackageParser(), KrsuReportFormatter()).execute(
            "PCMS2", self.root / "dungeon" / "problem.xml"
        )
        self.assertIn("Format: PCMS2", report)
        self.assertIn("testset", report)
        self.assertIn("solutions", report)
