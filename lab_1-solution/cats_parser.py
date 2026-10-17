"""Полный структурный разбор XML-описания пакета CATS."""

from __future__ import annotations

from dataclasses import dataclass
import re
from xml.etree import ElementTree

from krsu_parser.errors import InvalidPackageError
from krsu_parser.source import PackageSource


@dataclass(frozen=True)
class CatsElement:
    """Любой элемент CATS, включая неизвестные будущие элементы формата."""

    tag: str
    attributes: tuple[tuple[str, str], ...]
    text: str | None
    tail: str | None
    children: tuple["CatsElement", ...]

    @classmethod
    def from_xml(cls, element: ElementTree.Element) -> "CatsElement":
        text = " ".join((element.text or "").split()) or None
        return cls(
            tag=element.tag,
            attributes=tuple(sorted(element.attrib.items())),
            text=text,
            tail=" ".join((element.tail or "").split()) or None,
            children=tuple(cls.from_xml(child) for child in element),
        )


@dataclass(frozen=True)
class CatsPackage:
    descriptor: str
    version: str | None
    problem: CatsElement

    @property
    def title(self) -> str:
        return dict(self.problem.attributes)["title"]

    def attribute(self, name: str) -> str | None:
        return dict(self.problem.attributes).get(name)

    def elements(self, tag: str) -> tuple[CatsElement, ...]:
        return tuple(item for item in self.problem.children if item.tag == tag)


class CatsPackageParser:
    """Читает весь XML CATS, не отбрасывая элементы или атрибуты спецификации."""

    def parse(self, source: PackageSource, descriptor: str | None = None) -> CatsPackage:
        candidates = [name for name in source.file_names() if name.lower().endswith(".xml")]
        if descriptor is not None:
            if descriptor not in candidates:
                raise InvalidPackageError(f"XML-файл CATS не найден: {descriptor}")
            candidates = [descriptor]
        if len(candidates) != 1:
            raise InvalidPackageError("Пакет CATS должен содержать ровно один XML-файл описания.")

        descriptor = candidates[0]
        try:
            try:
                xml = source.read_text(descriptor, encoding="utf-8-sig")
            except InvalidPackageError:
                xml = source.read_text(descriptor, encoding="cp1251")
            # После декодирования строка уже Unicode. Удаляем декларацию,
            # чтобы некорректная декларация кодировки в старом пакете не
            # заставила XML-парсер повторно интерпретировать символы.
            root = ElementTree.fromstring(re.sub(r"^\s*<\?xml[^>]*\?>", "", xml, count=1))
        except ElementTree.ParseError as error:
            raise InvalidPackageError("XML-описание CATS некорректно.") from error

        problem = root.find("Problem") if root.tag == "CATS" else None
        if problem is None:
            raise InvalidPackageError("Ожидалась структура <CATS><Problem>.")
        if not problem.get("title"):
            raise InvalidPackageError("Элемент <Problem> должен содержать атрибут title.")
        return CatsPackage(descriptor, root.get("version"), CatsElement.from_xml(problem))


class CatsReportFormatter:
    """Выводит все разделы XML CATS в читаемом и детерминированном виде."""

    def format(self, package: CatsPackage) -> str:
        lines = ["Format: CATS", f"Descriptor: {package.descriptor}"]
        if package.version is not None:
            lines.append(f"Version: {package.version}")
        self._write_element(package.problem, lines, 0)
        return "\n".join(lines)

    def _write_element(self, element: CatsElement, lines: list[str], depth: int) -> None:
        indent = "  " * depth
        attributes = " ".join(f'{name}="{value}"' for name, value in element.attributes)
        label = f"{indent}{element.tag}" + (f" [{attributes}]" if attributes else "")
        if element.text:
            label += f": {element.text}"
        lines.append(label)
        for child in element.children:
            self._write_element(child, lines, depth + 1)
            if child.tail:
                lines.append(f"{indent}  text: {child.tail}")
