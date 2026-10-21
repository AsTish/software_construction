import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

from krsu_parser.application import ParsePackageUseCase
from krsu_parser.parser import KrsuPackageParser
from krsu_parser.presentation import KrsuReportFormatter


class PackageDiscoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.use_case = ParsePackageUseCase(KrsuPackageParser(), KrsuReportFormatter())

    def test_uses_an_arbitrarily_named_xml_at_archive_root(self) -> None:
        with TemporaryDirectory() as temporary:
            archive = Path(temporary) / "package.zip"
            with ZipFile(archive, "w", ZIP_DEFLATED) as file:
                file.writestr("descriptor.xml", "<testinfo><checker>check</checker></testinfo>")

            report = self.use_case.execute("KRSU", archive)

        self.assertIn("Checker: check", report)

    def test_prefers_xml_inside_the_format_folder(self) -> None:
        with TemporaryDirectory() as temporary:
            archive = Path(temporary) / "package.zip"
            with ZipFile(archive, "w", ZIP_DEFLATED) as file:
                file.writestr("other.xml", "<not-a-package />")
                file.writestr("KRSU/custom-name.xml", "<testinfo><checker>check</checker></testinfo>")

            report = self.use_case.execute("KRSU", archive)

        self.assertIn("Checker: check", report)
