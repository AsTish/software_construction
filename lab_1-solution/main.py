import argparse
import sys
from pathlib import Path

from krsu_parser.application import ParsePackageUseCase
from krsu_parser.errors import PackageError
from krsu_parser.parser import KrsuPackageParser
from krsu_parser.presentation import KrsuReportFormatter


def main(argv: list[str] | None = None) -> int:
    arguments = argparse.ArgumentParser(description="Парсер пакетов KRSU.")
    arguments.add_argument("format", help="Поддерживаются KRSU, CATS, EJUDGE и PCMS2")
    arguments.add_argument("package", type=Path, help="Каталог пакета или ZIP-архив")
    parsed = arguments.parse_args(argv)
    try:
        print(ParsePackageUseCase(KrsuPackageParser(), KrsuReportFormatter()).execute(parsed.format, parsed.package))
    except PackageError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
