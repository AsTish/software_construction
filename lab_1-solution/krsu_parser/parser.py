from xml.etree import ElementTree

from .domain import KrsuPackage, TestCase, TestGroup
from .errors import InvalidPackageError
from .source import PackageSource


class KrsuPackageParser:
    """Преобразует обязательный testinfo.xml в предметную модель."""

    def parse(self, source: PackageSource) -> KrsuPackage:
        try:
            root = ElementTree.fromstring(source.read_text("testinfo.xml"))
        except ElementTree.ParseError as error:
            raise InvalidPackageError("Файл testinfo.xml содержит некорректный XML.") from error
        if root.tag != "testinfo":
            raise InvalidPackageError("Корневым элементом должен быть <testinfo>.")
        groups = tuple(self._group(item) for item in root.findall("group"))
        tests = tuple(self._test(item) for item in root.findall("test"))
        known_groups = {group.identifier for group in groups}
        for test in tests:
            if test.group_id is not None and test.group_id not in known_groups:
                raise InvalidPackageError(f"Тест ссылается на несуществующую группу {test.group_id!r}.")
        return KrsuPackage(self._text(root, "checker"), self._text(root, "interactor"),
            self._text(root, "problem"), self._number(root, "memorylimit"),
            self._number(root, "timelimit"), self._text(root, "testversion"),
            self._number(root, "runtype"), groups, tests)

    def _group(self, element: ElementTree.Element) -> TestGroup:
        prereq = tuple(x.strip() for x in element.get("prereq", "").split(",") if x.strip())
        return TestGroup(self._attribute(element, "id"), self._integer(self._attribute(element, "points"), "group.points"), prereq)

    def _test(self, element: ElementTree.Element) -> TestCase:
        points = element.get("points")
        return TestCase(self._attribute(element, "input"), self._attribute(element, "output"),
            self._integer(points, "test.points") if points is not None else None, element.get("groupid"))

    @staticmethod
    def _text(root: ElementTree.Element, tag: str) -> str | None:
        node = root.find(tag)
        return node.text.strip() if node is not None and node.text else None

    def _number(self, root: ElementTree.Element, tag: str) -> int | None:
        value = self._text(root, tag)
        return self._integer(value, tag) if value is not None else None

    @staticmethod
    def _attribute(element: ElementTree.Element, name: str) -> str:
        value = element.get(name)
        if value is None or not value.strip():
            raise InvalidPackageError(f"Элемент <{element.tag}> не содержит атрибут {name!r}.")
        return value.strip()

    @staticmethod
    def _integer(value: str, field: str) -> int:
        try:
            return int(value)
        except ValueError as error:
            raise InvalidPackageError(f"Поле {field} должно быть целым числом.") from error
