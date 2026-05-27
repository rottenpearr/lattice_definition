import csv
import sys
import threading
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QMainWindow, QListWidgetItem, QDialog, QMessageBox, QFileDialog

from cris.app.generated.Info_Dialog_ui import Ui_Dialog_2  # Интерфейс диалогового окна информации
from cris.app.generated.Ion_Dialog_ui import Ui_Dialog  # Интерфейс диалогового окна для ввода координат
from cris.app.generated.Main_Window_ui import Ui_MainWindow  # Интерфейс главного окна
from cris.core.coordinates import shift_coordinates, normalize_coordinates
from cris.db.queries import get_similar_xyz_from_db, check_coords
from cris.db.repository.recognition import get_or_create_session, save_result
from cris.db.enrichment.substance_enricher import enrich_substance
from cris.core.ml_predict import predict_catboost, predict_catboost_substance, predict_rf, resolve_lattice_ids
from cris.logger import logger
from cris.tools.report import save_docx


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

        # self.ui.widget_2.hide()
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
        # TODO: здесь поиск добавить векторов функцию вызов
        coords = get_similar_xyz_from_db(data_dict)
        query_data = check_coords(coords, int(self.ui.combo_box_ions.currentText()))

        # ── Сессия создаётся всегда, независимо от DB-матча ──────────────────
        session = None
        try:
            norm_tuples = [(row[1], row[2], row[3]) for row in normalized_data]
            ion_count   = int(self.ui.combo_box_ions.currentText())
            session = get_or_create_session(ion_count=ion_count, normalized_coords=norm_tuples)
        except Exception as e:
            logger.warning("Could not create session: {}", e)

        # ── DB-результаты (если нашлось) ──────────────────────────────────────
        if query_data:
            result_lattice_types = sorted(query_data[0][0], key=lambda x: -x[3])
            result_substances    = sorted(query_data[0][1], key=lambda x: -x[2])
            result_possible_lattice              = query_data[1][0]
            result_possible_lattice_probability  = query_data[1][1]
            result_possible_substance            = query_data[2][0]
            result_possible_substance_probability = query_data[2][1]

            try:
                if session:
                    top_lt_id = result_possible_lattice[0] if result_possible_lattice else None
                    top_st_id = result_possible_substance[0] if result_possible_substance else None
                    save_result(
                        session_id=session.id,
                        method="COORD_MATCH",
                        method_version="1.0",
                        rank=1,
                        lattice_type_id=top_lt_id,
                        structure_id=top_st_id,
                        confidence=round(result_possible_lattice_probability / 100.0, 4),
                    )
                    logger.info("Session saved: id={}", session.id[:8])
            except Exception as e:
                logger.warning("Could not save recognition session: {}", e)
        else:
            result_lattice_types = []
            result_substances    = []
            result_possible_lattice              = None
            result_possible_lattice_probability  = 0.0
            result_possible_substance            = None
            result_possible_substance_probability = 0.0

        # ── CatBoost (сингония) ───────────────────────────────────────────────
        cb_preds = []
        try:
            cb_preds = predict_catboost(normalized_data)
            if cb_preds and session:
                resolve_lattice_ids(cb_preds)
                for rank, pred in enumerate(cb_preds, start=1):
                    save_result(session_id=session.id, method="CATBOOST",
                                method_version="1.0", rank=rank,
                                lattice_type_id=pred["lattice_type_id"],
                                structure_id=None, confidence=pred["confidence"])
                logger.info("CatBoost: top={} ({:.0f}%)",
                            cb_preds[0]["class"], cb_preds[0]["confidence"] * 100)
        except Exception as e:
            logger.warning("CatBoost prediction failed: {}", e)

        # ── CatBoost (вещество) ───────────────────────────────────────────────
        cb_substance_preds = []
        try:
            cb_substance_preds = predict_catboost_substance(normalized_data)
            if cb_substance_preds and session:
                resolve_lattice_ids(cb_substance_preds)
                for rank, pred in enumerate(cb_substance_preds, start=1):
                    save_result(session_id=session.id, method="CATBOOST_SUBSTANCE",
                                method_version="1.0", rank=rank,
                                lattice_type_id=pred["lattice_type_id"],
                                structure_id=None, confidence=pred["confidence"])
                logger.info("CatBoost-substance: top={} ({:.0f}%)",
                            cb_substance_preds[0]["class"], cb_substance_preds[0]["confidence"] * 100)
        except Exception as e:
            logger.warning("CatBoost-substance prediction failed: {}", e)

        # ── RF (вещество) ─────────────────────────────────────────────────────
        rf_preds = []
        try:
            rf_preds = predict_rf(normalized_data)
            if rf_preds and session:
                resolve_lattice_ids(rf_preds)
                for rank, pred in enumerate(rf_preds, start=1):
                    save_result(session_id=session.id, method="RF",
                                method_version="1.0", rank=rank,
                                lattice_type_id=pred["lattice_type_id"],
                                structure_id=None, confidence=pred["confidence"])
                logger.info("RF: top={} ({:.0f}%)",
                            rf_preds[0]["class"], rf_preds[0]["confidence"] * 100)
        except Exception as e:
            logger.warning("RF prediction failed: {}", e)

        # ── Запускаем обогащение вещества в фоне (не блокируем UI) ───────────
        if result_possible_substance is not None:
            st_id      = result_possible_substance[0]
            st_name    = result_possible_substance[1]
            st_formula = result_possible_substance[13] if len(result_possible_substance) > 13 else ""
            lt_name    = str(result_possible_lattice[2]) if result_possible_lattice else ""

            def _bg_enrich():
                try:
                    enrich_substance(
                        structure_id=st_id,
                        formula=st_formula or st_name,
                        name=st_name,
                        lattice_type=lt_name,
                    )
                except Exception as exc:
                    logger.warning("Background substance enrichment failed: {}", exc)

            threading.Thread(target=_bg_enrich, daemon=True).start()

        db_lattice_list   = " ".join(f"{item[1]} {item[3]:.2f}%;" for item in result_lattice_types) or "—"
        db_substance_list = " ".join(f"{item[1]} {item[2]:.2f}%;" for item in result_substances) or "—"
        if result_possible_lattice:
            db_lattice_top  = str(result_possible_lattice[2]) + f" {result_possible_lattice_probability:.2f}%"
            db_lattice_desc = str(result_possible_lattice[3])
        else:
            db_lattice_top  = "—"
            db_lattice_desc = "совпадений в базе не найдено"
        if result_possible_substance:
            db_substance_top = str(result_possible_substance[1]) + f" ({result_possible_substance_probability:.2f}%)"
            db_substance_desc = (
                f"a={result_possible_substance[2]}, b={result_possible_substance[3]}, "
                f"c={result_possible_substance[4]}; "
                f"V={result_possible_substance[5]} Å³; "
                f"α={result_possible_substance[6]}, β={result_possible_substance[7]}, γ={result_possible_substance[8]}; "
                f"SG №{result_possible_substance[9]} ({result_possible_substance[11]})"
            )
        else:
            db_substance_top  = "—"
            db_substance_desc = "—"

        def _fmt_ml_ranking(preds: list[dict], top_k: int = 3) -> str:
            if not preds:
                return "—"
            parts = [f"{p['lattice_name']} {p['confidence']*100:.1f}%" for p in preds[:top_k]]
            return ";  ".join(parts)

        cb_str          = _fmt_ml_ranking(cb_preds)
        cb_substance_str = _fmt_ml_ranking(cb_substance_preds)
        rf_str          = _fmt_ml_ranking(rf_preds)

        lattice_img_name = result_possible_lattice[1] if result_possible_lattice else "default"
        self.image_name = Path("data/images/" + str(lattice_img_name) + ".png").resolve()

        if all_filled:
            QMessageBox.information(self, "Успех", "Все координаты введены корректно!")
            self.ui.button_save.show()
            self.ui.info_lattice.setText(
                # ── Сингония ──────────────────────────────────────────────────
                "<b>━━━ СИНГОНИЯ ━━━</b><br>"
                f"<b>БД — подходящие типы:</b> {db_lattice_list}<br>"
                f"<b>БД — наиболее вероятный:</b> {db_lattice_top}<br>"
                f"<b>БД — описание типа:</b> {db_lattice_desc}<br>"
                f"<b>CatBoost (сингония):</b> {cb_str}<br>"
                "<br>"
                # ── По веществу ───────────────────────────────────────────────
                "<b>━━━ ВЕЩЕСТВО ━━━</b><br>"
                f"<b>БД — подходящие вещества:</b> {db_substance_list}<br>"
                f"<b>БД — наиболее вероятное:</b> {db_substance_top}<br>"
                f"<b>БД — параметры ячейки:</b> {db_substance_desc}<br>"
                f"<b>CatBoost (вещество):</b> {cb_substance_str}<br>"
                f"<b>Random Forest:</b> {rf_str}"
            )
            png_label = self.ui.lattice_widget
            image_path = str(self.image_name)
            self.pixmap = QPixmap(image_path)
            # pixmap_size = self.ui.widget_2.size()
            # scaled_pixmap = self.pixmap.scaled(pixmap_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            # png_label.setPixmap(scaled_pixmap)
        else:
            QMessageBox.warning(self, "Ошибка", "Заполните координаты для всех ионов!")

    def restart(self):
        self.ions_data = {}
        self.ui.combo_box_ions.setCurrentText("")
        self.populate_list()
        self.ui.info_lattice.setText("")
        self.ui.lattice_widget.clear()

    def save(self):
        filename = save_docx(self.ui.info_lattice.toPlainText(), self.image_name)
        QMessageBox.information(self, "Успех", f"Документ сохранен как {filename} в папку 'reports'.")


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
