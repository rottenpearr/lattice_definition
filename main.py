import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QDialog, QMessageBox

from Main_Window_ui import Ui_MainWindow  # Интерфейс главного окна
from Ion_Dialog_ui import Ui_Dialog  # Интерфейс диалогового окна для ввода координат


# Инициализация главного окна
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.combo_box_ions.setEditable(True)
        self.ui.combo_box_ions.lineEdit().setPlaceholderText("Выберите количество ионов")
        self.ui.combo_box_ions.addItems([str(i) for i in range(1, 11)])
        self.ui.combo_box_ions.setCurrentIndex(-1)

        self.ui.combo_box_ions.currentTextChanged.connect(self.populate_list)
        self.ui.ions_list.itemClicked.connect(self.open_input_dialog)
        self.ui.button_start.clicked.connect(self.check_all_values)

        self.ui.widget_2.hide()
        self.ui.button_save.hide()
        # self.ui.button_restart.hide()

        self.ions_data = {}  # Основной словарь для отображаемых данных
        self.temp_ions_data = {}  # Временный словарь для всех данных

    def populate_list(self):
        self.ui.ions_list.clear()
        num_items_text = self.ui.combo_box_ions.currentText()

        if not num_items_text.isdigit() or int(num_items_text) <= 0:
            return

        num_items = int(num_items_text)

        # Обновляем основной словарь на основе временного
        self.ions_data = {i: self.temp_ions_data[i] for i in range(1, num_items + 1) if i in self.temp_ions_data}

        for i in range(1, num_items + 1):
            item = QListWidgetItem(f"Ион {i}")

            # Восстанавливаем данные, если они есть во временном словаре
            saved_data = self.ions_data.get(i)
            if saved_data:
                summary = f"x: {saved_data[0]}, y: {saved_data[1]}, z: {saved_data[2]}"
                item.setText(f"Ион {i} - {summary}")
            else:
                item.setData(1, None)

            self.ui.ions_list.addItem(item)

    def open_input_dialog(self, item):
        ion_number = int(item.text().split()[1])
        saved_data = self.ions_data.get(ion_number)
        dialog = InputDialog(self)

        if saved_data:
            dialog.set_values(*saved_data)

        if dialog.exec() == QDialog.Accepted:
            x, y, z = dialog.get_values()
            if x and y and z:
                summary = f"x: {x}, y: {y}, z: {z}"
                item.setText(f"Ион {ion_number} - {summary}")

                # Сохраняем данные в оба словаря
                self.ions_data[ion_number] = (x, y, z)
                self.temp_ions_data[ion_number] = (x, y, z)

                print("Текущие данные ионов:", self.ions_data)  # Выводим основной словарь
            else:
                QMessageBox.warning(self, "Ошибка", "Все поля x, y, z должны быть заполнены!")

    def check_all_values(self):
        # Проверка всех ионов на заполненность координат
        all_filled = True
        for index in range(self.ui.ions_list.count()):
            item = self.ui.ions_list.item(index)
            coords = item.data(1)  # Извлекаем сохранённые координаты
            if not coords or any(not val for val in coords):  # Проверяем, заполнены ли все значения
                all_filled = False
                break  # Прерываем цикл при первом незаполненном ионе

        if all_filled:
            QMessageBox.information(self, "Успех", "Все координаты введены корректно!")

            # Показываем элементы после нажатия на кнопку "Старт"
            self.ui.widget_2.show()
            self.ui.button_save.show()
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
