# Лабораторная работа №1 — парсер пакетов задач

Программа разбирает ZIP-пакеты олимпиадных задач форматов `KRSU`, `CATS`,
`EJUDGE` и `PCMS2`.

## Запуск

Поддерживаются два равнозначных варианта с одним интерфейсом:

```text
Program.exe [FORMAT] [PACKAGE]
python main.py [FORMAT] [PACKAGE]
```

`FORMAT` — `KRSU`, `CATS`, `EJUDGE` или `PCMS2`.
`PACKAGE` — путь к ZIP-архиву либо к распакованной папке пакета.

Примеры:

```powershell
.\dist\Program.exe CATS "D:\me\projects\uni\7 sem\software_construction\5295.ZIP"
python main.py KRSU "D:\me\projects\uni\7 sem\software_construction\5295.ZIP"
python main.py EJUDGE "D:\me\projects\uni\7 sem\software_construction\5295.ZIP"
```

При поиске описания приоритет имеет папка с именем выбранного формата:
например, при `CATS` — `CATS/`. Из неё выбирается первый XML-файл; для
`EJUDGE` — первый CFG-файл. Если такой папки нет, берётся первый XML-файл во
всём архиве (или первый CFG-файл для `EJUDGE`). Поэтому имена XML-файлов не
обязаны быть `testinfo.xml` или `problem.xml`.

Готовый исполняемый файл находится в `dist/Program.exe`.

## Повторная сборка EXE

Нужны Python 3.10+ и PyInstaller:

```powershell
python -m pip install pyinstaller
.\build_exe.bat
```

## Проверка

```powershell
python -m unittest discover -s tests -v
```
