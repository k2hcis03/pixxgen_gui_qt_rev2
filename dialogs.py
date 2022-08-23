"""
2022-08-02
픽젠 GUI작업 시작
@K2H
"""
import os
import sys
import threading, time

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
ui_password = uic.loadUiType("/home/pi/Projects/pixxgen_gui_qt/ui/password.ui")[0]          # For VSC
ui_config = uic.loadUiType("/home/pi/Projects/pixxgen_gui_qt/ui/config.ui")[0]              # For VSC

class PasswordDialog(QDialog, ui_password):
    def __init__(self, parent):
        super(PasswordDialog, self).__init__(parent)
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
        
        self.password = None
        
    def input_password(self, number):
        print(number)
        if number < 10:
            self.lineEdit_password.insert(str(number))
            self.password = self.lineEdit_password.text()
        elif number == 10:              #back space
            self.lineEdit_password.backspace()
        elif number == 11:              # clear
            self.lineEdit_password.clear()

class ConfigDialog(QDialog, ui_config, threading.Thread):
    def __init__(self, parent, gpio_i2c_parsing_data):
        super(ConfigDialog, self).__init__(parent)
        threading.Thread.__init__(self)
        # icon = QIcon("./asserts/bell.png")
        # self.setWindowIcon(icon)
        # self.setWindowFlag(Qt.FramelessWindowHint)
        self.setupUi(self)
        self.setWindowTitle('Config')
        self.daemon = True
        self.thread_run = True
        self.gpio_i2c_parsing_data = gpio_i2c_parsing_data
        self.pushButton_OK.clicked.connect(self.ok_clicked)
         
    def run(self):
        while(True):
            time.sleep(0.5)
            print('thread running')
            
            if self.gpio_i2c_parsing_data['step1_enc1'][2]:             #left limit sensor
                self.checkBox_st1_left.setCheckState(Qt.Checked)
            else:
                self.checkBox_st1_left.setCheckState(Qt.Unchecked)    
            
            if self.gpio_i2c_parsing_data['step1_enc3'][2]:             #right limit sensor
                self.checkBox_st1_right.setCheckState(Qt.Checked)
            else:
                self.checkBox_st1_right.setCheckState(Qt.Unchecked) 
                
            if self.gpio_i2c_parsing_data['step2_enc1'][2]:             #left limit sensor
                self.checkBox_st2_left.setCheckState(Qt.Checked)
            else:
                self.checkBox_st2_left.setCheckState(Qt.Unchecked) 
            
            if self.gpio_i2c_parsing_data['step2_enc3'][2]:             #right limit sensor
                self.checkBox_st2_right.setCheckState(Qt.Checked)
            else:
                self.checkBox_st2_right.setCheckState(Qt.Unchecked) 
                
            if self.gpio_i2c_parsing_data['step3_enc1'][2]:             #left limit sensor
                self.checkBox_st3_left.setCheckState(Qt.Checked)
            else:
                self.checkBox_st3_left.setCheckState(Qt.Unchecked) 
            
            if self.gpio_i2c_parsing_data['step3_enc2'][2]:             #right limit sensor
                self.checkBox_st3_right.setCheckState(Qt.Checked)
            else:
                self.checkBox_st3_right.setCheckState(Qt.Unchecked) 
                
            if self.gpio_i2c_parsing_data['step4_enc1'][2]:             #left limit sensor
                self.checkBox_coll_left.setCheckState(Qt.Checked)
            else:
                self.checkBox_coll_left.setCheckState(Qt.Unchecked) 
            
            if self.gpio_i2c_parsing_data['step4_enc2'][2]:             #right limit sensor
                self.checkBox_coll_right.setCheckState(Qt.Checked)
            else:
                self.checkBox_coll_right.setCheckState(Qt.Unchecked) 
                  
            if self.gpio_i2c_parsing_data['dc1_enc1'][2]:               #left limit sensor
                self.checkBox_dc1_left.setCheckState(Qt.Checked)
            else:
                self.checkBox_dc1_left.setCheckState(Qt.Unchecked) 
            
            if self.gpio_i2c_parsing_data['dc1_enc2'][2]:               #right limit sensor
                self.checkBox_dc1_right.setCheckState(Qt.Checked)
            else:
                self.checkBox_dc1_right.setCheckState(Qt.Unchecked) 
                   
            if not self.thread_run:
                break
    
    def ok_clicked(self):
        self.thread_run = False
        self.close()