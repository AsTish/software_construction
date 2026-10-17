from abc import ABC, abstractmethod
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from .errors import InvalidPackageError, PackageNotFoundError


class PackageSource(ABC):
    @abstractmethod
    def read_text(self, name: str, encoding: str = "utf-8-sig") -> str:
        """Прочитать текстовый файл из корня пакета."""

    @abstractmethod
    def file_names(self) -> tuple[str, ...]:
        """Вернуть имена файлов, расположенных в пакете."""


class DirectoryPackageSource(PackageSource):
    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def read_text(self, name: str, encoding: str = "utf-8-sig") -> str:
        try:
            return (self._directory / name).read_text(encoding=encoding)
        except FileNotFoundError as error:
            raise InvalidPackageError(f"В пакете отсутствует обязательный файл: {name}") from error
        except UnicodeDecodeError as error:
            raise InvalidPackageError(f"Файл {name} должен быть в UTF-8.") from error

    def file_names(self) -> tuple[str, ...]:
        return tuple(item.relative_to(self._directory).as_posix() for item in self._directory.rglob("*") if item.is_file())


class ZipPackageSource(PackageSource):
    def __init__(self, archive: Path) -> None:
        self._archive = archive

    def read_text(self, name: str, encoding: str = "utf-8-sig") -> str:
        try:
            with ZipFile(self._archive) as package:
                match = name if name in package.namelist() else next(
                    (item for item in package.namelist() if item.rstrip("/").endswith(f"/{name}")), None
                )
                if match is None:
                    raise InvalidPackageError(f"В пакете отсутствует обязательный файл: {name}")
                return package.read(match).decode(encoding)
        except BadZipFile as error:
            raise InvalidPackageError("Указанный файл не является корректным ZIP-архивом.") from error
        except UnicodeDecodeError as error:
            raise InvalidPackageError(f"Файл {name} должен быть в UTF-8.") from error

    def file_names(self) -> tuple[str, ...]:
        try:
            with ZipFile(self._archive) as package:
                return tuple(item for item in package.namelist() if not item.endswith("/"))
        except BadZipFile as error:
            raise InvalidPackageError("Указанный файл не является корректным ZIP-архивом.") from error


def open_package_source(path: Path) -> PackageSource:
    if not path.exists():
        raise PackageNotFoundError(f"Пакет не найден: {path}")
    if path.is_dir():
        return DirectoryPackageSource(path)
    if path.is_file() and path.suffix.lower() == ".zip":
        return ZipPackageSource(path)
    raise PackageNotFoundError(f"Ожидался каталог или ZIP-архив: {path}")
