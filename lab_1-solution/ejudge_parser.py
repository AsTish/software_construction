"""Разбор файлов problem.cfg и valuer.cfg формата EJUDGE."""

from __future__ import annotations

from dataclasses import dataclass
import re

from krsu_parser.errors import InvalidPackageError
from krsu_parser.source import PackageSource


@dataclass(frozen=True)
class EjudgeGroup:
    identifier: int
    options: tuple[tuple[str, str | None], ...]

    def option(self, name: str) -> str | None:
        return dict(self.options).get(name)


@dataclass(frozen=True)
class EjudgePackage:
    problem_options: tuple[tuple[str, str], ...]
    global_options: tuple[tuple[str, str | None], ...]
    groups: tuple[EjudgeGroup, ...]

    def problem_option(self, name: str) -> str | None:
        return dict(self.problem_options).get(name)


class EjudgePackageParser:
    def parse(self, source: PackageSource, problem_descriptor: str = "problem.cfg") -> EjudgePackage:
        if problem_descriptor not in source.file_names():
            raise InvalidPackageError(f"Файл problem.cfg не найден: {problem_descriptor}")
        problem_options = self._parse_problem(source.read_text(problem_descriptor))
        valuer_name = self._sibling(problem_descriptor, "valuer.cfg")
        if valuer_name not in source.file_names():
            raise InvalidPackageError("В пакете EJUDGE отсутствует valuer.cfg.")
        global_options, groups = self._parse_valuer(source.read_text(valuer_name))
        return EjudgePackage(tuple(problem_options.items()), global_options, groups)

    @staticmethod
    def _sibling(path: str, name: str) -> str:
        return f"{path.rsplit('/', 1)[0]}/{name}" if "/" in path else name

    @staticmethod
    def _without_comments(text: str) -> str:
        return "\n".join(line.split("#", 1)[0].split("//", 1)[0] for line in text.splitlines())

    def _parse_problem(self, text: str) -> dict[str, str]:
        cleaned = self._without_comments(text)
        section = re.search(r"\[problem\](.*)", cleaned, re.IGNORECASE | re.DOTALL)
        if section is None:
            raise InvalidPackageError("В problem.cfg отсутствует раздел [problem].")
        options: dict[str, str] = {}
        for line in section.group(1).splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            key, value = key.strip(), value.strip().strip('"')
            if key:
                options[key] = value
        return options

    def _parse_valuer(self, text: str) -> tuple[tuple[tuple[str, str | None], ...], tuple[EjudgeGroup, ...]]:
        cleaned = self._without_comments(text)
        blocks = re.findall(r"\b(global|group\s+\d+)\s*\{(.*?)\}", cleaned, re.DOTALL)
        global_options: tuple[tuple[str, str | None], ...] = ()
        groups: list[EjudgeGroup] = []
        for header, body in blocks:
            options = self._parse_options(body)
            if header == "global":
                global_options = options
            else:
                groups.append(EjudgeGroup(int(header.split()[1]), options))
        return global_options, tuple(groups)

    @staticmethod
    def _parse_options(body: str) -> tuple[tuple[str, str | None], ...]:
        parsed: list[tuple[str, str | None]] = []
        for statement in body.split(";"):
            tokens = statement.split()
            if tokens:
                parsed.append((tokens[0], " ".join(tokens[1:]) or None))
        return tuple(parsed)


class EjudgeReportFormatter:
    def format(self, package: EjudgePackage) -> str:
        lines = ["Format: EJUDGE", "Problem options:"]
        lines.extend(f"  {key} = {value}" for key, value in package.problem_options)
        if package.global_options:
            lines.append("Global options:")
            lines.extend(f"  {key}{' ' + value if value else ''}" for key, value in package.global_options)
        lines.append(f"Groups: {len(package.groups)}")
        for group in package.groups:
            lines.append(f"  Group {group.identifier}:")
            lines.extend(f"    {key}{' ' + value if value else ''}" for key, value in group.options)
        return "\n".join(lines)
