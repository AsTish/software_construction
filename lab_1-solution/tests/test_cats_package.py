"""Интеграционные тесты на реальном пакете CATS из задания."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

from cats_parser import CatsPackageParser
from krsu_parser.application import ParsePackageUseCase
from krsu_parser.parser import KrsuPackageParser
from krsu_parser.presentation import KrsuReportFormatter
from krsu_parser.source import open_package_source


class CatsPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cats = Path(__file__).parent / ".." / ".." / "lab_1-task" / "CATS"
        if not cls.cats.is_dir():
            raise unittest.SkipTest("Папка CATS не найдена.")

    def test_cats_folder(self) -> None:
        package = CatsPackageParser().parse(open_package_source(self.cats))
        self.assertEqual("Area 51", package.title)
        self.assertEqual("1.4", package.version)
        self.assertEqual("2", package.attribute("tlimit"))
        self.assertEqual("64", package.attribute("mlimit"))
        self.assertEqual("area.in", package.attribute("inputFile"))
        self.assertEqual("check.dpr", dict(package.elements("Checker")[0].attributes)["src"])
        self.assertEqual(1, len(package.elements("TestRange")))
        test_range = dict(package.elements("TestRange")[0].attributes)
        self.assertEqual(("1", "42"), (test_range["from"], test_range["to"]))

    def test_cats_zip(self) -> None:
        with TemporaryDirectory() as temporary:
            archive = Path(temporary) / "cats.zip"
            with ZipFile(archive, "w", ZIP_DEFLATED) as file:
                file.write(self.cats / "area51.xml", "area51.xml")
            package = CatsPackageParser().parse(open_package_source(archive))
        self.assertEqual("Area 51", package.title)

    def test_cli_scenario(self) -> None:
        report = ParsePackageUseCase(KrsuPackageParser(), KrsuReportFormatter()).execute(
            "CATS", self.cats / "area51.xml"
        )
        self.assertIn("Format: CATS", report)
        self.assertIn('Problem [author="NEERC 2005"', report)
        self.assertIn("ProblemStatement", report)
        self.assertIn("Sample [rank=\"1\"]", report)
        self.assertIn("Solution [name=\"sol\" src=\"area_al.dpr\"]", report)
