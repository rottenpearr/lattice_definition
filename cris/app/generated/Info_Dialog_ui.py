# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'Info_Dialog.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
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
from PySide6.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QTextEdit, QVBoxLayout,
    QWidget)

class Ui_Dialog_2(object):
    def setupUi(self, Dialog):
        if not Dialog.objectName():
            Dialog.setObjectName(u"Dialog")
        Dialog.resize(500, 400)
        Dialog.setMinimumSize(QSize(500, 400))
        Dialog.setMaximumSize(QSize(500, 400))
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
        self.horizontalLayout_2 = QHBoxLayout(Dialog)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_2 = QLabel(Dialog)
        self.label_2.setObjectName(u"label_2")
        font = QFont()
        font.setFamilies([u"Poppins"])
        font.setPointSize(14)
        font.setBold(True)
        self.label_2.setFont(font)

        self.verticalLayout.addWidget(self.label_2)

        self.textEdit_2 = QTextEdit(Dialog)
        self.textEdit_2.setObjectName(u"textEdit_2")
        self.textEdit_2.setMinimumSize(QSize(0, 0))
        self.textEdit_2.setMaximumSize(QSize(16777215, 16777215))
        self.textEdit_2.setBaseSize(QSize(0, 0))
        self.textEdit_2.setReadOnly(True)
        self.textEdit_2.setOverwriteMode(False)
        self.textEdit_2.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        self.verticalLayout.addWidget(self.textEdit_2)

        self.pushButton = QPushButton(Dialog)
        self.pushButton.setObjectName(u"pushButton")
        self.pushButton.setFont(font)
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

        self.verticalLayout.addWidget(self.pushButton)


        self.horizontalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(Dialog)

        QMetaObject.connectSlotsByName(Dialog)
    # setupUi

    def retranslateUi(self, Dialog):
        Dialog.setWindowTitle(QCoreApplication.translate("Dialog", u"Dialog", None))
        self.label_2.setText(QCoreApplication.translate("Dialog", u"\u041e \u041f\u0420\u041e\u0413\u0420\u0410\u041c\u041c\u0415:", None))
        self.textEdit_2.setHtml(QCoreApplication.translate("Dialog", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><meta charset=\"utf-8\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"hr { height: 1px; border-width: 0; }\n"
"li.unchecked::marker { content: \"\\2610\"; }\n"
"li.checked::marker { content: \"\\2612\"; }\n"
"</style></head><body style=\" font-family:'Segoe UI'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">\u041f\u0435\u0440\u0435\u0434 \u0432\u0430\u043c\u0438 \u043f\u0440\u043e\u0442\u043e\u0442\u0438\u043f \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0430 \u0434\u043b\u044f \u0440\u0430\u0441\u043f\u043e\u0437\u043d\u0430\u0432\u0430\u043d\u0438\u044f \u043a\u0440\u0438\u0441\u0442\u0430\u043b\u043b\u0438\u0447\u0435\u0441\u043a\u0438\u0445 \u0440\u0435\u0448\u0435"
                        "\u0442\u043e\u043a, \u0441\u043e\u0437\u0434\u0430\u043d\u043d\u044b\u0439 \u0432 \u0440\u0430\u043c\u043a\u0430\u0445 \u043a\u0443\u0440\u0441\u043e\u0432\u043e\u0433\u043e \u043f\u0440\u043e\u0435\u043a\u0442\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f \u043f\u043e \u0434\u0438\u0441\u0446\u0438\u043f\u043b\u0438\u043d\u0435 \u00ab\u0411\u0430\u0437\u044b \u0434\u0430\u043d\u043d\u044b\u0445\u00bb.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">\u0414\u043b\u044f \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0435\u043d\u0438\u044f \u0442\u0438\u043f\u0430 \u043a\u0440\u0438\u0441\u0442\u0430\u043b\u043b\u0438\u0447\u0435\u0441\u043a\u043e\u0439 \u0440\u0435\u0448\u0435\u0442\u043a\u0438 \u043d\u0435\u043e\u0431\u0445\u043e\u0434\u0438\u043c\u043e \u0432\u0432\u0435\u0441\u0442\u0438 </span><span style=\" font-size:14pt; font-weight:700;\">\u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430"
                        "\u0442\u044b \u0432\u0441\u0435\u0445 \u0430\u0442\u043e\u043c\u043e\u0432 \u044d\u043b\u0435\u043c\u0435\u043d\u0442\u0430\u0440\u043d\u043e\u0439 \u044f\u0447\u0435\u0439\u043a\u0438</span><span style=\" font-size:14pt;\">.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">\u0412\u044b \u043c\u043e\u0436\u0435\u0442\u0435 \u0432\u044b\u0431\u0440\u0430\u0442\u044c \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e \u0438\u043e\u043d\u043e\u0432, \u0438\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u044f \u0432\u044b\u043f\u0430\u0434\u0430\u044e\u0449\u0438\u0439 \u0441\u043f\u0438\u0441\u043e\u043a \u0438\u043b\u0438 \u0432\u0432\u043e\u0434\u044f \u0437\u043d\u0430\u0447\u0435\u043d\u0438\u0435 \u0432\u0440\u0443\u0447\u043d\u0443\u044e. \u041f\u043e\u0441\u043b\u0435 \u044d\u0442\u043e\u0433\u043e \u0432\u0432\u0435\u0434\u0438\u0442\u0435 \u043a\u043e\u043e\u0440\u0434\u0438\u043d"
                        "\u0430\u0442\u044b \u043a\u0430\u0436\u0434\u043e\u0433\u043e \u0438\u043e\u043d\u0430 \u0432 \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u044e\u0449\u0438\u0435 \u043f\u043e\u043b\u044f.<br />\u0410\u043b\u044c\u0442\u0435\u0440\u043d\u0430\u0442\u0438\u0432\u043d\u043e, \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0430 \u043f\u043e\u0434\u0434\u0435\u0440\u0436\u0438\u0432\u0430\u0435\u0442 \u0437\u0430\u0433\u0440\u0443\u0437\u043a\u0443 \u0444\u0430\u0439\u043b\u0430 \u0432 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 </span><span style=\" font-size:14pt; font-style:italic;\">.csv</span><span style=\" font-size:14pt;\">, \u0441\u043e\u0434\u0435\u0440\u0436\u0430\u0449\u0435\u0433\u043e \u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u044b. \u0412 \u044d\u0442\u043e\u043c \u0441\u043b\u0443\u0447\u0430\u0435 \u043a\u0430\u0436\u0434\u044b\u0439 \u0438\u043e\u043d \u0434\u043e\u043b\u0436\u0435\u043d \u0431\u044b\u0442\u044c \u0437\u0430\u043f\u0438\u0441\u0430\u043d \u0432 "
                        "\u043e\u0442\u0434\u0435\u043b\u044c\u043d\u043e\u0439 \u0441\u0442\u0440\u043e\u043a\u0435 \u0444\u0430\u0439\u043b\u0430. \u0417\u0430\u0433\u0440\u0443\u0436\u0435\u043d\u043d\u044b\u0435 \u0434\u0430\u043d\u043d\u044b\u0435 \u0431\u0443\u0434\u0443\u0442 \u0430\u0432\u0442\u043e\u043c\u0430\u0442\u0438\u0447\u0435\u0441\u043a\u0438 \u043e\u0431\u0440\u0430\u0431\u043e\u0442\u0430\u043d\u044b \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u043e\u0439.</span></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">\u041f\u043e\u0441\u043b\u0435 \u0432\u0432\u043e\u0434\u0430 \u0432\u0441\u0435\u0445 \u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442 \u043d\u0430\u0436\u043c\u0438\u0442\u0435 \u043a\u043d\u043e\u043f\u043a\u0443 \u00ab\u0421\u0422\u0410\u0420\u0422\u00bb. \u041f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u0430 \u043e\u043f\u0440\u0435\u0434\u0435\u043b\u0438\u0442 \u0442\u0438\u043f "
                        "\u043a\u0440\u0438\u0441\u0442\u0430\u043b\u043b\u0438\u0447\u0435\u0441\u043a\u043e\u0439 \u0440\u0435\u0448\u0435\u0442\u043a\u0438, \u043e\u0442\u043e\u0431\u0440\u0430\u0437\u0438\u0442 \u0443\u0441\u043b\u043e\u0432\u043d\u043e\u0435 \u0438\u0437\u043e\u0431\u0440\u0430\u0436\u0435\u043d\u0438\u0435 \u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u044b, \u0434\u0430\u0441\u0442 \u043a\u0440\u0430\u0442\u043a\u043e\u0435 \u043e\u043f\u0438\u0441\u0430\u043d\u0438\u0435 \u043d\u0430\u0439\u0434\u0435\u043d\u043d\u043e\u0439 \u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u044b, \u043f\u0440\u0435\u0434\u043e\u0441\u0442\u0430\u0432\u0438\u0442 \u0432\u0435\u0440\u043e\u044f\u0442\u043d\u043e\u0441\u0442\u044c \u043f\u0440\u0438\u043d\u0430\u0434\u043b\u0435\u0436\u043d\u043e\u0441\u0442\u0438 \u043a \u0442\u043e\u043c\u0443 \u0438\u043b\u0438 \u0438\u043d\u043e\u043c\u0443 \u0442\u0438\u043f\u0443 \u0440\u0435\u0448\u0435\u0442\u043a\u0438, \u0438 \u043f\u0440\u0435\u0434\u043b\u043e\u0436\u0438\u0442 \u0441"
                        "\u043f\u0438\u0441\u043e\u043a \u0432\u043e\u0437\u043c\u043e\u0436\u043d\u044b\u0445 \u0432\u0435\u0449\u0435\u0441\u0442\u0432, \u0441\u043e\u043e\u0442\u0432\u0435\u0442\u0441\u0442\u0432\u0443\u044e\u0449\u0438\u0445 \u0432\u0432\u0435\u0434\u0435\u043d\u043d\u044b\u043c \u043a\u043e\u043e\u0440\u0434\u0438\u043d\u0430\u0442\u0430\u043c.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">\u0414\u043b\u044f \u0441\u043e\u0445\u0440\u0430\u043d\u0435\u043d\u0438\u044f \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u043e\u0432 \u0432\u044b \u043c\u043e\u0436\u0435\u0442\u0435 \u0441\u043e\u0437\u0434\u0430\u0442\u044c \u043e\u0442\u0447\u0435\u0442 \u0432 \u0444\u043e\u0440\u043c\u0430\u0442\u0435 .docx. \u0414\u043b\u044f \u044d\u0442\u043e\u0433\u043e \u0434\u043e\u0441\u0442\u0430\u0442\u043e\u0447\u043d\u043e \u043d\u0430\u0436\u0430\u0442\u044c \u043a\u043d\u043e\u043f\u043a\u0443"
                        " \u00ab\u0421\u041e\u0425\u0420\u0410\u041d\u0418\u0422\u042c\u00bb.</span></p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:14pt;\">\u0415\u0441\u043b\u0438 \u0432\u044b \u0445\u043e\u0442\u0438\u0442\u0435 \u043f\u0440\u043e\u0432\u0435\u0441\u0442\u0438 \u0430\u043d\u0430\u043b\u0438\u0437 \u0434\u043b\u044f \u0434\u0440\u0443\u0433\u043e\u0433\u043e \u043d\u0430\u0431\u043e\u0440\u0430 \u0434\u0430\u043d\u043d\u044b\u0445, \u0432\u043e\u0441\u043f\u043e\u043b\u044c\u0437\u0443\u0439\u0442\u0435\u0441\u044c \u043a\u043d\u043e\u043f\u043a\u043e\u0439 \u00ab\u0421\u0411\u0420\u041e\u0421\u00bb, \u0447\u0442\u043e\u0431\u044b \u043e\u0447\u0438\u0441\u0442\u0438\u0442\u044c \u0442\u0435\u043a\u0443\u0449\u0438\u0435 \u0440\u0435\u0437\u0443\u043b\u044c\u0442\u0430\u0442\u044b \u0438 \u043d\u0430\u0447\u0430\u0442\u044c \u043d\u043e\u0432\u044b\u0439 \u0440\u0430\u0441\u0447\u0435\u0442.<br /><br /></span>"
                        "<span style=\" font-size:14pt; font-weight:700;\">\u0410\u0432\u0442\u043e\u0440\u044b \u043f\u0440\u043e\u0433\u0440\u0430\u043c\u043c\u044b:</span><span style=\" font-size:14pt;\"> \u0427\u0435\u0440\u043d\u044f\u043a\u043e\u0432 \u041c.\u0421., \u041c\u0430\u0440\u043a\u043e\u0432\u0430 \u0410.\u0414.</span></p></body></html>", None))
        self.pushButton.setText(QCoreApplication.translate("Dialog", u"\u041e\u041a", None))
    # retranslateUi

