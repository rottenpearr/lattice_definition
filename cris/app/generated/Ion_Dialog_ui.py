# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Ion_Dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
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
from PySide6.QtWidgets import (QApplication, QDialog, QFrame, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(330, 300)
        Dialog.setMinimumSize(QSize(330, 300))
        Dialog.setMaximumSize(QSize(330, 300))
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
        Dialog.setPalette(palette)
        self.verticalLayout = QVBoxLayout(Dialog)
        self.verticalLayout.setSpacing(20)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(15, 15, 15, 15)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label_ion = QLabel(Dialog)
        self.label_ion.setObjectName(u"label_ion")
        font = QFont()
        font.setFamilies([u"Poppins"])
        font.setPointSize(16)
        font.setBold(True)
        self.label_ion.setFont(font)

        self.verticalLayout_2.addWidget(self.label_ion)


        self.verticalLayout.addLayout(self.verticalLayout_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label = QLabel(Dialog)
        self.label.setObjectName(u"label")
        self.label.setFont(font)

        self.horizontalLayout.addWidget(self.label)

        self.lineEdit_X = QLineEdit(Dialog)
        self.lineEdit_X.setObjectName(u"lineEdit_X")
        font1 = QFont()
        font1.setFamilies([u"Poppins"])
        font1.setPointSize(16)
        self.lineEdit_X.setFont(font1)

        self.horizontalLayout.addWidget(self.lineEdit_X)

        self.horizontalLayout.setStretch(1, 8)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font)

        self.horizontalLayout_2.addWidget(self.label_2)

        self.lineEdit_Y = QLineEdit(Dialog)
        self.lineEdit_Y.setObjectName(u"lineEdit_Y")
        self.lineEdit_Y.setFont(font1)

        self.horizontalLayout_2.addWidget(self.lineEdit_Y)

        self.horizontalLayout_2.setStretch(1, 8)

        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_3 = QLabel(Dialog)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setFont(font)

        self.horizontalLayout_3.addWidget(self.label_3)

        self.lineEdit_Z = QLineEdit(Dialog)
        self.lineEdit_Z.setObjectName(u"lineEdit_Z")
        self.lineEdit_Z.setFont(font1)

        self.horizontalLayout_3.addWidget(self.lineEdit_Z)

        self.horizontalLayout_3.setStretch(1, 8)

        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalFrame_4 = QFrame(Dialog)
        self.horizontalFrame_4.setObjectName(u"horizontalFrame_4")
        self.horizontalLayout_4 = QHBoxLayout(self.horizontalFrame_4)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer)

        self.pushButton_2 = QPushButton(self.horizontalFrame_4)
        self.pushButton_2.setObjectName(u"pushButton_2")
        self.pushButton_2.setFont(font1)
        self.pushButton_2.setStyleSheet(u"QPushButton {\n"
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

        self.horizontalLayout_4.addWidget(self.pushButton_2)

        self.pushButton = QPushButton(self.horizontalFrame_4)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setFont(font1)
        self.pushButton.setStyleSheet(u"QPushButton {\n"
"background-color: #73a36a;\n"
"color: #000000;\n"
"border-radius: 5px;\n"
"padding: 8px;\n"
"}\n"
"\n"
"QPushButton:hover {\n"
"background-color: #96d389;\n"
"border: none; \n"
"}\n"
"\n"
"QPushButton:pressed {\n"
"background-color: #69a84c;\n"
"border: none; \n"
"}")

        self.horizontalLayout_4.addWidget(self.pushButton)

        self.horizontalLayout_4.setStretch(0, 4)
        self.horizontalLayout_4.setStretch(1, 2)
        self.horizontalLayout_4.setStretch(2, 3)

        self.verticalLayout.addWidget(self.horizontalFrame_4)

        self.verticalLayout.setStretch(1, 2)
        self.verticalLayout.setStretch(2, 2)
        self.verticalLayout.setStretch(3, 2)

        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_ion.setText(QCoreApplication.translate("Dialog", u"\u0412\u0432\u0435\u0434\u0438\u0442\u0435 \u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u044b \u0438\u043e\u043d\u0430:", None))
        self.label.setText(QCoreApplication.translate("Dialog", u"X:", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"Y:", None))
        self.label_3.setText(QCoreApplication.translate("Dialog", u"Z:", None))
        self.pushButton_2.setText(QCoreApplication.translate("Dialog", u"\u041e\u041a", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"\u041e\u0442\u043c\u0435\u043d\u0430", None))
    # retranslateUi

