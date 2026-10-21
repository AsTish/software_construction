from pathlib import Path

from cats_parser import CatsPackageParser, CatsReportFormatter
from ejudge_parser import EjudgePackageParser, EjudgeReportFormatter
from pcms2_parser import Pcms2PackageParser, Pcms2ReportFormatter

from .errors import UnsupportedFormatError
from .parser import KrsuPackageParser
from .presentation import KrsuReportFormatter
from .source import PackageSource, open_package_source, scope_package_source


class ParsePackageUseCase:
    """Find a package of the requested format and produce its report."""

    def __init__(self, parser: KrsuPackageParser, formatter: KrsuReportFormatter) -> None:
        self._parser, self._formatter = parser, formatter

    def execute(self, format_name: str, package_path: Path) -> str:
        format_name = format_name.upper()
        source, descriptor = self._find_format_package(format_name, package_path)
        if format_name == "KRSU":
            return self._formatter.format(self._parser.parse(source, descriptor))
        if format_name == "CATS":
            return CatsReportFormatter().format(CatsPackageParser().parse(source, descriptor))
        if format_name == "EJUDGE":
            return EjudgeReportFormatter().format(EjudgePackageParser().parse(source, descriptor))
        if format_name == "PCMS2":
            return Pcms2ReportFormatter().format(Pcms2PackageParser().parse(source, descriptor))
        raise UnsupportedFormatError(f"Supported formats: KRSU, CATS, EJUDGE, PCMS2; got: {format_name}")

    @staticmethod
    def _find_format_package(format_name: str, package_path: Path) -> tuple[PackageSource, str]:
        if format_name not in {"KRSU", "CATS", "EJUDGE", "PCMS2"}:
            raise UnsupportedFormatError(f"Supported formats: KRSU, CATS, EJUDGE, PCMS2; got: {format_name}")

        # Direct descriptor paths remain supported for convenience.
        if package_path.is_file() and package_path.suffix.lower() != ".zip":
            return open_package_source(package_path.parent), package_path.name

        source = open_package_source(package_path)
        names = source.file_names()
        extension = ".cfg" if format_name == "EJUDGE" else ".xml"
        candidates = [name for name in names if name.lower().endswith(extension)]

        # The format folder, when present, identifies the package.  Without it,
        # use the first descriptor found in the archive/directory.
        in_format_folder = [
            name for name in candidates
            if format_name.lower() in {part.lower() for part in name.split("/")[:-1]}
        ]
        descriptor_path = (in_format_folder or candidates)[0] if (in_format_folder or candidates) else None
        if descriptor_path is None:
            raise UnsupportedFormatError(
                f"Could not find a {extension} descriptor for {format_name}."
            )
        prefix = descriptor_path.rsplit("/", 1)[0] if "/" in descriptor_path else ""
        return scope_package_source(source, prefix), descriptor_path.rsplit("/", 1)[-1]
