# Лабораторная работа №1 — парсер пакетов задач

## Выполненные подзадания

- Разбор пакета KRSU: **[+]**
- Разбор пакета CATS: **[+]**
- Разбор пакета EJUDGE: **[+]**
- Разбор пакета PCMS2: **[+]**

## Требования

- Python 3.10 или новее.

## Запуск

```powershell
python main.py KRSU <путь_к_testinfo.xml>
python main.py CATS <путь_к_описанию_задачи.xml>
python main.py EJUDGE <путь_к_problem.cfg>
python main.py PCMS2 <путь_к_problem.xml>
```

Примеры:

```powershell
python main.py KRSU "..\lab_1-task\KRSU\A\testinfo.xml"
python main.py CATS "..\lab_1-task\CATS\area51.xml"
python main.py EJUDGE "..\lab_1-task\EJUDGE\sample\problem.cfg"
python main.py PCMS2 "..\lab_1-task\PCMS2\dungeon\problem.xml"
```

## Результат

Для KRSU программа выводит метаданные из `testinfo.xml`, группы и перечень тестов.

Для CATS программа выводит полную структуру XML-описания задачи: атрибуты `Problem`, текстовые разделы, примеры, решения, checker, генераторы, валидаторы, импорты, тесты и другие элементы формата.

Для EJUDGE программа читает параметры из `problem.cfg`, глобальные параметры и группы тестов из `valuer.cfg`.

Для PCMS2 программа выводит полную структуру `problem.xml`: сведения о задаче, тестовые наборы и группы, statements, assets, решения, checker, валидаторы, documents и остальные элементы.

## Проверка

```powershell
python -m unittest discover -s tests -v
```

Тесты используют папки из `../lab_1-task` относительно корня проекта.
