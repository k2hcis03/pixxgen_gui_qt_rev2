"""
2022-08-02
픽젠 GUI작업 시작
@K2H
"""
import os
import sys, time
from tkinter import messagebox
import init
   
from logger import logger as logging
from konfig import Config
from stepping_motor import SteppingMotor as STMOTOR
from dc_motor import DcMotor as DCMOTOR
from collimator import Collimator as COLLMOTOR
from uarts import Uarts as UARTS
from concurrent.futures import ThreadPoolExecutor 

from dialogs import PasswordDialog as password
from dialogs import ConfigDialog as configuration

from tcpserver import TcpServerThread as tcp_server

import sensor_timer
import threading
import queue
import position
import RPi.GPIO as GPIO

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
        self.collimator_rotate = 0
        # self.collimator_rotate_remote = 0
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setupUi(self)
        
        self.toggle_laser = False       #레이저 다이오드 온 오프 for 이미지 변환
        self.command_queue = None
        self.coll_laser = 0             #레이저 다이오드 1, 2, 온 오프 플래그
        # cc = Config("./config.ini")
        self.cc = Config("/home/pi/Projects/pixxgen_gui_qt/config.ini")      # For VSC
        motor_speed = self.cc.get_map('motor_speed')
        self.st1_max_speed = motor_speed['ST1MAXSPEED']
        self.st1_min_speed = motor_speed['ST1MINSPEED']
        self.st2_max_speed = motor_speed['ST2MAXSPEED']
        self.st2_min_speed = motor_speed['ST2MINSPEED']
        self.st3_max_speed = motor_speed['ST3MAXSPEED']
        self.st3_min_speed = motor_speed['ST3MINSPEED']
        self.coll1_max_speed = motor_speed['COLL1MAXSPEED']
        self.coll1_min_speed = motor_speed['COLL1MINSPEED']
        self.dc1_max_speed = motor_speed['DC1MAXSPEED']
        self.dc1_min_speed = motor_speed['DC1MINSPEED']

        self.motor_poistion = None
        self.motor_stopped = False
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
        self._lock = threading.Lock()
        
        self.motor_poistion = position.MotorPosition(self, self.command_queue, self.st_motor, self.init.gpio_i2c_parsing_data, 
                                                     self._lock, logging, self.uart_power1, self.uart_power2, self.init.dev_gpio_handle)
        self.motor_poistion.start()
        
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
        self.pushButton_mode.clicked.connect(self.set_mode)
        self.pushButton_exit.clicked.connect(self.exit_program)
        
        #  2024년 제네레이터 변경 기능 추가
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(20, GPIO.OUT)
        GPIO.output(20, GPIO.HIGH)
        self.pushButton_sel_gen.clicked.connect(self.select_generator)
        #
        self.pushButton_total_body.clicked.connect(self.total_body_sequence)
        # 첫번째 콜리미터 위치 이동
        self.coll_motor.coll_motor_start(1, True, self.coll1_min_speed, -288*10, True)  #288 = 90도
        time.sleep(2)
        
        self.server = tcp_server(self)
        self.server.start()         #tcp server시작
        # self.server.serve_forever()
        
    def chang_collimator(self):        
        self.collimator_rotate += 1
        self.collimator_rotate %= 4

        print(self.collimator_rotate)
        if self.collimator_rotate == 0:
            # 콜리미터 모터 초기 위치 설정
            self.enable_button(self.pushButton_select_colimator, False)
            self.coll_motor.coll_motor_start(1, True, self.coll1_min_speed, -288*10, True)  #288 = 90도
            time.sleep(2)
            self.collimator_rotate = 0
            self.enable_button(self.pushButton_select_colimator, True)
        # 다음 콜리미터 위치 이동
        else:
            self.enable_button(self.pushButton_select_colimator, False)
            self.coll_motor.coll_motor_start(1, True, self.coll1_max_speed, 288, False)  #288 = 90도
            time.sleep(1)
            self.enable_button(self.pushButton_select_colimator, True)
            
        button_border = f'QPushButton{{border: none;}}'
        button_choice = f'QPushButton{{background-image: url(:/images/m_collimator{self.collimator_rotate+1}_down.png)}}'
        self.pushButton_select_colimator.setStyleSheet(button_border + button_choice)
        logging.info(f'chang_collimator clicked : {self.collimator_rotate}')

    def chang_collimator_remote(self, rotate):        
        print(rotate)
        if rotate == 0:
            # 콜리미터 모터 초기 위치 설정
            self.enable_button(self.pushButton_select_colimator, False)
            self.coll_motor.coll_motor_start(1, True, self.coll1_max_speed, -288*10, True)  #288 = 90도
            time.sleep(1)
            self.collimator_rotate = 0
            self.enable_button(self.pushButton_select_colimator, True)
        # 다음 콜리미터 위치 이동
        else:
            diff = rotate - self.collimator_rotate
            self.enable_button(self.pushButton_select_colimator, False)

            if diff != 0:
                self.coll_motor.coll_motor_start(1, True, self.coll1_max_speed, 288*diff, False)  #288 = 90도
                self.collimator_rotate = rotate
            time.sleep(1)
            self.enable_button(self.pushButton_select_colimator, True)
            
        button_border = f'QPushButton{{border: none;}}'
        button_choice = f'QPushButton{{background-image: url(:/images/m_collimator{self.collimator_rotate+1}_down.png)}}'
        self.pushButton_select_colimator.setStyleSheet(button_border + button_choice)
        logging.info(f'chang_collimator clicked : {rotate}')
    
    def enable_button(self, button, enable):
        if enable:
            button.setEnabled(True)
        else:
            button.setDisabled(True)
               
    def move_motor_left_press(self, pressed):
        #if not self.motor_poistion.command_completed(): #명령어 처리가 없으면 동작
        logging.info(f'move_motor_left pressed : {pressed}')
        print('move_motor_left pressed', pressed)
        self.motor_poistion.set_command_stop(True)  #기존 동작 강제 스톱
        
        self.st_motor.st_motor_enable(1, False)
        self.st_motor.st_motor_start(1, False, 0, 0)
        
        if pressed:
            self.st_motor.st_motor_enable(1, True)
            self.st_motor.st_motor_start(1, True, self.st1_max_speed, -160000000)
        else:
            self.st_motor.st_motor_enable(1, False)
            self.st_motor.st_motor_start(1, False, 0, 0)

    def move_motor_right_press(self, pressed):
        #if not self.motor_poistion.command_completed(): #명령어 처리가 없으면 동작
        logging.info(f'move_motor_right pressed : {pressed}')
        print('move_motor_right pressed', pressed)
        self.motor_poistion.set_command_stop(True)  #기존 동작 강제 스톱
        
        self.st_motor.st_motor_enable(1, False)
        self.st_motor.st_motor_start(1, False, 0, 0)
        
        if pressed:
            self.st_motor.st_motor_enable(1, True)
            self.st_motor.st_motor_start(1, True, self.st1_max_speed, 160000000)
        else:
            self.st_motor.st_motor_enable(1, False)
            self.st_motor.st_motor_start(1, False, 0, 0)

    def move_motor_up_press(self, pressed):
        logging.info(f'move_motor_up pressed : {pressed}')
        print('move_motor_up_press pressed', pressed)
        self.motor_poistion.set_command_stop(True)  #기존 동작 강제 스톱
        
        self.st_motor.st_motor_enable(1, False)
        self.st_motor.st_motor_start(1, False, 0, 0)
            
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
        self.motor_poistion.set_command_stop(True)  #기존 동작 강제 스톱
        
        self.st_motor.st_motor_enable(1, False)
        self.st_motor.st_motor_start(1, False, 0, 0)
        
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
            # 레이저 1, 2 ON
            self.coll_laser = self.coll_laser & ~0x03
            self.coll_motor.coll_extout_start(6, self.coll_laser)
            
            self.toggle_laser = not self.toggle_laser
            button_border = f'QPushButton{{border: none;}}'
            button_choice = f'QPushButton{{background-image: url(:/images/3_off.png)}}'
            self.pushButton_laser.setStyleSheet(button_border + button_choice)
        else:
            # 레이저 1, 2 OFF
            self.coll_laser = self.coll_laser  | 0x03
            self.coll_motor.coll_extout_start(6, self.coll_laser) 
            self.toggle_laser = not self.toggle_laser
            button_border = f'QPushButton{{border: none;}}'
            button_choice = f'QPushButton{{background-image: url(:/images/3_on.png)}}'
            self.pushButton_laser.setStyleSheet(button_border + button_choice)
    
    def move_center_position(self):   
        logging.info(f'pushButton_move_center clicked')
        move_center = self.cc.get_map('move_center')
        loop = move_center['LOOP']
        
        for count in range(1, loop+1):
            message = {
                'position'  : move_center[f'POSITION{count}'],
                'speed'     : int(move_center[f'SPEED{count}']),
                'count'     : int(move_center[f'COUNT{count}']), 
                'timeout'   : int(move_center[f'TIMEOUT{count}'])   #1분
            }
            print(message)
            self.command_queue.put(message)
        self.motor_poistion.set_command_stop(False)  #큐를 시작할 수 있는 조건 FALSE
        
    def move_left_position(self):
        logging.info(f'pushButton_move_left clicked')
        move_left = self.cc.get_map('st_move_left')
        loop = move_left['LOOP']
        
        for count in range(1, loop+1):
            message = {
                'position'  : move_left[f'POSITION{count}'],
                'speed'     : int(move_left[f'SPEED{count}']),
                'count'     : int(move_left[f'COUNT{count}']), 
                'timeout'   : int(move_left[f'TIMEOUT{count}'])   #1분
            }
            print(message)
            self.command_queue.put(message)
        self.motor_poistion.set_command_stop(False) #큐를 시작할 수 있는 조건 FALSE
    
    def move_right_position(self):
        logging.info(f'pushButton_move_right clicked')
        move_left = self.cc.get_map('st_move_right')
        loop = move_left['LOOP']
        
        for count in range(1, loop+1):
            message = {
                'position'  : move_left[f'POSITION{count}'],
                'speed'     : int(move_left[f'SPEED{count}']),
                'count'     : int(move_left[f'COUNT{count}']), 
                'timeout'   : int(move_left[f'TIMEOUT{count}'])   #1분
            }
            print(message)
            self.command_queue.put(message)
        self.motor_poistion.set_command_stop(False) #큐를 시작할 수 있는 조건 FALSE
         
    def set_config(self):
        logging.info('set_config clicked')
        ret = password(self)
        config = configuration(self, self.init.gpio_i2c_parsing_data, self.dc_motor, 
                               self.uart_power1, self.uart_power2, self.init.dev_gpio_handle)
        # config.setWindowModality(Qt.ApplicationModal)
        config.setWindowModality(Qt.NonModal)
        
        if ret.exec():
            if ret.password == str(1234):           # 패스워드 확인
                config.show()
                config.start()
            else:
                QMessageBox.warning(self, "Warning", "Wrong Password")
        else:
            print('cancel')
    
    def set_mode(self):         #모터 정지 기능 수행 그림 변경 필요 
        # self.motor_poistion.set_command_stop(True)
        # # button_border = f'QPushButton{{border: none;}}'
        # # button_choice = f'QPushButton{{background-image: url(:/images/b_mode_down.png)}}'
        # self.motor_stopped = True
        # # time.sleep(0.01)
        # # 모터 스톱
        # self.st_motor.st_motor_enable(1, False)
        # self.st_motor.st_motor_start(1, False, 0, 0)
        # self.st_motor.st_motor_enable(2, False)
        # self.st_motor.st_motor_start(2, False, 0, 0)
        # self.st_motor.st_motor_enable(3, False)
        # self.st_motor.st_motor_start(3, False, 0, 0)
        # print(self.motor_stopped)        
        # self.pushButton_mode.setStyleSheet(button_border + button_choice)
        logging.info(f'pushButton_total_body clicked')
        mode_seq = self.cc.get_map('mode_seq')
        loop = mode_seq['LOOP']
        
        for count in range(1, loop+1):
            message = {
                'position'  : mode_seq[f'POSITION{count}'],
                'speed'     : int(mode_seq[f'SPEED{count}']),
                'count'     : int(mode_seq[f'COUNT{count}']), 
                'timeout'   : int(mode_seq[f'TIMEOUT{count}'])   #1분
            }
            print(message)
            self.command_queue.put(message)
            
        mode_seq = self.cc.get_map('xray_on')
        # loop = mode_seq['LOOP']
        message = {
            'position'  : mode_seq['POSITION'],
            'xray_num'  : int(mode_seq['XRAY_NUM']),
            'con_pulse' : int(mode_seq['CON_PULSE']),
            'kv'        : float(mode_seq['KV']),
            'ma'        : float(mode_seq['MA']), 
            'buzzer'    : int(mode_seq['BUZZER']),
            'time'      : float(mode_seq['TIME'])   #1분
        }
        print(message)
        self.command_queue.put(message)
        self.motor_poistion.set_command_stop(False) #큐를 시작할 수 있는 조건 FALSE
        
    def exit_program(self):
        self.timer1.thread_timer_gpio_read_stop()
        time.sleep(0.1)
        self.server.close_socket()
        QApplication.quit()
    
    def motor_buttons_disable(self, on_off):
        if on_off:
            self.pushButton_motor_left.setDisabled(True)
            self.pushButton_motor_right.setDisabled(True)
            self.pushButton_motor_up.setDisabled(True)
            self.pushButton_motor_down.setDisabled(True)      
            self.pushButton_move_center.setDisabled(True)
            self.pushButton_move_left.setDisabled(True)
        else:
            self.pushButton_motor_left.setEnabled(True)
            self.pushButton_motor_right.setEnabled(True)
            self.pushButton_motor_up.setEnabled(True)
            self.pushButton_motor_down.setEnabled(True)      
            self.pushButton_move_center.setEnabled(True)
            self.pushButton_move_left.setEnabled(True)
    
    def total_body_sequence(self):
        logging.info(f'pushButton_total_body clicked')
        move_total_body = self.cc.get_map('move_total_body')
        loop = move_total_body['LOOP']
        
        for count in range(1, loop+1):
            message = {
                'position'  : move_total_body[f'POSITION{count}'],
                'speed'     : int(move_total_body[f'SPEED{count}']),
                'count'     : int(move_total_body[f'COUNT{count}']), 
                'timeout'   : int(move_total_body[f'TIMEOUT{count}'])   #1분
            }
            print(message)
            self.command_queue.put(message)
        self.motor_poistion.set_command_stop(False) #큐를 시작할 수 있는 조건 FALSE
        
    # 20240402 제너레이터 선택 기능 추가
    def select_generator (self):
        if self.pushButton_sel_gen.text() == 'XRAY-2':
            GPIO.output(20, GPIO.HIGH)
            self.pushButton_sel_gen.setText('XRAY-1')
        else:
            GPIO.output(20, GPIO.LOW)
            self.pushButton_sel_gen.setText('XRAY-2')
        
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
