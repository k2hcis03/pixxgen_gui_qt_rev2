import define
import time

from PyQt5.QtCore import QThread
import threading
import queue
import fcntl
import user_ioctl
import ctypes

TIME_OUT = 1
SENSOR_DETECT = 2
COUNT_REACH = 3
FORCE_STOP = 4

class MotorPosition(threading.Thread):
    def __init__(self, parent, work_queue, st_motor, gpio_i2c_parsing_data,
                 _lock, logging, uart_power1, uart_power2, dev_gpio_handle) -> None:
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
        self.uart_power1 = uart_power1
        self.uart_power2 = uart_power2
        self.dev_gpio_handle = dev_gpio_handle
        
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
                    time.sleep(0.1)
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
                    time.sleep(0.1)  
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
                    time.sleep(0.1)
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
                    time.sleep(0.1)
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
                    time.sleep(0.1)
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
                    time.sleep(0.1)
                elif message['position'] == 'xray_on': 
                    self.logging.info('xray_on')  
                    completed = self.xray_on(message)
                    self.send_command = False       # 동작 완료
                    break;      
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
            motor3_count = int(count.readline())

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
            motor3_count = int(count.readline())

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
    
    def xray_on(self, message):
        if message['xray_num'] == 1:
            power_volt = "[XV{:04}]".format(int(float(message['kv']) * 10))
            self.uart_power1.send_serial(power_volt, None)
        else:
            power_volt = "[XV{:04}]".format(int(float(message['kv']) * 10))
            self.uart_power2.send_serial(power_volt, None)
        time.sleep(0.02)
        
        if message['xray_num'] == 1:
            power_current = "[XA{:03}]".format(int(float(message['ma'])))
            self.uart_power1.send_serial(power_current, None)
        else:
            power_current = "[XA{:03}]".format(int(float(message['ma'])))
            self.uart_power2.send_serial(power_current, None)
        time.sleep(0.02)
             
        if message['xray_num'] == 1:
            power_time = "[XT{:03}]".format(int(float(message['time']) * 10))
            self.uart_power1.send_serial(power_time, None)
        else:
            power_time = "[XT{:03}]".format(int(float(message['time']) * 10))
            self.uart_power2.send_serial(power_time, None)
        time.sleep(0.02)
        self.off_xray_power(message['xray_num'])
        
        time.sleep(0.1)
        self.on_xray_power(message['xray_num'], message)
        
        
    def on_xray_power(self, xray, message):
        if xray == 1:
            if message['con_pulse']:
                continuse_or_pulse_mode = "[XMC]"
            else:
                continuse_or_pulse_mode = "[XMP]"    
            
            if message['buzzer']:
                power_buz = "[XBON]"
            else:
                power_buz = "[XBOF]"
            
            self.uart_power1.send_serial(continuse_or_pulse_mode, None)
            time.sleep(0.02)
            self.uart_power1.send_serial(power_buz, None)
            time.sleep(0.02)
            
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
            if message['con_pulse']:
                continuse_or_pulse_mode = "[XMC]"
            else:
                continuse_or_pulse_mode = "[XMP]"    
            
            if message['buzzer']:
                power_buz = "[XBON]"
            else:
                power_buz = "[XBOF]"
            
            self.uart_power2.send_serial(continuse_or_pulse_mode, None)
            time.sleep(0.02)
            self.uart_power2.send_serial(power_buz, None)
            time.sleep(0.02)
            
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
            
    def off_xray_power(self, xray):
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
            
        