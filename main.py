import sys
from pathlib import Path

import mysql.connector
from PySide6 import QtWidgets
from PySide6.QtGui import QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QDialog, QMessageBox, QWidget, QVBoxLayout, \
    QFrame
from PySide6.QtCore import Qt

from Main_Window_ui import Ui_MainWindow  # Интерфейс главного окна
from Ion_Dialog_ui import Ui_Dialog       # Интерфейс диалогового окна для ввода координат
from db.config import db_config
from collections import Counter


def get_similar_xyz_from_db(coordinates):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    results = []
    try:
        query = """
            SELECT * FROM ions_library
            WHERE atom_site_fract_x = %s AND atom_site_fract_y = %s AND atom_site_fract_z = %s
        """
        for x, y, z in list(coordinates.values()):
            cursor.execute(query, (x, y, z))
            results.append(cursor.fetchall())
    except Exception as e:
        conn.rollback()
        print(f"Произошла ошибка: {e}")
    finally:
        cursor.close()
        conn.close()
    return results


def check_coords(ions):
    ions = ions[0]
    lattice_list = [item[1] for item in ions]
    substance_list = [item[2] for item in ions]

    lattice_counts = Counter(lattice_list)
    lattice_total = sum(lattice_counts.values())
    lattice_probabilities = {name: (count / lattice_total) * 100 for name, count in lattice_counts.items()}
    sorted_lattice_probabilities = sorted(lattice_probabilities.items(), key=lambda x: x[1], reverse=True)

    substance_counts = Counter(substance_list)
    substance_total = sum(substance_counts.values())
    substance_probabilities = {name: (count / substance_total) * 100 for name, count in substance_counts.items()}
    sorted_substance_probabilities = sorted(substance_probabilities.items(), key=lambda x: x[1], reverse=True)

    if not sorted_lattice_probabilities:
        return False

    lattice_names = []
    substance_names = []

    lattice_info_list = []
    lattice_info = None
    top_lattice_id = sorted_lattice_probabilities[0][0]
    top_lattice_probability = sorted_lattice_probabilities[0][1]

    substance_info_list = []
    substance_info = None
    top_substance_id = sorted_substance_probabilities[0][0]
    top_substance_probability = sorted_substance_probabilities[0][1]

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    try:
        query = """
            SELECT * FROM lattice_type
            WHERE id = %s
        """
        for id in lattice_list:
            cursor.execute(query, [id])
            lattice_info_list.append(cursor.fetchall())

        query = """
            SELECT * FROM substances
            WHERE id = %s
        """
        for id in substance_list:
            cursor.execute(query, [id])
            substance_info_list.append(cursor.fetchall())

        for lattice in lattice_info_list:
            lattice = lattice[0]
            if not ([lattice[0], lattice[2], lattice[1]] in lattice_names):
                lattice_names.append([lattice[0], lattice[2], lattice[1]])
            if lattice[0] == top_lattice_id:
                lattice_info = lattice

        for substance in substance_info_list:
            substance = substance[0]
            if not([substance[0], substance[1]] in substance_names):
                substance_names.append([substance[0], substance[1]])
            if substance[0] == top_substance_id:
                substance_info = substance

        for i in range(len(lattice_names)):
            id = lattice_names[i][0]
            probability = lattice_probabilities[id]
            lattice_names[i].append(probability)

        for i in range(len(substance_names)):
            id = substance_names[i][0]
            probability = substance_probabilities[id]
            substance_names[i].append(probability)

    except Exception as e:
        conn.rollback()
        print(f"Произошла ошибка: {e}")
    finally:
        cursor.close()
        conn.close()

    return [[lattice_names, substance_names], [lattice_info, top_lattice_probability], [substance_info, top_substance_probability]]



