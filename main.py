import sys
from pathlib import Path

import mysql.connector
from PySide6 import QtWidgets
from PySide6.QtGui import QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QDialog, QMessageBox, QWidget, QVBoxLayout, \
    QFrame, QFileDialog
from PySide6.QtCore import Qt

from Main_Window_ui import Ui_MainWindow  # Интерфейс главного окна
from Ion_Dialog_ui import Ui_Dialog       # Интерфейс диалогового окна для ввода координат
from Info_Dialog_ui import Ui_Dialog_2      # Интерфейс диалогового окна информации
from db.config import db_config
from db.ions_query import get_similar_xyz_from_db, check_coords
from collections import Counter
import csv
from generate_report import save_docx
from db.coordinates_nondimensionalization import shift_coordinates, normalize_coordinates


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

        self.ui.pushButton.clicked.connect(self.open_csv_file)

        self.ui.button_restart.clicked.connect(self.restart)
        self.ui.button_save.clicked.connect(self.save)

        self.ui.widget_2.hide()
        self.ui.button_save.hide()

        self.image_name = ""
        self.ions_data = {}  # Словарь для всех данных

        # Подключение кнопки ИНФО
        self.ui.button_info.clicked.connect(self.show_info_dialog)

    def show_info_dialog(self):
        # Создаем и отображаем окно InfoDialog
        dialog = InfoDialog(self)
        dialog.exec()

    def handle_custom_option(self, index):
        # Если выбран элемент "Впишите свой вариант"
        if index == self.ui.combo_box_ions.count() - 1:
            # Возвращаем пользователя к редактируемой строке
            self.ui.combo_box_ions.setCurrentIndex(-1)
            self.ui.combo_box_ions.lineEdit().clear()
            self.ui.combo_box_ions.lineEdit().setFocus()


    def populate_list(self):
        self.check_ion_amount()
        self.ui.ions_list.clear()  # Очищаем список
        num_items_text = self.ui.combo_box_ions.currentText()

        if not num_items_text.isdigit() or int(num_items_text) <= 0:
            return

        num_items = int(num_items_text)
        # Перезаполняем ions_list данными из self.ions_data
        for i in range(1, num_items + 1):
            item = QListWidgetItem(f"Ион {i}")
            saved_data = self.ions_data.get(i)  # Проверяем, есть ли данные для этого иона
            if saved_data:
                summary = f"x: {saved_data[0]}, y: {saved_data[1]}, z: {saved_data[2]}"
                item.setText(f"Ион {i} - {summary}")
                item.setData(Qt.UserRole, saved_data)  # Сохраняем данные в item
            else:
                item.setData(Qt.UserRole, (None, None, None))  # Устанавливаем пустые данные
            self.ui.ions_list.addItem(item)

    def open_csv_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Открыть CSV файл", "", "CSV Files (*.csv);;All Files (*)")
        if file_name:
            with open(str(Path(file_name))) as csvfile:
                csv_data = list(csv.reader(csvfile, delimiter=";"))
                count = len(csv_data)
                if count == 0 or count > 1000:
                    QMessageBox.warning(self, "Ошибка", "Количество строк должно быть в пределах 1-1000!")
                    return
                self.ions_data = {}
                id = 1
                for row in csv_data:
                    try:
                        x, y, z = row[0], row[1], row[2]
                        _, _, _ = float(x), float(y), float(z)
                    except Exception:
                        QMessageBox.warning(self, "Ошибка", f"Недопустимый формат записи!")
                        self.ions_data = {}
                        return
                    self.ions_data[id] = row
                    id += 1
                self.ui.combo_box_ions.setEditText(str(count))
                self.populate_list()

    def open_input_dialog(self, item):
        ion_number = int(item.text().split()[1])
        saved_data = item.data(Qt.UserRole)
        dialog = InputDialog(self)

        if saved_data and all(saved_data):
            dialog.set_values(*saved_data)

        if dialog.exec() == QDialog.Accepted:
            x, y, z = dialog.get_values()
            if x and y and z:
                try:
                    _, _, _ = float(x), float(y), float(z)
                except ValueError:
                    QMessageBox.warning(self, "Ошибка", "Введенные данные некорректны!")
                    return
                summary = f"x: {x}, y: {y}, z: {z}"
                item.setText(f"Ион {ion_number} - {summary}")
                item.setData(Qt.UserRole, (x, y, z))  # Сохраняем данные в item
                self.ions_data[ion_number] = (x, y, z)  # Сохраняем данные в словарь
            else:
                QMessageBox.warning(self, "Ошибка", "Все поля x, y, z должны быть заполнены!")

    def check_ion_amount(self):
        text = self.ui.combo_box_ions.currentText()
        new_next = ""
        for symbol in text:
            if symbol.isdigit():
                new_next += symbol
        try:
            if int(new_next) > 1000:
                new_next = "1000"
        except ValueError:
            pass
        self.ui.combo_box_ions.setCurrentText(new_next)

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

        data = [["ion", float(a), float(b), float(c)] for a, b, c in self.ions_data.values()]
        data_dict = {}
        for i in range(len(data)):
            data_dict[i + 1] = data[i]
        shifted_data = shift_coordinates(data_dict.values())
        normalized_data = normalize_coordinates(shifted_data)
        data_dict = {}
        for i in range(len(normalized_data)):
            data_dict[i + 1] = normalized_data[i]
        coords = get_similar_xyz_from_db(data_dict)
        query_data = check_coords(coords, int(self.ui.combo_box_ions.currentText()))

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
        result_possible_substance_description = (f"Длина ребра ячейки по оси a = {str(result_possible_substance[2])}; "
                                                 f"Длина ребра ячейки по оси b = {str(result_possible_substance[3])}; "
                                                 f"Длина ребра ячейки по оси c = {str(result_possible_substance[4])}; "
                                                 f"Объем элементарной ячейки кристалла (куб. Ангстрем) = {str(result_possible_substance[5])}; "
                                                 f"Угол между осями b и c (альфа) = {str(result_possible_substance[6])}; "
                                                 f"Угол между осями a и c (бета) = {str(result_possible_substance[7])}; "
                                                 f"Угол между осями a и b (гамма) = {str(result_possible_substance[8])}; "
                                                 f"Номер пространственной группы (по МТК) = {str(result_possible_substance[9])}; "
                                                 f"Пространственная группа (Hall-notation) = {str(result_possible_substance[10])}; "
                                                 f"Пространственная группа (Hermann-Mauguin notation) = {str(result_possible_substance[11])};")

        self.image_name = Path("data/images/" + str(result_possible_lattice[1]) + ".png").resolve()

        if all_filled:
            QMessageBox.information(self, "Успех", "Все координаты введены корректно!")
            self.ui.widget_2.show()
            self.ui.button_save.show()
            self.ui.info_lattice.setText(
                f"<b>Подходящие типы кристаллической решетки:</b> {result_lattice_types}<br>"
                f"<b>Наиболее вероятный тип:</b> {result_possible_lattice_name}<br>"
                f"<b>Описание типа:</b> {result_possible_lattice_description}<br>"
                f"<b>Возможное вещество:</b> {result_substances}<br>"
                f"<b>Наиболее вероятное вещество:</b> {result_possible_substance_name}<br>"
                f"<b>Описание вещества:</b> {result_possible_substance_description}"
            )
            png_label = self.ui.lattice_widget
            image_path = str(self.image_name)
            self.pixmap = QPixmap(image_path)
            pixmap_size = self.ui.widget_2.size()

            scaled_pixmap = self.pixmap.scaled(pixmap_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            png_label.setPixmap(scaled_pixmap)
            # layout = QtWidgets.QVBoxLayout(self.ui.widget_2)
            # layout.addWidget(self.ui.lattice_widget, alignment=Qt.AlignmentFlag.AlignCenter)
            # self.ui.widget_2.setLayout(layout)
        else:
            QMessageBox.warning(self, "Ошибка", "Заполните координаты для всех ионов!")

    def restart(self):
        self.ions_data = {}
        self.ui.combo_box_ions.setCurrentText("")
        self.populate_list()
        self.ui.info_lattice.setText("")
        self.ui.lattice_widget.clear()

    def save(self):
        save_docx(self.ui.info_lattice.toPlainText(), self.image_name)


# Инициализация окна для ввода координат
class InputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog()  # Инициализация интерфейса окна ввода координат
        self.ui.setupUi(self)

        self.ui.lineEdit_X.textEdited.connect(lambda: self.check_coordinate(self.ui.lineEdit_X))
        self.ui.lineEdit_Y.textEdited.connect(lambda: self.check_coordinate(self.ui.lineEdit_Y))
        self.ui.lineEdit_Z.textEdited.connect(lambda: self.check_coordinate(self.ui.lineEdit_Z))

        # Подключаем кнопки "ОК" и "Отмена" к методам accept() и reject()
        self.ui.pushButton_2.clicked.connect(self.accept)
        self.ui.pushButton.clicked.connect(self.reject)

    def check_coordinate(self, item):
        text = item.text()
        new_next = ""
        dot = 1
        for i in range(len(text)):
            symbol = text[i]
            if not symbol.isdigit():
                if symbol == "-":
                    if i == 0:
                        new_next += symbol
                elif symbol == ".":
                    if dot == 1:
                        new_next += symbol
                        dot -= 1
            else:
                new_next += symbol
        item.setText(new_next)

    def get_values(self):
        # Получаем значения из QLineEdit полей
        return self.ui.lineEdit_X.text(), self.ui.lineEdit_Y.text(), self.ui.lineEdit_Z.text()

    def set_values(self, x, y, z):
        # Устанавливаем значения в QLineEdit поля
        self.ui.lineEdit_X.setText(x)
        self.ui.lineEdit_Y.setText(y)
        self.ui.lineEdit_Z.setText(z)


class InfoDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Dialog_2()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.close_dialog)

    def close_dialog(self):
        self.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)  # Создаем объект приложения

    main_window = MainWindow()  # Создаем главное окно приложения
    main_window.show()  # Показываем главное окно

    sys.exit(app.exec())  # Запускаем основной цикл приложения и завершаем его при закрытии
