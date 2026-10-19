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

Если архив содержит несколько форматов, программа ищет описание в папке с
именем выбранного формата: например, при `CATS` — внутри `CATS/`. Если внутри
одной такой папки лежат несколько самостоятельных пакетов, программа сообщает
об этом, а не выбирает один случайно. Тогда передайте ZIP одного пакета или его
распакованную папку.

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
