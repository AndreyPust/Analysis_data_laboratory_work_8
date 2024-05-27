#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sqlite3
import typing as t
from pathlib import Path


"""
Исходный код индивидуального задания 2.21.

Для своего варианта лабораторной работы 2.17 необходимо реализовать хранение данных 
в базе данных SQLite3. Информация в базе данных должна храниться не менее чем в двух таблицах.

Необходимо использовать словарь, содержащий следующие ключи: название пункта назначения; 
номер поезда; время отправления. Написать программу, выполняющую следующие действия: ввод 
с клавиатуры данных в список, состоящий из словарей заданной структуры; записи должны быть 
упорядочены по времени отправления поезда; вывод на экран информации о поездах, направляющихся 
в пункт, название которого введено с клавиатуры; если таких поездов нет, выдать на дисплей 
соответствующее сообщение (Вариант 26 (7), работа 2.8).

"""


def display_trains(trains: t.List[t.Dict[str, t.Any]]) -> None:
    """
    Отобразить список поездов.
    """
    # Проверить, что список поездов не пуст.
    if trains:
        # Заголовок таблицы.
        line = '+-{}-+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 13,
            '-' * 18,
            '-' * 30
        )
        print(line)
        print(
            '| {:^4} | {:^30} | {:^13} | {:^18} | {:^30} |'.format(
                "№",
                "Пункт отправления",
                "Номер поезда",
                "Время отправления",
                "Пункт назначения"
            )
        )
        print(line)

        # Вывести данные о всех поездах.
        for idx, train in enumerate(trains, 1):
            print(
                '| {:>4} | {:<30} | {:<13} | {:>18} | {:<30} |'.format(
                    idx,
                    train.get('departure_point', ''),
                    train.get('number_train', ''),
                    train.get('time_departure', ''),
                    train.get('destination', '')
                )
            )
            print(line)

    else:
        print("Список поездов пуст.")


def create_db(database_path: Path) -> None:
    """
    Создать базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Создать таблицу с информацией о станциях.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS stations (
        station_id INTEGER PRIMARY KEY AUTOINCREMENT,
        station_name TEXT NOT NULL
        )
        """
    )

    # Создать таблицу с информацией о поездах.
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trains (
        train_id INTEGER PRIMARY KEY AUTOINCREMENT,
        departure_id INTEGER NOT NULL,
        train_number TEXT NOT NULL,
        time_departure TEXT NOT NULL,
        destination_id INTEGER NOT NULL,
        FOREIGN KEY(departure_id) REFERENCES stations(station_id),
        FOREIGN KEY(destination_id) REFERENCES stations(station_id)
        )
        """
    )

    conn.close()


def add_train(database_path: Path, departure_point: str,
              number_train: str, time_departure: str, destination: str) -> None:
    """
    Добавить поезд в базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Получить идентификатор станции отправления в базе данных.
    # Если такой записи нет, то добавить информацию о новой станции.
    cursor.execute(
        """
        SELECT station_id FROM stations WHERE station_name = ?
        """,
        (departure_point,)
    )
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            """
            INSERT INTO stations (station_name) VALUES (?)
            """,
            (departure_point,)
        )
        departure_id = cursor.lastrowid
    else:
        departure_id = row[0]

    # Получить идентификатор станции назначения в базе данных.
    cursor.execute(
        """
        SELECT station_id FROM stations WHERE station_name = ?
        """,
        (destination,)
    )
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            """
            INSERT INTO stations (station_name) VALUES (?)
            """,
            (destination,)
        )
        destination_id = cursor.lastrowid
    else:
        destination_id = row[0]

    # Добавить информацию о новом поезде.
    cursor.execute(
        """
        INSERT INTO trains (departure_id, train_number, time_departure, destination_id)
        VALUES (?, ?, ?, ?)
        """,
        (departure_id, number_train, time_departure, destination_id)
    )

    conn.commit()
    conn.close()


def select_all(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать все поезда.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            trains.train_number, 
            t1.station_name AS departure_point, 
            trains.time_departure, 
            t2.station_name AS destination 
        FROM trains
        JOIN stations t1 ON t1.station_id = trains.departure_id
        JOIN stations t2 ON t2.station_id = trains.destination_id
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "number_train": row[0],
            "departure_point": row[1],
            "time_departure": row[2],
            "destination": row[3],
        }
        for row in rows
    ]


def select_by_destination(database_path: Path, destination: str) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать все поезда, направляющиеся в указанный пункт назначения.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT 
            trains.train_number, 
            t1.station_name AS departure_point, 
            trains.time_departure, 
            t2.station_name AS destination 
        FROM trains
        JOIN stations t1 ON t1.station_id = trains.departure_id
        JOIN stations t2 ON t2.station_id = trains.destination_id
        WHERE LOWER(t2.station_name) = LOWER(?)
        """,
        (destination,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "number_train": row[0],
            "departure_point": row[1],
            "time_departure": row[2],
            "destination": row[3],
        }
        for row in rows
    ]


def main(command_line=None):
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.home() / "trains.db"),
        help="The database file name"
    )

    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("trains")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )

    subparsers = parser.add_subparsers(dest="command")

    # Создать субпарсер для добавления поезда.
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new train"
    )
    add.add_argument(
        "-dep",
        "--departure_point",
        action="store",
        required=True,
        help="The train's departure point"
    )
    add.add_argument(
        "-n",
        "--number_train",
        action="store",
        required=True,
        help="The train's number"
    )
    add.add_argument(
        "-t",
        "--time_departure",
        action="store",
        required=True,
        help="The time departure of train"
    )
    add.add_argument(
        "-des",
        "--destination",
        action="store",
        required=True,
        help="The destination of train"
    )

    # Создать субпарсер для отображения всех поездов.
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all trains"
    )

    # Создать субпарсер для выбора поездов по пунктам назначения.
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Select the trains"
    )
    select.add_argument(
        "-P",
        "--point_user",
        action="store",
        required=True,
        help="The required point"
    )

    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)

    # Получить путь к файлу базы данных.
    db_path = Path(args.db)
    create_db(db_path)

    # Добавить поезд.
    if args.command == "add":
        add_train(
            db_path,
            args.departure_point,
            args.number_train,
            args.time_departure,
            args.destination
        )

    # Отобразить все поезда.
    elif args.command == "display":
        display_trains(select_all(db_path))

    # Выбрать требуемые поезда.
    elif args.command == "select":
        selected = select_by_destination(db_path, args.point_user)
        display_trains(selected)


if __name__ == "__main__":
    main()
