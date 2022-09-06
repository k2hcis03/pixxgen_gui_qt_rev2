"""
2022-08-02
픽젠 GUI작업 시작
@K2H
"""
import os
import sys
import threading, time

import fcntl
import user_ioctl
import ctypes

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
    def __init__(self, parent, gpio_i2c_parsing_data, dc_motor, uart_power1, uart_power2, dev_gpio_handle):
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
        self.dev_gpio_handle = dev_gpio_handle
        self.pushButton_OK.clicked.connect(self.ok_clicked)
        
        self.uart_power1 = uart_power1
        self.uart_power2 = uart_power2
        
        self.dc_motor = dc_motor
        self.pushButton_dc_motor_up.clicked.connect(self.move_dc_motor_up)
        self.pushButton_dc_motor_down.clicked.connect(self.move_dc_motor_down)
        
        self.pushButton_xray1_kv.clicked.connect(lambda: self.set_xray_kv(1))
        self.pushButton_xray2_kv.clicked.connect(lambda: self.set_xray_kv(2))
        
        self.pushButton_xray1_ma.clicked.connect(lambda: self.set_xray_ma(1))
        self.pushButton_xray2_ma.clicked.connect(lambda: self.set_xray_ma(2))
        
        self.pushButton_xray1_sec.clicked.connect(lambda: self.set_xray_sec(1))
        self.pushButton_xray2_sec.clicked.connect(lambda: self.set_xray_sec(2))
        
        self.pushButton_xray1_power_on.clicked.connect(lambda: self.on_xray_power(1))
        self.pushButton_xray2_power_on.clicked.connect(lambda: self.on_xray_power(1))
        
        self.pushButton_xray1_power_off.clicked.connect(lambda: self.off_xray_power(1))
        self.pushButton_xray2_power_off.clicked.connect(lambda: self.off_xray_power(1))
        
    def run(self):
        while(True):
            time.sleep(0.5)
            print('thread running')
            
            if self.gpio_i2c_parsing_data['step1_enc3'][2]:             #left limit sensor
                self.checkBox_st1_left.setCheckState(Qt.Checked)
            else:
                self.checkBox_st1_left.setCheckState(Qt.Unchecked)    
            
            if self.gpio_i2c_parsing_data['step1_enc1'][2]:             #right limit sensor
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
    
    def move_dc_motor_up(self):
        print('move_dc_motor_up')
        self.dc_motor.dc_motor_start(1, True, 100, -1000000, 1000)  #duty, 
        
    def move_dc_motor_down(self):
        print('move_dc_motor_down')
        self.dc_motor.dc_motor_start(1, True, 50, 1000000, 1000)  #duty, 
        
    def ok_clicked(self):
        self.thread_run = False
        self.close()
        
    def set_xray_kv(self, xray):
        try:
            if xray == 1:
                power_volt = "[XV{:04}]".format(int(float(self.lineEdit_xray1_kv.text()) * 10))
                self.uart_power1.send_serial(power_volt, self.lineEdit_xray1_status)
            elif xray == 2:
                power_volt = "[XV{:04}]".format(int(float(self.lineEdit_xray2_kv.text()) * 10))
                self.uart_power1.send_serial(power_volt, self.lineEdit_xray2_status)
        except ValueError as e:
            print('check value')
            
    def set_xray_ma(self, xray):
        try:
            if xray == 1:
                power_current = "[XA{:03}]".format(int(float(self.lineEdit_xray1_ma.text())))
                self.uart_power1.send_serial(power_current, self.lineEdit_xray1_status)
            elif xray == 2:
                power_current = "[XA{:03}]".format(int(float(self.lineEdit_xray2_ma.text())))
                self.uart_power1.send_serial(power_current, self.lineEdit_xray2_status)
        except ValueError as e:
            print('check value')
                       
    def set_xray_sec(self, xray):
        try:
            if xray == 1:
                power_time = "[XT{:03}]".format(int(float(self.lineEdit_xray1_time.text()) * 10))
                self.uart_power1.send_serial(power_time, self.lineEdit_xray1_status)
            elif xray == 2:
                power_time = "[XT{:03}]".format(int(float(self.lineEdit_xray2_time.text()) * 10))
                self.uart_power1.send_serial(power_time, self.lineEdit_xray2_status)
        except ValueError as e:
            print('check value')
            
    def on_xray_power(self, xray):
        if xray == 1:
            if self.radioButton_xray1_continue.isChecked():
                continuse_or_pulse_mode = "[XMC]"
            else:
                continuse_or_pulse_mode = "[XMP]"    
            
            if self.checkBox_xray1_buzzer.isChecked():
                power_buz = "[XBON]"
            else:
                power_buz = "[XBOF]"
            
            self.uart_power1.send_serial(continuse_or_pulse_mode, self.lineEdit_xray1_status)
            time.sleep(0.01)
            self.uart_power1.send_serial(power_buz, self.lineEdit_xray1_status)
            time.sleep(0.01)
            
            _ioctl = user_ioctl.IOCTLRequest()
            data = user_ioctl.StructIOCTL()
            
            for i in range(13):
                data.exout[i] = 0
            data.exout[user_ioctl.XRAY1_READY] = 1
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
            time.sleep(0.2)  
            
            data.exout[user_ioctl.XRAY1_ON] = 1
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
        else:
            if self.radioButton_xray2_continue.isChecked():
                continuse_or_pulse_mode = "[XMC]"
            else:
                continuse_or_pulse_mode = "[XMP]"    
            
            if self.checkBox_xray2_buzzer.isChecked():
                power_buz = "[XBON]"
            else:
                power_buz = "[XBOF]"
            
            self.uart_power2.send_serial(continuse_or_pulse_mode, self.lineEdit_xray2_status)
            time.sleep(0.01)
            self.uart_power2.send_serial(power_buz, self.lineEdit_xray2_status)
            time.sleep(0.01)
            
            _ioctl = user_ioctl.IOCTLRequest()
            data = user_ioctl.StructIOCTL()
            
            for i in range(13):
                data.exout[i] = 0
            data.exout[user_ioctl.XRAY2_READY] = 1
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
            time.sleep(0.2)  
            
            data.exout[user_ioctl.XRAY2_ON] = 1
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
            
    def onff_xray_power(self, xray):
        if xray == 1:
            _ioctl = user_ioctl.IOCTLRequest()
            data = user_ioctl.StructIOCTL()
            
            for i in range(13):
                data.exout[i] = 0
            data.exout[user_ioctl.XRAY1_ON] = 0
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
            time.sleep(0.5)  
            
            data.exout[user_ioctl.XRAY1_READY] = 0
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
        else:
            _ioctl = user_ioctl.IOCTLRequest()
            data = user_ioctl.StructIOCTL()
            
            for i in range(13):
                data.exout[i] = 0
            data.exout[user_ioctl.XRAY2_ON] = 0
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
            time.sleep(0.5)  
            
            data.exout[user_ioctl.XRAY2_READY] = 0
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)