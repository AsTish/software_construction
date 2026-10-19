from abc import ABC, abstractmethod
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from .errors import InvalidPackageError, PackageNotFoundError


class PackageSource(ABC):
    @abstractmethod
    def read_text(self, name: str, encoding: str = "utf-8-sig") -> str:
        """Read a text file relative to the package root."""

    @abstractmethod
    def file_names(self) -> tuple[str, ...]:
        """Return all file names relative to the package root."""


class ScopedPackageSource(PackageSource):
    """A view of a directory inside an archive or a package directory."""

    def __init__(self, source: PackageSource, prefix: str) -> None:
        self._source = source
        self._prefix = prefix.strip("/")
        self._prefix_with_separator = f"{self._prefix}/" if self._prefix else ""

    def read_text(self, name: str, encoding: str = "utf-8-sig") -> str:
        return self._source.read_text(f"{self._prefix_with_separator}{name}", encoding)

    def file_names(self) -> tuple[str, ...]:
        return tuple(
            name[len(self._prefix_with_separator):]
            for name in self._source.file_names()
            if name.startswith(self._prefix_with_separator)
        )


class DirectoryPackageSource(PackageSource):
    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def read_text(self, name: str, encoding: str = "utf-8-sig") -> str:
        try:
            return (self._directory / name).read_text(encoding=encoding)
        except FileNotFoundError as error:
            raise InvalidPackageError(f"Required file is missing: {name}") from error
        except UnicodeDecodeError as error:
            raise InvalidPackageError(f"File is not encoded as {encoding}: {name}") from error

    def file_names(self) -> tuple[str, ...]:
        return tuple(item.relative_to(self._directory).as_posix() for item in self._directory.rglob("*") if item.is_file())


class ZipPackageSource(PackageSource):
    def __init__(self, archive: Path) -> None:
        self._archive = archive

    def read_text(self, name: str, encoding: str = "utf-8-sig") -> str:
        try:
            with ZipFile(self._archive) as package:
                if name not in package.namelist():
                    raise InvalidPackageError(f"Required file is missing: {name}")
                return package.read(name).decode(encoding)
        except BadZipFile as error:
            raise InvalidPackageError("The specified file is not a valid ZIP archive.") from error
        except UnicodeDecodeError as error:
            raise InvalidPackageError(f"File is not encoded as {encoding}: {name}") from error

    def file_names(self) -> tuple[str, ...]:
        try:
            with ZipFile(self._archive) as package:
                return tuple(item for item in package.namelist() if not item.endswith("/"))
        except BadZipFile as error:
            raise InvalidPackageError("The specified file is not a valid ZIP archive.") from error


def open_package_source(path: Path) -> PackageSource:
    if not path.exists():
        raise PackageNotFoundError(f"Package not found: {path}")
    if path.is_dir():
        return DirectoryPackageSource(path)
    if path.is_file() and path.suffix.lower() == ".zip":
        return ZipPackageSource(path)
    raise PackageNotFoundError(f"Expected a directory or ZIP archive: {path}")


def scope_package_source(source: PackageSource, prefix: str) -> PackageSource:
    return ScopedPackageSource(source, prefix) if prefix else source
