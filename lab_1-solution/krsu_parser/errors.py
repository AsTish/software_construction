class PackageError(Exception):
    """Базовая ошибка пакета KRSU."""


class UnsupportedFormatError(PackageError):
    pass


class PackageNotFoundError(PackageError):
    pass


class InvalidPackageError(PackageError):
    pass