# Инициализация главного окна
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.combo_box_ions.setEditable(True)
        self.ui.combo_box_ions.lineEdit().setPlaceholderText("Выберите количество ионов")
        self.ui.combo_box_ions.addItems([str(i) for i in range(1, 11)])

        # Добавляем строку "Впишите свой вариант"
        self.ui.combo_box_ions.addItem("Впишите свой вариант")

        # Подключаем обработчик для выбора
        self.ui.combo_box_ions.currentIndexChanged.connect(self.handle_custom_option)

        self.ui.combo_box_ions.setCurrentIndex(-1)  # Оставляем пустым изначально

        self.ui.combo_box_ions.currentTextChanged.connect(self.populate_list)
        self.ui.ions_list.itemClicked.connect(self.open_input_dialog)
        self.ui.button_start.clicked.connect(self.check_all_values)

        self.ui.widget_2.hide()
        self.ui.button_save.hide()

        self.temp_ions_data = {}  # Временный словарь для всех данных

    def handle_custom_option(self, index):
        # Если выбран элемент "Впишите свой вариант"
        if index == self.ui.combo_box_ions.count() - 1:
            # Возвращаем пользователя к редактируемой строке
            self.ui.combo_box_ions.setCurrentIndex(-1)
            self.ui.combo_box_ions.lineEdit().clear()
            self.ui.combo_box_ions.lineEdit().setFocus()


    def populate_list(self):
        self.ui.ions_list.clear()  # Очищаем список
        num_items_text = self.ui.combo_box_ions.currentText()

        if not num_items_text.isdigit() or int(num_items_text) <= 0:
            return

        num_items = int(num_items_text)

        # Перезаполняем ions_list данными из self.temp_ions_data
        for i in range(1, num_items + 1):
            item = QListWidgetItem(f"Ион {i}")
            saved_data = self.temp_ions_data.get(i)  # Проверяем, есть ли данные для этого иона
            if saved_data:
                summary = f"x: {saved_data[0]}, y: {saved_data[1]}, z: {saved_data[2]}"
                item.setText(f"Ион {i} - {summary}")
                item.setData(Qt.UserRole, saved_data)  # Сохраняем данные в item
            else:
                item.setData(Qt.UserRole, (None, None, None))  # Устанавливаем пустые данные
            self.ui.ions_list.addItem(item)

        # print("Обновленные данные ионов:", self.temp_ions_data)  # Проверка данных в консоли

    def open_input_dialog(self, item):
        ion_number = int(item.text().split()[1])
        saved_data = item.data(Qt.UserRole)
        dialog = InputDialog(self)

        if saved_data and all(saved_data):
            dialog.set_values(*saved_data)

        if dialog.exec() == QDialog.Accepted:
            x, y, z = dialog.get_values()
            if x and y and z:
                summary = f"x: {x}, y: {y}, z: {z}"
                item.setText(f"Ион {ion_number} - {summary}")
                item.setData(Qt.UserRole, (x, y, z))  # Сохраняем данные в item

                # Сохраняем данные во временный словарь
                self.temp_ions_data[ion_number] = (x, y, z)

                # print("Текущие данные ионов:", self.temp_ions_data)  # Выводим словарь для отладки
            else:
                QMessageBox.warning(self, "Ошибка", "Все поля x, y, z должны быть заполнены!")

    def check_all_values(self):
        # Проверка всех ионов на заполненность координат
        all_filled = True
        for index in range(self.ui.ions_list.count()):
            item = self.ui.ions_list.item(index)
            coords = item.data(Qt.UserRole)  # Извлекаем сохранённые координаты

            # Проверяем, что координаты не пустые и корректные
            if not coords or any(val is None or val == '' for val in coords):
                all_filled = False
                break  # Прерываем цикл при первом незаполненном ионе

        coords = get_similar_xyz_from_db(self.temp_ions_data)
        query_data = check_coords(coords)

        if not query_data:
            QMessageBox.warning(self, "Поиск не дал результатов", "Попробуйте ввести другие значения!")
            return

        result_lattice_types = query_data[0][0]
        result_substances = query_data[0][1]
        result_possible_lattice = query_data[1][0]
        result_possible_lattice_probability = query_data[1][1]
        result_possible_substance = query_data[2][0]
        result_possible_substance_probability = query_data[2][1]

        result_lattice_types = " ".join(list(str(item[1]) + " " + str(item[3]) + "%;" for item in result_lattice_types))
        result_substances = " ".join(list(str(item[1]) + " " + str(item[2]) + "%;" for item in result_substances))
        result_possible_lattice_name = str(result_possible_lattice[2]) + " " + f"({result_possible_lattice_probability}%)"
        result_possible_lattice_description = str(result_possible_lattice[3])
        result_possible_substance_name = str(result_possible_substance[1]) + " " + f"({result_possible_substance_probability}%)"
        result_possible_substance_description = str(result_possible_substance[-3]) + " " + str(result_possible_substance[-2]) + "..."  # TODO: добавить еще описание

        image_name = Path("data/images/" + str(result_possible_lattice[1]) + ".png").resolve()

        if all_filled:
            QMessageBox.information(self, "Успех", "Все координаты введены корректно!")
            self.ui.widget_2.show()
            self.ui.button_save.show()
            self.ui.combo_box_ions.setDisabled(True)  # Блокируем QComboBox после проверки
            self.ui.info_lattice.setText(
                f"Подходящие типы кристаллической решетки: {result_lattice_types}\n"
                f"Наиболее вероятный тип: {result_possible_lattice_name}\n"
                f"Описание типа: {result_possible_lattice_description}\n"
                f"Возможное вещество: {result_substances}\n"
                f"Наиболее вероятное вещество: {result_possible_substance_name}\n"
                f"Описание вещества: {result_possible_substance_description}"
            )
            png_label = self.ui.lattice_widget
            image_path = str(image_name)
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(
                png_label.size(),
                aspectMode=Qt.AspectRatioMode.KeepAspectRatio
            )
            png_label.setPixmap(pixmap)

            # layout = QtWidgets.QVBoxLayout(self.ui.widget_2)
            # layout.addWidget(self.ui.lattice_widget, alignment=Qt.AlignmentFlag.AlignCenter)
            # self.ui.widget_2.setLayout(layout)

        else:
            QMessageBox.warning(self, "Ошибка", "Заполните координаты для всех ионов!")


# Инициализация окна для ввода координат
class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()  # Инициализация интерфейса окна ввода координат
        self.ui.setupUi(self)

        # Подключаем кнопки "ОК" и "Отмена" к методам accept() и reject()
        self.ui.pushButton_2.clicked.connect(self.accept)
        self.ui.pushButton.clicked.connect(self.reject)

    def get_values(self):
        # Получаем значения из QLineEdit полей
        return self.ui.lineEdit_X.text(), self.ui.lineEdit_Y.text(), self.ui.lineEdit_Z.text()

    def set_values(self, x, y, z):
        # Устанавливаем значения в QLineEdit поля
        self.ui.lineEdit_X.setText(x)
        self.ui.lineEdit_Y.setText(y)
        self.ui.lineEdit_Z.setText(z)


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Создаем объект приложения

    main_window = MainWindow()  # Создаем главное окно приложения
    main_window.show()  # Показываем главное окно

    sys.exit(app.exec())  # Запускаем основной цикл приложения и завершаем его при закрытии
