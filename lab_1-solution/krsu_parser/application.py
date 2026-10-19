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
        source = self._find_format_package(format_name, package_path)
        if format_name == "KRSU":
            return self._formatter.format(self._parser.parse(source))
        if format_name == "CATS":
            return CatsReportFormatter().format(CatsPackageParser().parse(source))
        if format_name == "EJUDGE":
            return EjudgeReportFormatter().format(EjudgePackageParser().parse(source))
        if format_name == "PCMS2":
            return Pcms2ReportFormatter().format(Pcms2PackageParser().parse(source))
        raise UnsupportedFormatError(f"Supported formats: KRSU, CATS, EJUDGE, PCMS2; got: {format_name}")

    @staticmethod
    def _find_format_package(format_name: str, package_path: Path) -> PackageSource:
        descriptors = {"KRSU": "testinfo.xml", "EJUDGE": "problem.cfg", "PCMS2": "problem.xml"}
        if format_name not in {*descriptors, "CATS"}:
            raise UnsupportedFormatError(f"Supported formats: KRSU, CATS, EJUDGE, PCMS2; got: {format_name}")

        # Direct descriptor paths remain supported for convenience.
        if package_path.is_file() and package_path.suffix.lower() != ".zip":
            return open_package_source(package_path.parent)

        source = open_package_source(package_path)
        names = source.file_names()
        if format_name == "CATS":
            candidates = [name for name in names if name.lower().endswith(".xml")]
        else:
            descriptor = descriptors[format_name]
            candidates = [name for name in names if name.rsplit("/", 1)[-1].lower() == descriptor]

        # A teaching archive can contain all formats. Prefer CATS/, KRSU/ etc.
        in_format_folder = [
            name for name in candidates
            if format_name.lower() in {part.lower() for part in name.split("/")[:-1]}
        ]
        if in_format_folder:
            candidates = in_format_folder

        def depth_below_format(name: str) -> int:
            parts = name.split("/")[:-1]
            positions = [index for index, part in enumerate(parts) if part.lower() == format_name.lower()]
            return len(parts) - positions[-1] - 1 if positions else len(parts)

        if candidates:
            nearest = min(depth_below_format(name) for name in candidates)
            candidates = [name for name in candidates if depth_below_format(name) == nearest]

        if len(candidates) != 1:
            expected = "an XML descriptor" if format_name == "CATS" else descriptors[format_name]
            found = ", ".join(candidates) or "none"
            raise UnsupportedFormatError(
                f"Could not determine one {format_name} package by {expected}; found: {found}."
            )

        descriptor_path = candidates[0]
        prefix = descriptor_path.rsplit("/", 1)[0] if "/" in descriptor_path else ""
        return scope_package_source(source, prefix)
