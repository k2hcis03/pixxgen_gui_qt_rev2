"""
2022-08-02
픽젠 GUI작업 시작
@K2H
"""
import os
import sys
import init
   
from logger import logger as logging
from konfig import Config
from stepping_motor import SteppingMotor as STMOTOR
from dc_motor import DcMotor as DCMOTOR
from collimator import Collimator as COLLMOTOR
from uarts import Uarts as UARTS
from concurrent.futures import ThreadPoolExecutor 

from dialogs import PasswordDialog as password
import sensor_timer
import threading
import queue
import position
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
ui = uic.loadUiType("/home/pi/Projects/pixxgen_gui_qt/ui/main.ui")[0]          # For VSC

class MainWindow(QMainWindow, ui):
    def __init__(self):
        super(MainWindow, self).__init__()
        # icon = QIcon("./asserts/bell.png")
        # self.setWindowTitle('AVG Antivirus Free')
        # self.setWindowIcon(icon)
        self.collimator_rotate = 1
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setupUi(self)
        
        self.toggle_laser = False       #레이저 다이오드 온 오프
        self.command_queue = None
        
        # cc = Config("./config.ini")
        cc = Config("/home/pi/Projects/pixxgen_gui_qt/config.ini")      # For VSC
        motor_speed = cc.get_map('motor_speed')
        self.st1_max_speed = motor_speed['ST1MAXSPEED']
        self.st1_min_speed = motor_speed['ST1MINSPEED']
        self.st2_max_speed = motor_speed['ST2MAXSPEED']
        self.st2_min_speed = motor_speed['ST2MINSPEED']
        self.st3_max_speed = motor_speed['ST3MAXSPEED']
        self.st3_min_speed = motor_speed['ST3MINSPEED']
        self.dc1_max_speed = motor_speed['DC1MAXSPEED']
        self.dc1_min_speed = motor_speed['DC1MINSPEED']

        # 하드웨어 초기화
        self.init = init.HardwareInit(logging)
        
        if self.init.init_done:
            self.st_motor = STMOTOR(self.init.dev_gpio_handle, self.init.gpio_i2c_datas, self.init.gpio_i2c_parsing_data
                                    , logging)
            self.dc_motor = DCMOTOR(self.init.dev_gpio_handle, self.init.gpio_i2c_datas, self.init.gpio_i2c_parsing_data
                                   , logging)
            self.coll_motor = COLLMOTOR(self.init.dev_gpio_handle, logging)
            self.uart_power1 = UARTS(self.init.dev_gpio_handle, "/dev/ttyAMA2", 9600, logging)
            self.uart_power2 = UARTS(self.init.dev_gpio_handle, "/dev/ttyAMA3", 9600, logging)
            self.uart_power1.start()
            self.uart_power2.start()
        
            self.timer1 = sensor_timer.GPIORead(self.init.dev_gpio_handle, self.init.gpio_i2c_datas,
                                                 self.init.gpio_i2c_parsing_data, self.st_motor, 
                                                 self.dc_motor, logging, self)
            self.timer1.thread_timer_gpio_read_start()
        else:
            logging.info('하드웨어 초기화 실패')

        
        # 모터 포시션 움직이는 쓰레드 생성
        # with ThreadPoolExecutor(max_workers=1) as executor:
        #     logging.info('MotorPosition thread is created')
        #     command = queue.Queue(maxsize=10)
        #     motor_poistion = position.MotorPosition(command, self.st_motor, self.init.gpio_i2c_parsing_data, logging)
        #     executor.submit(motor_poistion.manager_motor_position)
        
        logging.info('MotorPosition thread is created')
        self.command_queue = queue.Queue(maxsize=10)
        motor_poistion = position.MotorPosition(self, self.command_queue, self.st_motor, self.init.gpio_i2c_parsing_data, logging)
        motor_poistion.start()
        
        self.pushButton_select_colimator.clicked.connect(self.chang_collimator)

        self.pushButton_motor_left.pressed.connect(lambda: self.move_motor_left_press(1))
        self.pushButton_motor_left.released.connect(lambda: self.move_motor_left_press(0))

        self.pushButton_motor_right.pressed.connect(lambda: self.move_motor_right_press(1))
        self.pushButton_motor_right.released.connect(lambda: self.move_motor_right_press(0))

        self.pushButton_motor_up.pressed.connect(lambda: self.move_motor_up_press(1))
        self.pushButton_motor_up.released.connect(lambda: self.move_motor_up_press(0))

        self.pushButton_motor_down.pressed.connect(lambda: self.move_motor_down_press(1))
        self.pushButton_motor_down.released.connect(lambda: self.move_motor_down_press(0))

        self.pushButton_laser.clicked.connect(self.on_off_laser)
        
        self.pushButton_move_center.clicked.connect(self.move_center_position)
        self.pushButton_move_left.clicked.connect(self.move_left_position)
        self.pushButton_setting.clicked.connect(self.set_config)
        
        
    def chang_collimator(self):
        self.collimator_rotate += 1
        self.collimator_rotate %= 5

        if self.collimator_rotate == 0:
            self.collimator_rotate = 1

        collimator_border = f'QPushButton{{border: none;}}'
        collimator_choice = f'QPushButton{{background-image: url(:/images/m_collimator{self.collimator_rotate}_down.png)}}'
        self.pushButton_select_colimator.setStyleSheet(collimator_border + collimator_choice)

    def move_motor_left_press(self, pressed):
        logging.info(f'move_motor_left pressed : {pressed}')
        print('move_motor_left pressed', pressed)

        if pressed:
            self.st_motor.st_motor_enable(1, True)
            self.st_motor.st_motor_start(1, True, self.st1_max_speed, -160000000)
        else:
            self.st_motor.st_motor_enable(1, False)
            self.st_motor.st_motor_start(1, False, 0, 0)

    def move_motor_right_press(self, pressed):
        logging.info(f'move_motor_right pressed : {pressed}')
        print('move_motor_right pressed', pressed)

        if pressed:
            self.st_motor.st_motor_enable(1, True)
            self.st_motor.st_motor_start(1, True, self.st1_max_speed, 160000000)
        else:
            self.st_motor.st_motor_enable(1, False)
            self.st_motor.st_motor_start(1, False, 0, 0)

    def move_motor_up_press(self, pressed):
        logging.info(f'move_motor_up pressed : {pressed}')
        print('move_motor_up_press pressed', pressed)

        if pressed:
            self.st_motor.st_motor_enable(2, True)
            self.st_motor.st_motor_enable(3, True)
            self.st_motor.st_motor_start(2, True, self.st2_max_speed, 160000000)
            self.st_motor.st_motor_start(3, True, self.st3_max_speed, 160000000)
        else:
            self.st_motor.st_motor_enable(2, False)
            self.st_motor.st_motor_enable(3, False)
            self.st_motor.st_motor_start(2, False, 0, 0)
            self.st_motor.st_motor_start(3, False, 0, 0)
            
    def move_motor_down_press(self, pressed):
        logging.info(f'move_motor_down pressed : {pressed}')
        print('move_motor_down_press pressed', pressed)

        if pressed:
            self.st_motor.st_motor_enable(2, True)
            self.st_motor.st_motor_enable(3, True)
            self.st_motor.st_motor_start(2, True, self.st2_max_speed, -160000000)
            self.st_motor.st_motor_start(3, True, self.st3_max_speed, -160000000)
        else:
            self.st_motor.st_motor_enable(2, False)
            self.st_motor.st_motor_enable(3, False)
            self.st_motor.st_motor_start(2, False, 0, 0)
            self.st_motor.st_motor_start(3, False, 0, 0)

    def on_off_laser(self):
        logging.info(f'pushButton_laser clicked : {self.toggle_laser}')
        
        if self.toggle_laser:
            self.toggle_laser = not self.toggle_laser
            collimator_border = f'QPushButton{{border: none;}}'
            collimator_choice = f'QPushButton{{background-image: url(:/images/3_off.png)}}'
            self.pushButton_laser.setStyleSheet(collimator_border + collimator_choice)
        else:
            self.toggle_laser = not self.toggle_laser
            collimator_border = f'QPushButton{{border: none;}}'
            collimator_choice = f'QPushButton{{background-image: url(:/images/3_on.png)}}'
            self.pushButton_laser.setStyleSheet(collimator_border + collimator_choice)
    
    def move_center_position(self):
        logging.info(f'pushButton_move_center clicked')
    
    def move_left_position(self):
        logging.info(f'pushButton_move_left clicked')
        message = {
            'position'  : 'left',
            'speed'     : 1000,
            'count'     : 0, 
            'timeout'   : 60*1000
        }
        self.command_queue.put(message)
    
    def set_config(self):
        logging.info('set_config clicked')
        ret = password()
        
        if ret.exec():
            print('Success')
        else:
            print('Cancel!')
        
def main():
    app = QApplication(sys.argv)
    windows = MainWindow()
    windows.show()
    
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print('Exiting')


if __name__ == '__main__':
    main()
