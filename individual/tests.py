#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import sqlite3
from pathlib import Path
import os
import induvidual_1


TEST_DB = "test_trains.db"


class CustomTestResult(unittest.TextTestResult):
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)

    def addSuccess(self, test):
        super().addSuccess(test)
        self.stream.writeln(f"{self.getDescription(test)} ... ok")

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.stream.writeln(f"{self.getDescription(test)} ... skipped '{reason}'")


class CustomTestRunner(unittest.TextTestRunner):
    def _makeResult(self):
        return CustomTestResult(self.stream, self.descriptions, self.verbosity)


class TrainManagementTest(unittest.TestCase):

    def setUp(self):
        """Создание тестовой базы данных перед каждым тестированием."""
        self.database_path = Path(TEST_DB)
        induvidual_1.create_db(self.database_path)

    def tearDown(self):
        """Удаление тестовой базы данных после каждого теста."""
        os.remove(self.database_path)

    def test_add_train(self):
        """Тест добавления поездов"""
        # Добавление поезда, используя эту функцию
        departure_point = "Москва"
        number_train = "123A"
        time_departure = "12:00"
        destination = "Санкт-Петербург"
        induvidual_1.add_train(self.database_path, departure_point, number_train, time_departure, destination)

        # Проверка добавления поезда
        conn = sqlite3.connect(str(self.database_path))
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT t1.station_name AS departure_point, trains.train_number, trains.time_departure, t2.station_name AS destination 
            FROM trains
            JOIN stations t1 ON t1.station_id = trains.departure_id
            JOIN stations t2 ON t2.station_id = trains.destination_id
            WHERE trains.train_number = ?
            """,
            (number_train,)
        )
        row = cursor.fetchone()
        conn.close()
        self.assertIsNotNone(row)
        self.assertEqual(row, (departure_point, number_train, time_departure, destination))

    def test_select_all(self):
        """Проверка выбора всех поездов."""
        # Add trains using the function
        trains_data = [
            ("Москва", "123", "12:00", "Санкт-Петербург"),
            ("Казань", "456", "14:00", "Москва")
        ]
        for train_data in trains_data:
            induvidual_1.add_train(self.database_path, *train_data)

        # Проверка выбора
        trains = induvidual_1.select_all(self.database_path)
        self.assertEqual(len(trains), len(trains_data))
        for train_data in trains_data:
            self.assertIn({
                "number_train": train_data[1],
                "departure_point": train_data[0],
                "time_departure": train_data[2],
                "destination": train_data[3],
            }, trains)

    def test_select_by_destination(self):
        """Тестирование поездов по пункту назначения"""
        trains_data = [
            ("Москва", "123", "12:00", "Санкт-Петербург"),
            ("Казань", "456", "14:00", "Москва"),
            ("Сочи", "789", "16:00", "Москва")
        ]
        for train_data in trains_data:
            induvidual_1.add_train(self.database_path, *train_data)

        # Проверка поезда на пункт назначения Москава.
        selected_trains = induvidual_1.select_by_destination(self.database_path, "Москва")
        expected_trains = [
            {
                "number_train": "456",
                "departure_point": "Казань",
                "time_departure": "14:00",
                "destination": "Москва"
            },
            {
                "number_train": "789",
                "departure_point": "Сочи",
                "time_departure": "16:00",
                "destination": "Москва"
            }
        ]
        self.assertEqual(len(selected_trains), len(expected_trains))
        for train in expected_trains:
            self.assertIn(train, selected_trains)


if __name__ == "__main__":
    unittest.main(testRunner=CustomTestRunner)
