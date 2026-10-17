from pathlib import Path

from .errors import UnsupportedFormatError
from .parser import KrsuPackageParser
from .presentation import KrsuReportFormatter
from .source import open_package_source
from cats_parser import CatsPackageParser, CatsReportFormatter
from ejudge_parser import EjudgePackageParser, EjudgeReportFormatter
from pcms2_parser import Pcms2PackageParser, Pcms2ReportFormatter


class ParsePackageUseCase:
    def __init__(self, parser: KrsuPackageParser, formatter: KrsuReportFormatter) -> None:
        self._parser, self._formatter = parser, formatter

    def execute(self, format_name: str, package_path: Path) -> str:
        if format_name.upper() == "KRSU":
            if package_path.is_file() and package_path.name.lower() != "testinfo.xml":
                raise UnsupportedFormatError("Для KRSU укажите testinfo.xml, каталог пакета или ZIP-архив.")
            source = open_package_source(package_path.parent) if package_path.is_file() else open_package_source(package_path)
            return self._formatter.format(self._parser.parse(source))
        if format_name.upper() == "CATS":
            if package_path.is_file() and package_path.suffix.lower() != ".xml":
                raise UnsupportedFormatError("Для CATS укажите XML-файл описания, каталог пакета или ZIP-архив.")
            source = open_package_source(package_path.parent) if package_path.is_file() else open_package_source(package_path)
            descriptor = package_path.name if package_path.is_file() else None
            return CatsReportFormatter().format(CatsPackageParser().parse(source, descriptor))
        if format_name.upper() == "EJUDGE":
            if not package_path.is_file() or package_path.name.lower() != "problem.cfg":
                raise UnsupportedFormatError("Для EJUDGE укажите файл problem.cfg.")
            source = open_package_source(package_path.parent)
            return EjudgeReportFormatter().format(EjudgePackageParser().parse(source))
        if format_name.upper() == "PCMS2":
            if not package_path.is_file() or package_path.name.lower() != "problem.xml":
                raise UnsupportedFormatError("Для PCMS2 укажите файл problem.xml.")
            source = open_package_source(package_path.parent)
            return Pcms2ReportFormatter().format(Pcms2PackageParser().parse(source))
        raise UnsupportedFormatError(f"Поддерживаются KRSU, CATS, EJUDGE и PCMS2, получено: {format_name}")
