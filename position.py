import define
import time

from PyQt5.QtCore import QThread
import threading
import queue

TIME_OUT = 1
SENSOR_DETECT = 2
COUNT_REACH = 3
FORCE_STOP = 4

class MotorPosition(threading.Thread):
    def __init__(self, parent, work_queue, st_motor, gpio_i2c_parsing_data, _lock, logging) -> None:
        threading.Thread.__init__(self)
        self.command_queue = work_queue
        self.st_motor = st_motor
        self.gpio_i2c_parsing_data = gpio_i2c_parsing_data
        self.logging = logging
        self.send_command = False
        self.motor_centor_count = 100000
        self.daemon = True
        self.timeout = 0
        self._lock = _lock
        self.not_doing_work = False
        
    def run(self):
        while True:
            message = self.command_queue.get()
       
            while True:
                if message['position'] == 'st_left':
                    completed = self.st_move_left_position(message)
                    
                    if completed == SENSOR_DETECT:
                        self.logging.info('st_move_left_position completed by sensor')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == COUNT_REACH:
                        self.logging.info('st_move_left_position completed by counter')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == TIME_OUT:
                        self.logging.info('st_move_left_position time out!')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == FORCE_STOP:
                        self.logging.info('st_move_left_position stopped by force')
                        self.send_command = False       # 동작 완료
                        break
                elif message['position'] == 'st_right':
                    completed = self.st_move_right_position(message)
                    
                    if completed == SENSOR_DETECT:
                        self.logging.info('st_move_right_position completed by sensor')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == COUNT_REACH:
                        self.logging.info('st_move_right_position completed by counter')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == TIME_OUT:
                        self.logging.info('st_move_right_position time out!')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == FORCE_STOP:
                        self.logging.info('st_move_right_position stopped by force')
                        self.send_command = False       # 동작 완료
                        break
                      
                elif message['position'] == 'st_up': 
                    completed = self.st_move_up_position(message)
                    
                    if completed == SENSOR_DETECT:
                        self.logging.info('st_move_up_position completed by sensor')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == COUNT_REACH:
                        self.logging.info('st_move_up_position completed by counter')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == TIME_OUT:
                        self.logging.info('st_move_up_position time out!')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == FORCE_STOP:
                        self.logging.info('st_move_up_position stopped by force')
                        self.send_command = False       # 동작 완료
                        break
                
                elif message['position'] == 'st_down': 
                    completed = self.st_move_down_position(message)
                    
                    if completed == SENSOR_DETECT:
                        self.logging.info('st_move_down_position completed by sensor')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == COUNT_REACH:
                        self.logging.info('st_move_down_position completed by counter')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == TIME_OUT:
                        self.logging.info('st_move_down_position time out!')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == FORCE_STOP:
                        self.logging.info('st_move_down_position stopped by force')
                        self.send_command = False       # 동작 완료
                        break    
                
                elif message['position'] == 'dc_down': 
                    completed = self.dc_move_down_position(message)
                    
                    if completed == SENSOR_DETECT:
                        self.logging.info('dc_move_down_position completed by sensor')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == COUNT_REACH:
                        self.logging.info('dc_move_down_position completed by counter')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == TIME_OUT:
                        self.logging.info('dc_move_down_position time out!')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == FORCE_STOP:
                        self.logging.info('dc_move_down_position stopped by force')
                        self.send_command = False       # 동작 완료
                        break
                elif message['position'] == 'dc_up': 
                    completed = self.dc_move_up_position(message)
                    
                    if completed == SENSOR_DETECT:
                        self.logging.info('dc_move_up_position completed by sensor')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == COUNT_REACH:
                        self.logging.info('dc_move_up_position completed by counter')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == TIME_OUT:
                        self.logging.info('dc_move_up_position time out!')
                        self.send_command = False       # 동작 완료
                        break
                    elif completed == FORCE_STOP:
                        self.logging.info('dc_move_up_position stopped by force')
                        self.send_command = False       # 동작 완료
                        break
                            
    def st_move_left_position(self, message) -> int:    #1을 리턴하면 위치 도착 0을 리턴하면 이동 중. 
        if self.gpio_i2c_parsing_data['step1_enc3'][2]:
            return SENSOR_DETECT

        if not self.send_command:
            self.timeout = time.time()
            self.st_motor.st_motor_enable(1, True)
            self.st_motor.st_motor_start(1, True, message['speed'], -1*message['count'])
            self.send_command = True
        
        if time.time() - self.timeout >= message['timeout']:
            return TIME_OUT
        
        if self.not_doing_work:
            return FORCE_STOP

        with open('/sys/bus/platform/drivers/pixggen_gpio/equipment/pixxgen_sys/counter1') as count:
            motor_count = int(count.readline())
            
            if motor_count == 0:
                return 2
        return 0
    
    def st_move_right_position(self, message) -> int:    #1을 리턴하면 위치 도착 0을 리턴하면 이동 중.
        if self.gpio_i2c_parsing_data['step1_enc1'][2]:
            return SENSOR_DETECT
        
        if not self.send_command:
            self.timeout = time.time()
            self.st_motor.st_motor_enable(1, True)
            self.st_motor.st_motor_start(1, True, message['speed'], message['count'])
            self.send_command = True
        
        if time.time() - self.timeout >= message['timeout']:
            return TIME_OUT
        
        if self.not_doing_work:
            return FORCE_STOP
        
        with open('/sys/bus/platform/drivers/pixggen_gpio/equipment/pixxgen_sys/counter1') as count:
            motor_count = int(count.readline())
            
            if motor_count == 0:
                return COUNT_REACH
        return 0

    def move_center_position(self, message):
        if not self.send_command:
            self.st_motor.st_motor_enable(1, True)
            self.st_motor.st_motor_start(1, True, message['max_speed'], self.motor_centor_count)
            self.send_command = True

    def st_move_up_position(self, message) -> int:    #1을 리턴하면 위치 도착 0을 리턴하면 이동 중.
        motor2_count = -1
        motor3_count = -1
        
        if self.gpio_i2c_parsing_data['step2_enc1'][2] and self.gpio_i2c_parsing_data['step3_enc1'][2]:
            return SENSOR_DETECT
        
        if not self.send_command:
            self.timeout = time.time()
            self.st_motor.st_motor_enable(2, True)
            self.st_motor.st_motor_enable(3, True)
            self.st_motor.st_motor_start(2, True, message['speed'], message['count'])
            self.st_motor.st_motor_start(3, True, message['speed'], message['count'])
            self.send_command = True
        
        if time.time() - self.timeout >= message['timeout']:
            return TIME_OUT
        
        if self.not_doing_work:
            return FORCE_STOP
        
        with open('/sys/bus/platform/drivers/pixggen_gpio/equipment/pixxgen_sys/counter2') as count:
            motor2_count = int(count.readline())
            
        with open('/sys/bus/platform/drivers/pixggen_gpio/equipment/pixxgen_sys/counter3') as count:
            motor_count = int(count.readline())

        if motor2_count == 0 and motor3_count == 0:
            return COUNT_REACH
        return 0
    
    def st_move_down_position(self, message) -> int:    #1을 리턴하면 위치 도착 0을 리턴하면 이동 중.
        motor2_count = -1
        motor3_count = -1
        
        if self.gpio_i2c_parsing_data['step2_enc2'][2] or self.gpio_i2c_parsing_data['step3_enc2'][2]:  # 모터 3번이 2번보다 길이가 짧으므로 OR조건으로 설정
            return SENSOR_DETECT
        
        if not self.send_command:
            self.timeout = time.time()
            self.st_motor.st_motor_enable(2, True)
            self.st_motor.st_motor_enable(3, True)
            self.st_motor.st_motor_start(2, True, message['speed'], -1*message['count'])
            self.st_motor.st_motor_start(3, True, message['speed'], -1*message['count'])
            self.send_command = True
        
        if time.time() - self.timeout >= message['timeout']:
            return TIME_OUT
        
        if self.not_doing_work:
            return FORCE_STOP
        
        with open('/sys/bus/platform/drivers/pixggen_gpio/equipment/pixxgen_sys/counter2') as count:
            motor2_count = int(count.readline())
            
        with open('/sys/bus/platform/drivers/pixggen_gpio/equipment/pixxgen_sys/counter3') as count:
            motor_count = int(count.readline())

        if motor2_count == 0 or motor3_count == 0:      # 모터 3번이 2번보다 길이가 짧으므로 OR조건으로 설정
            return COUNT_REACH
        return 0
    
    def dc_move_down_position(self, message) -> int:    #1을 리턴하면 위치 도착 0을 리턴하면 이동 중.
        if self.gpio_i2c_parsing_data['dc1_enc1'][2]:  
            return SENSOR_DETECT
        
        if not self.send_command:
            self.timeout = time.time()
            self.dc_motor.dc_motor_start(1, True, message['speed'], message['count'], 1000)  #duty, 
            self.send_command = True
        
        if time.time() - self.timeout >= message['timeout']:
            return TIME_OUT
        
        if self.not_doing_work:
            return FORCE_STOP

        return 0
    
    def dc_move_up_position(self, message) -> int:    #1을 리턴하면 위치 도착 0을 리턴하면 이동 중.
        if self.gpio_i2c_parsing_data['dc1_enc2'][2]:  
            return SENSOR_DETECT
        
        if not self.send_command:
            self.timeout = time.time()
            self.dc_motor.dc_motor_start(1, True, message['speed'], -1*message['count'], 1000)  #duty, 
            self.send_command = True
        
        if time.time() - self.timeout >= message['timeout']:
            return TIME_OUT
        
        if self.not_doing_work:
            return FORCE_STOP

        return 0
    
    def set_command_stop(self, on_off):
        self.not_doing_work = on_off
        
        #강제 스톱이 오면 큐를 비운다.
        if on_off:
            while True:
                try:
                    message = self.command_queue.get(False)
                except queue.Empty:
                    self.logging.info('명령어 큐를 모두 비움')
                    break
                else:
                    self.logging.info('명령어 큐에 명령어가 있음')
    
    def command_completed(self):
        return self.send_command                
            
        