# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Main_Window.ui'
##
## Created by: Qt User Interface Compiler version 6.7.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QHBoxLayout, QLabel,
    QListWidget, QListWidgetItem, QMainWindow, QPushButton,
    QSizePolicy, QSpacerItem, QTextEdit, QVBoxLayout,
    QWidget)
import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QSize(800, 600))
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.WindowText, brush)
        brush1 = QBrush(QColor(115, 163, 106, 255))
        brush1.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Button, brush1)
        palette.setBrush(QPalette.Active, QPalette.Text, brush)
        palette.setBrush(QPalette.Active, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Active, QPalette.ButtonText, brush)
        brush2 = QBrush(QColor(195, 229, 191, 255))
        brush2.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Base, brush2)
        brush3 = QBrush(QColor(255, 255, 255, 255))
        brush3.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Window, brush3)
        brush4 = QBrush(QColor(90, 90, 90, 255))
        brush4.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Shadow, brush4)
        palette.setBrush(QPalette.Active, QPalette.Highlight, brush3)
        brush5 = QBrush(QColor(105, 168, 76, 255))
        brush5.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Link, brush5)
        palette.setBrush(QPalette.Active, QPalette.LinkVisited, brush5)
        brush6 = QBrush(QColor(150, 211, 137, 255))
        brush6.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.AlternateBase, brush6)
        palette.setBrush(QPalette.Active, QPalette.ToolTipBase, brush3)
        palette.setBrush(QPalette.Active, QPalette.ToolTipText, brush)
        brush7 = QBrush(QColor(156, 214, 144, 255))
        brush7.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Active, QPalette.Accent, brush7)
        palette.setBrush(QPalette.Inactive, QPalette.WindowText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Button, brush1)
        palette.setBrush(QPalette.Inactive, QPalette.Text, brush)
        palette.setBrush(QPalette.Inactive, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.ButtonText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Base, brush2)
        palette.setBrush(QPalette.Inactive, QPalette.Window, brush3)
        palette.setBrush(QPalette.Inactive, QPalette.Shadow, brush4)
        palette.setBrush(QPalette.Inactive, QPalette.Highlight, brush3)
        palette.setBrush(QPalette.Inactive, QPalette.Link, brush5)
        palette.setBrush(QPalette.Inactive, QPalette.LinkVisited, brush5)
        palette.setBrush(QPalette.Inactive, QPalette.AlternateBase, brush6)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipBase, brush3)
        palette.setBrush(QPalette.Inactive, QPalette.ToolTipText, brush)
        palette.setBrush(QPalette.Inactive, QPalette.Accent, brush7)
        palette.setBrush(QPalette.Disabled, QPalette.Button, brush1)
        palette.setBrush(QPalette.Disabled, QPalette.BrightText, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Base, brush3)
        palette.setBrush(QPalette.Disabled, QPalette.Window, brush3)
        palette.setBrush(QPalette.Disabled, QPalette.Shadow, brush4)
        brush8 = QBrush(QColor(157, 157, 157, 255))
        brush8.setStyle(Qt.SolidPattern)
        palette.setBrush(QPalette.Disabled, QPalette.Highlight, brush8)
        palette.setBrush(QPalette.Disabled, QPalette.Link, brush5)
        palette.setBrush(QPalette.Disabled, QPalette.LinkVisited, brush5)
        palette.setBrush(QPalette.Disabled, QPalette.AlternateBase, brush6)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipBase, brush3)
        palette.setBrush(QPalette.Disabled, QPalette.ToolTipText, brush)
        palette.setBrush(QPalette.Disabled, QPalette.Accent, brush7)
        MainWindow.setPalette(palette)
        font = QFont()
        font.setFamilies([u"Poppins"])
        font.setPointSize(14)
        MainWindow.setFont(font)
        icon = QIcon()
        icon.addFile(u":/icons/logo.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setFont(font)
        self.widget.setStyleSheet(u"QWidget {\n"
"background-color: #c3e5bf;\n"
"color: #000000;\n"
"border-radius: 15px;\n"
"}\n"
"            \n"
"QPushButton {\n"
"background-color: #73a36a;\n"
"color: #000000;\n"
"border-radius: 5px;\n"
"padding: 8px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: #96d389;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: #69a84c;\n"
"}")
        self.horizontalLayout_3 = QHBoxLayout(self.widget)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label = QLabel(self.widget)
        self.label.setObjectName(u"label")
        font1 = QFont()
        font1.setFamilies([u"Poppins"])
        font1.setPointSize(14)
        font1.setBold(True)
        self.label.setFont(font1)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(False)

        self.horizontalLayout_3.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.button_info = QPushButton(self.widget)
        self.button_info.setObjectName(u"button_info")
        self.button_info.setFont(font)
        icon1 = QIcon()
        icon1.addFile(u":/icons/help.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_info.setIcon(icon1)
        self.button_info.setIconSize(QSize(24, 24))

        self.horizontalLayout_3.addWidget(self.button_info)

        self.horizontalLayout_3.setStretch(0, 5)
        self.horizontalLayout_3.setStretch(1, 1)
        self.horizontalLayout_3.setStretch(2, 5)

        self.verticalLayout.addWidget(self.widget)

        self.combo_box_ions = QComboBox(self.centralwidget)
        self.combo_box_ions.setObjectName(u"combo_box_ions")
        font2 = QFont()
        font2.setFamilies([u"Poppins"])
        font2.setPointSize(16)
        self.combo_box_ions.setFont(font2)
        self.combo_box_ions.setStyleSheet(u"QComboBox {\n"
"    background-color: #9cd690;\n"
"    color: #000000;\n"
"    border-radius: 15px;\n"
"    padding: 5px;\n"
"}\n"
"\n"
"QComboBox::down-arrow {\n"
"    width: 10px;\n"
"    height: 10px;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #e8f5e9;\n"
"    color: #000000;\n"
"    selection-background-color: #c5e1a5;\n"
"}\n"
"\n"
"QComboBox QAbstractItemView QScrollBar:vertical {\n"
"    border: none;\n"
"    background: #9cd690;\n"
"    width: 15px;\n"
"}\n"
"\n"
"QComboBox {\n"
"        font-family: 'Poppins';\n"
"        font-size: 16pt;\n"
"}\n"
"")

        self.verticalLayout.addWidget(self.combo_box_ions)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.ions_list = QListWidget(self.centralwidget)
        self.ions_list.setObjectName(u"ions_list")
        self.ions_list.setFont(font)
        self.ions_list.setStyleSheet(u"QListWidget {\n"
"background-color: #c3e5bf;\n"
"color: #000000;\n"
"border-radius: 15px;\n"
"}")

        self.horizontalLayout_2.addWidget(self.ions_list)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.pushButton = QPushButton(self.centralwidget)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setStyleSheet(u"QPushButton {\n"
"background-color: #73a36a;\n"
"color: #000000;\n"
"border-radius: 5px;\n"
"padding: 8px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: #96d389;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: #69a84c;\n"
"}")
        icon2 = QIcon()
        icon2.addFile(u":/icons/download.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.pushButton.setIcon(icon2)
        self.pushButton.setIconSize(QSize(24, 24))

        self.verticalLayout_6.addWidget(self.pushButton)


        self.verticalLayout.addLayout(self.verticalLayout_6)


        self.horizontalLayout.addLayout(self.verticalLayout)

        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.widget_2 = QWidget(self.centralwidget)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setStyleSheet(u"QWidget {\n"
"border: 2px solid #69a84c;\n"
"border-radius: 15px;\n"
"}")
        self.horizontalLayout_5 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.lattice_widget = QLabel(self.widget_2)
        self.lattice_widget.setObjectName(u"lattice_widget")
        self.lattice_widget.setStyleSheet(u"QWidget {\n"
"border: none;\n"
"border-radius: none;\n"
"}")
        self.lattice_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_5.addWidget(self.lattice_widget)


        self.verticalLayout_3.addWidget(self.widget_2)


        self.verticalLayout_2.addLayout(self.verticalLayout_3)

        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.info_lattice = QTextEdit(self.centralwidget)
        self.info_lattice.setObjectName(u"info_lattice")
        self.info_lattice.setFont(font)
        self.info_lattice.setStyleSheet(u"QTextEdit {\n"
"background-color: rgb(255, 255, 255);\n"
"color: rgb(0, 0, 0);\n"
"border-radius: 15px;\n"
"}")
        self.info_lattice.setReadOnly(True)

        self.verticalLayout_4.addWidget(self.info_lattice)


        self.verticalLayout_2.addLayout(self.verticalLayout_4)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.button_save = QPushButton(self.centralwidget)
        self.button_save.setObjectName(u"button_save")
        self.button_save.setFont(font)
        self.button_save.setStyleSheet(u"QPushButton {\n"
"background-color: #73a36a;\n"
"color: #000000;\n"
"border-radius: 5px;\n"
"padding: 8px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: #96d389;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: #69a84c;\n"
"}")

        self.verticalLayout_5.addWidget(self.button_save)


        self.verticalLayout_2.addLayout(self.verticalLayout_5)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.button_start = QPushButton(self.centralwidget)
        self.button_start.setObjectName(u"button_start")
        self.button_start.setFont(font)
        self.button_start.setStyleSheet(u"QPushButton {\n"
"background-color: #73a36a;\n"
"color: #000000;\n"
"border-radius: 5px;\n"
"padding: 8px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: #96d389;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: #69a84c;\n"
"}")
        icon3 = QIcon()
        icon3.addFile(u":/icons/check.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_start.setIcon(icon3)
        self.button_start.setIconSize(QSize(24, 24))

        self.horizontalLayout_4.addWidget(self.button_start)

        self.button_restart = QPushButton(self.centralwidget)
        self.button_restart.setObjectName(u"button_restart")
        self.button_restart.setStyleSheet(u"QPushButton {\n"
"background-color: #73a36a;\n"
"color: #000000;\n"
"border-radius: 5px;\n"
"padding: 8px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: #96d389;\n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: #69a84c;\n"
"}")
        icon4 = QIcon()
        icon4.addFile(u":/icons/refresh.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.button_restart.setIcon(icon4)
        self.button_restart.setIconSize(QSize(24, 24))

        self.horizontalLayout_4.addWidget(self.button_restart)

        self.horizontalLayout_4.setStretch(0, 2)
        self.horizontalLayout_4.setStretch(1, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.verticalLayout_2.setStretch(0, 2)
        self.verticalLayout_2.setStretch(1, 1)

        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 3)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u041e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0438\u0435 \u0442\u0438\u043f\u0430 \u043a\u0440\u0438\u0441\u0442\u0430\u043b\u043b\u0438\u0447\u0435\u0441\u043a\u043e\u0439 \u0440\u0435\u0448\u0435\u0442\u043a\u0438", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"\u0422\u0418\u041f \u0420\u0415\u0428\u0415\u0422\u041a\u0418", None))
        self.button_info.setText("")
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"\u0417\u0410\u0413\u0420\u0423\u0417\u0418\u0422\u042c \u0418\u0417 \u0424\u0410\u0419\u041b\u0410", None))
        self.lattice_widget.setText("")
        self.info_lattice.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Poppins'; font-size:14pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.button_save.setText(QCoreApplication.translate("MainWindow", u"\u0421\u041e\u0425\u0420\u0410\u041d\u0418\u0422\u042c", None))
        self.button_start.setText(QCoreApplication.translate("MainWindow", u"\u0421\u0422\u0410\u0420\u0422", None))
        self.button_restart.setText("")
    # retranslateUi

