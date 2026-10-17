from dataclasses import dataclass


@dataclass(frozen=True)
class TestGroup:
    identifier: str
    points: int
    prerequisites: tuple[str, ...]


@dataclass(frozen=True)
class TestCase:
    input_file: str
    output_file: str
    points: int | None
    group_id: str | None


@dataclass(frozen=True)
class KrsuPackage:
    checker: str | None
    interactor: str | None
    problem: str | None
    memory_limit_bytes: int | None
    time_limit_milliseconds: int | None
    test_version: str | None
    run_type: int | None
    groups: tuple[TestGroup, ...]
    tests: tuple[TestCase, ...]
