import define
import time

from PyQt5.QtCore import QThread
import threading

class MotorPosition(threading.Thread):
    def __init__(self, parent, queue, st_motor, gpio_i2c_parsing_data, logging) -> None:
        threading.Thread.__init__(self)
        self.queue = queue
        self.st_motor = st_motor
        self.gpio_i2c_parsing_data = gpio_i2c_parsing_data
        self.logging = logging
        self.send_command = False
        self.motor_centor_count = 100000
        self.daemon = True
        self.timeout = 0
        
    def run(self):
        while True:
            message = self.queue.get()
       
            while True:
                if message['position'] == 'left':
                    completed = self.move_left_position(message)
                    
                    if completed > 0:
                        self.logging.info('move_left_position completed')
                        self.send_command = False
                        break
                    elif completed < 0:
                        self.logging.info('move_left_position time out!')
                        self.send_command = False
                        break
                elif message['position'] == 'right': 
                    completed = self.move_right_position(message)
                    
                    if completed > 0:
                        self.logging.info('move_right_position completed')
                        self.send_command = False
                        break
                    elif completed < 0:
                        self.logging.info('move_right_position time out!')
                        self.send_command = False
                        break
                
    def move_left_position(self, message) -> int:    #1을 리턴하면 위치 도착 0을 리턴하면 이동 중. 
        if self.gpio_i2c_parsing_data['step1_enc3'][2]:
            self.send_command = False
            return 1

        if not self.send_command:
            self.timeout = time.time()
            self.st_motor.st_motor_enable(1, True)
            self.st_motor.st_motor_start(1, True, message['speed'], message['count'])
            self.send_command = True
        
        if time.time() - self.timeout >= message['timeout']:
            return -1
        
        return 0
    
    def move_right_position(self, message) -> int:    #1을 리턴하면 위치 도착 0을 리턴하면 이동 중.
        if self.gpio_i2c_parsing_data['step1_enc1'][2]:
            self.send_command = False
            return 1
        
        if not self.send_command:
            self.timeout = time.time()
            self.st_motor.st_motor_enable(1, True)
            self.st_motor.st_motor_start(1, True, message['speed'], message['count'])
            self.send_command = True
        
        if time.time() - self.timeout >= message['timeout']:
            return -1
        
        return 0

    def move_center_position(self, message):
        if not self.send_command:
            self.st_motor.st_motor_enable(1, True)
            self.st_motor.st_motor_start(1, True, message['max_speed'], self.motor_centor_count)
            self.send_command = True
