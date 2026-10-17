"""Интеграционные проверки учебного пакета EJUDGE."""

import unittest
from pathlib import Path

from ejudge_parser import EjudgePackageParser
from krsu_parser.application import ParsePackageUseCase
from krsu_parser.parser import KrsuPackageParser
from krsu_parser.presentation import KrsuReportFormatter
from krsu_parser.source import open_package_source


class EjudgePackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.package = Path(__file__).parent / ".." / ".." / "lab_1-task" / "EJUDGE" / "sample"
        if not cls.package.is_dir():
            raise unittest.SkipTest("Пакет EJUDGE не найден.")

    def test_problem_and_valuer_configuration(self) -> None:
        package = EjudgePackageParser().parse(open_package_source(self.package))
        self.assertEqual("2", package.problem_option("time_limit"))
        self.assertEqual("512M", package.problem_option("max_vm_size"))
        self.assertEqual("reconstruct-bus-schedule", package.problem_option("internal_name"))
        self.assertEqual(5, len(package.groups))
        self.assertEqual("1-2", package.groups[0].option("tests"))
        self.assertEqual("3", package.groups[4].option("requires"))

    def test_cli_uses_problem_configuration_file(self) -> None:
        report = ParsePackageUseCase(KrsuPackageParser(), KrsuReportFormatter()).execute(
            "EJUDGE", self.package / "problem.cfg"
        )
        self.assertIn("Format: EJUDGE", report)
        self.assertIn("Groups: 5", report)
