"""
2022-08-02
픽젠 GUI작업 시작
@K2H
"""
import os
import sys
   
# from PySide6 import QtWidgets
# from PySide6.QtWidgets import QApplication, QMainWindow, QLineEdit, QDialog, QMessageBox, QWidget, QFontDialog
# from PySide6.QtGui import QPixmap, QIcon
# from PySide6.QtCore import Qt, QDir, QFileInfo
# from PySide6.QtUiTools import loadUiType
#
# ui, _ = loadUiType('./ui/main.ui')

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QDialog, QMessageBox, QWidget, QFontDialog
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QDir, QFileInfo
from PyQt5 import uic

# ui = uic.loadUiType("./ui/main.ui")[0]
ui = uic.loadUiType("/home/pi/Projects/pixxgen_gui_qt/ui/password.ui")[0]          # For VSC

class PasswordDialog(QDialog, ui):
    def __init__(self):
        super(PasswordDialog, self).__init__()
        # icon = QIcon("./asserts/bell.png")
        # self.setWindowIcon(icon)
        # self.setWindowFlag(Qt.FramelessWindowHint)
        self.setupUi(self)
        self.setWindowTitle('Password')
        self.pushButton_0.clicked.connect(lambda: self.input_password(0))
        self.pushButton_1.clicked.connect(lambda: self.input_password(1))
        self.pushButton_2.clicked.connect(lambda: self.input_password(2))
        self.pushButton_3.clicked.connect(lambda: self.input_password(3))
        self.pushButton_4.clicked.connect(lambda: self.input_password(4))
        self.pushButton_5.clicked.connect(lambda: self.input_password(5))
        self.pushButton_6.clicked.connect(lambda: self.input_password(6))
        self.pushButton_7.clicked.connect(lambda: self.input_password(7))
        self.pushButton_8.clicked.connect(lambda: self.input_password(8))
        self.pushButton_9.clicked.connect(lambda: self.input_password(9))
        self.pushButton_10.clicked.connect(lambda: self.input_password(10))
        self.pushButton_11.clicked.connect(lambda: self.input_password(11))
        
            
    def input_password(self, number):
        print(number)
