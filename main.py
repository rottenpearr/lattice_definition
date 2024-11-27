import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QDialog, QMessageBox

from Main_Window_ui import Ui_MainWindow  # Интерфейс главного окна
from Ion_Dialog_ui import Ui_Dialog


# Инициализация главного окна
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()  # Инициализация интерфейса главного окна
        self.ui.setupUi(self)

        self.ui.combo_box_ions.setEditable(True)  # Делаем QComboBox редактируемым
        self.ui.combo_box_ions.addItems([str(i) for i in range(1, 11)])  # Добавляем варианты от 1 до 10
        self.ui.combo_box_ions.currentTextChanged.connect(self.populate_list)  # Обрабатываем изменение текста

        self.ui.ions_list.itemClicked.connect(self.open_input_dialog)
        self.ui.button_start.clicked.connect(self.check_all_values)

        # Скрываем элементы до нажатия кнопки "Старт"
        self.ui.widget_2.hide()
        self.ui.button_save.hide()

        self.ions_data = {}  # Словарь для хранения данных о координатах

    def populate_list(self):
        self.ui.ions_list.clear()
        num_items_text = self.ui.combo_box_ions.currentText()

        # Проверка на корректность ввода числа
        if not num_items_text.isdigit() or int(num_items_text) <= 0:
            return  # Игнорируем некорректные значения

        num_items = int(num_items_text)

        # Удаляем данные для ионов, которые больше не будут отображаться
        self.ions_data = {k: v for k, v in self.ions_data.items() if k <= num_items}

        for i in range(1, num_items + 1):
            item = QListWidgetItem(f"Ион {i}")

            # Если данные для этого иона уже были сохранены, восстанавливаем их
            saved_data = self.ions_data.get(i)
            if saved_data:
                summary = f"x: {saved_data[0]}, y: {saved_data[1]}, z: {saved_data[2]}"
                item.setText(f"Ион {i} - {summary}")
            else:
                item.setData(1, None)  # Для хранения дополнительной информации (изначально None)

            self.ui.ions_list.addItem(item)

    def open_input_dialog(self, item):
        ion_number = int(item.text().split()[1])  # Извлекаем номер иона
        saved_data = item.data(1)  # Получаем сохраненные данные (x, y, z) или None
        dialog = InputDialog(self)

        # Если есть сохранённые данные, устанавливаем их в поля
        if saved_data:
            dialog.set_values(*saved_data)

        # Открываем диалог
        if dialog.exec() == QDialog.Accepted:  # Проверяем, нажата ли кнопка "ОК"
            x, y, z = dialog.get_values()
            if x and y and z:  # Проверяем, что все поля заполнены
                summary = f"x: {x}, y: {y}, z: {z}"
                item.setText(f"Ион {ion_number} - {summary}")
                item.setData(1, (x, y, z))  # Сохраняем данные для дальнейшего использования
                self.ions_data[ion_number] = (x, y, z)  # Сохраняем данные в словарь
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
