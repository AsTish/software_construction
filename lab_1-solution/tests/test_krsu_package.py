"""Тесты используют реальную папку KRSU из материалов задания."""

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

from krsu_parser.application import ParsePackageUseCase
from krsu_parser.errors import InvalidPackageError
from krsu_parser.parser import KrsuPackageParser
from krsu_parser.presentation import KrsuReportFormatter
from krsu_parser.source import open_package_source


def krsu_directory() -> Path:
    configured = os.environ.get("KRSU_PACKAGE")
    if configured:
        return Path(configured)
    # Путь задан относительно директории tests:
    # tests/../../lab_1-task/KRSU.
    return (Path(__file__).parent / ".." / ".." / "lab_1-task" / "KRSU").resolve()


class KrsuPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.krsu = krsu_directory()
        if not cls.krsu.is_dir():
            raise unittest.SkipTest("Укажите KRSU_PACKAGE с путём к папке KRSU.")

    def test_root_krsu_folder(self) -> None:
        package = KrsuPackageParser().parse(open_package_source(self.krsu))
        self.assertEqual("checker.exe", package.checker)
        self.assertEqual("interactor.exe", package.interactor)
        self.assertEqual(268435456, package.memory_limit_bytes)
        self.assertEqual(1000, package.time_limit_milliseconds)
        self.assertEqual(3, len(package.groups))
        self.assertEqual(4, len(package.tests))
        self.assertEqual(("1", "2"), package.groups[2].prerequisites)

    def test_krsu_a_folder(self) -> None:
        package = KrsuPackageParser().parse(open_package_source(self.krsu / "A"))
        self.assertEqual(27, len(package.tests))
        self.assertEqual("input01.txt", package.tests[0].input_file)
        self.assertEqual("output27.txt", package.tests[-1].output_file)
        self.assertEqual(30, package.tests[-1].points)

    def test_krsu_zip(self) -> None:
        with TemporaryDirectory() as temporary:
            archive = Path(temporary) / "krsu.zip"
            with ZipFile(archive, "w", ZIP_DEFLATED) as file:
                file.write(self.krsu / "testinfo.xml", "testinfo.xml")
            package = KrsuPackageParser().parse(open_package_source(archive))
        self.assertEqual(4, len(package.tests))

    def test_report(self) -> None:
        report = ParsePackageUseCase(KrsuPackageParser(), KrsuReportFormatter()).execute("KRSU", self.krsu / "A")
        self.assertIn("Format: KRSU", report)
        self.assertIn("Tests: 27", report)

    def test_testinfo_file_can_be_passed_directly(self) -> None:
        report = ParsePackageUseCase(KrsuPackageParser(), KrsuReportFormatter()).execute(
            "KRSU", self.krsu / "A" / "testinfo.xml"
        )
        self.assertIn("Tests: 27", report)

    def test_other_format_xml_is_validated_by_its_parser(self) -> None:
        with self.assertRaises(InvalidPackageError):
            ParsePackageUseCase(KrsuPackageParser(), KrsuReportFormatter()).execute("PCMS2", self.krsu)

    def test_invalid_xml_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary:
            Path(temporary, "testinfo.xml").write_text("<testinfo>", encoding="utf-8")
            with self.assertRaises(InvalidPackageError):
                KrsuPackageParser().parse(open_package_source(Path(temporary)))
