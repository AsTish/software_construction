"""Структурный парсер XML-пакетов PCMS2."""

from __future__ import annotations

from dataclasses import dataclass
import re
from xml.etree import ElementTree

from krsu_parser.errors import InvalidPackageError
from krsu_parser.source import PackageSource


@dataclass(frozen=True)
class Pcms2Element:
    tag: str
    attributes: tuple[tuple[str, str], ...]
    text: str | None
    tail: str | None
    children: tuple["Pcms2Element", ...]

    @classmethod
    def from_xml(cls, element: ElementTree.Element) -> "Pcms2Element":
        return cls(
            element.tag,
            tuple(sorted(element.attrib.items())),
            " ".join((element.text or "").split()) or None,
            " ".join((element.tail or "").split()) or None,
            tuple(cls.from_xml(child) for child in element),
        )


@dataclass(frozen=True)
class Pcms2Package:
    descriptor: str
    problem: Pcms2Element


class Pcms2PackageParser:
    def parse(self, source: PackageSource, descriptor: str = "problem.xml") -> Pcms2Package:
        if descriptor not in source.file_names():
            raise InvalidPackageError(f"Файл problem.xml не найден: {descriptor}")
        try:
            xml = source.read_text(descriptor, encoding="utf-8-sig")
            root = ElementTree.fromstring(re.sub(r"^\s*<\?xml[^>]*\?>", "", xml, count=1))
        except ElementTree.ParseError as error:
            raise InvalidPackageError("Файл problem.xml содержит некорректный XML.") from error
        if root.tag != "problem":
            raise InvalidPackageError("Корневым элементом PCMS2 должен быть <problem>.")
        return Pcms2Package(descriptor, Pcms2Element.from_xml(root))


class Pcms2ReportFormatter:
    def format(self, package: Pcms2Package) -> str:
        lines = ["Format: PCMS2", f"Descriptor: {package.descriptor}"]
        self._write(package.problem, lines, 0)
        return "\n".join(lines)

    def _write(self, element: Pcms2Element, lines: list[str], depth: int) -> None:
        indent = "  " * depth
        attributes = " ".join(f'{key}="{value}"' for key, value in element.attributes)
        line = f"{indent}{element.tag}" + (f" [{attributes}]" if attributes else "")
        if element.text:
            line += f": {element.text}"
        lines.append(line)
        for child in element.children:
            self._write(child, lines, depth + 1)
            if child.tail:
                lines.append(f"{indent}  text: {child.tail}")
