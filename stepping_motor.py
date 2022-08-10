import define
import time
# from ioctl import IOCTL
import fcntl
import user_ioctl
import ctypes


class SteppingMotor:
    def __init__(self, dev_gpio, gpio_i2c_datas, gpio_i2c_parsing_data, logging):
        print("Steppingmotor Class Init")
        self.dev_gpio = dev_gpio['dev_gpio']
        self.dev_gpio_i2c_0 = dev_gpio['dev_gpio_i2c_0']
        self.dev_gpio_i2c_1 = dev_gpio['dev_gpio_i2c_1']

        self.gpio_i2c_datas = gpio_i2c_datas
        self.gpio_i2c_parsing_data = gpio_i2c_parsing_data
        
        # self.CW = 1
        # self.CCW = 2
        # self.STOP = 3
        
        self.motor1_dir = self.motor2_dir = self.motor3_dir = self.motor4_dir = define.CW
        self.st_motor_enable(1, 0)
        self.st_motor_enable(2, 0)
        self.st_motor_enable(3, 0)
        self.st_motor_enable(4, 0)

        self.logging = logging

    def st_motor_enable(self, motor_number, enable):
        if motor_number == 1:
            if enable == True:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_a'] = self.gpio_i2c_datas['gpio_i2c_1_output_a'] & ~0x08
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_a']
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_a'] = self.gpio_i2c_datas['gpio_i2c_1_output_a'] | 0x08
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_a']
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)
        elif motor_number == 2:
            if enable == True:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_a'] = self.gpio_i2c_datas['gpio_i2c_1_output_a'] & ~0x10
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_a']
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_a'] = self.gpio_i2c_datas['gpio_i2c_1_output_a'] | 0x10
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_a']               
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)
        elif motor_number == 3: 
            if enable == True:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_a'] = self.gpio_i2c_datas['gpio_i2c_1_output_a'] & ~0x20
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_a']                
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_a'] = self.gpio_i2c_datas['gpio_i2c_1_output_a'] | 0x20
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_a']                
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)   
        elif motor_number == 4: 
            if enable == True:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_B, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_b'] = self.gpio_i2c_datas['gpio_i2c_1_output_b'] | 0x02
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_b']                
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_b'] = self.gpio_i2c_datas['gpio_i2c_1_output_b'] & ~0x02
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_b']                
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)  

    def st_motor_dir(self, motor_number, dir):
        if motor_number == 1:
            if dir == define.CW:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_a'] = self.gpio_i2c_datas['gpio_i2c_1_output_a'] & ~0x01
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_a']  
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)
                self.motor1_dir = define.CW
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_a'] = self.gpio_i2c_datas['gpio_i2c_1_output_a'] | 0x01
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_a']  
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)
                self.motor1_dir = define.CCW
        elif motor_number == 2:
            if dir == define.CW:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_a'] = self.gpio_i2c_datas['gpio_i2c_1_output_a'] & ~0x02
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_a']  
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)
                self.motor2_dir = define.CW
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_a'] = self.gpio_i2c_datas['gpio_i2c_1_output_a'] | 0x02
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_a']  
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)
                self.motor2_dir = define.CCW
        elif motor_number == 3: 
            if dir == define.CW:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_a'] = self.gpio_i2c_datas['gpio_i2c_1_output_a'] & ~0x04
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_a']  
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)
                self.motor3_dir = define.CW
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_a'] = self.gpio_i2c_datas['gpio_i2c_1_output_a'] | 0x04
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_a']  
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)  
                self.motor3_dir = define.CCW  
        elif motor_number == 4: 
            if dir == define.CW:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_a'] = self.gpio_i2c_datas['gpio_i2c_1_output_a'] & ~0x40
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_a']  
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)
                self.motor4_dir = define.CW
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_I2C_GPIO_A, ctypes.sizeof(data))
                self.gpio_i2c_datas['gpio_i2c_1_output_a'] = self.gpio_i2c_datas['gpio_i2c_1_output_a'] | 0x40
                data.gpio_i2c_out_a = self.gpio_i2c_datas['gpio_i2c_1_output_a']  
                fcntl.ioctl(self.dev_gpio_i2c_1, SET_DATA, data)  
                self.motor4_dir = define.CCW   

    def st_motor_start(self, st_motor_number, start, speed, count):
        if st_motor_number == 1:
            if start == True:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.START_STEP_MOTOR1, ctypes.sizeof(data))
                
                if count < 0:
                    self.st_motor_dir(1, define.CCW)
                else:
                    self.st_motor_dir(1, define.CW)
                if self.motor1_dir == define.CW and self.gpio_i2c_parsing_data['step1_enc1'][2] == 1:
                    return
                if self.motor1_dir == define.CCW and self.gpio_i2c_parsing_data['step1_enc3'][2] == 1:
                    return
                data.st_motor_speed = speed
                data.st_motor_count = abs(count)
                fcntl.ioctl(self.dev_gpio, SET_DATA, data)
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.STOP_STEP_MOTOR1, ctypes.sizeof(data))
                data.st_motor_speed = 0
                data.st_motor_count = 0
                
                if self.motor1_dir != define.STOP:
                    self.motor1_dir = define.STOP
                    fcntl.ioctl(self.dev_gpio, SET_DATA, data)
        elif st_motor_number == 2:
            if start == True:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.START_STEP_MOTOR2, ctypes.sizeof(data))
                
                if count < 0:
                    self.st_motor_dir(2, define.CCW)
                else:
                    self.st_motor_dir(2, define.CW)
                if self.motor2_dir == define.CW and self.gpio_i2c_parsing_data['step2_enc1'][2] == 1:
                    return
                if self.motor2_dir == define.CCW and self.gpio_i2c_parsing_data['step2_enc3'][2] == 1:
                    return
                data.st_motor_speed = speed
                data.st_motor_count = abs(count)
                fcntl.ioctl(self.dev_gpio, SET_DATA, data)
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.STOP_STEP_MOTOR2, ctypes.sizeof(data))
                data.st_motor_speed = 0
                data.st_motor_count = 0
                
                if self.motor2_dir != define.STOP:
                    self.motor2_dir = define.STOP
                    fcntl.ioctl(self.dev_gpio, SET_DATA, data)
        elif st_motor_number == 3: 
            if start == True:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.START_STEP_MOTOR3, ctypes.sizeof(data))
                
                if count < 0:
                    self.st_motor_dir(3, define.CCW)
                else:
                    self.st_motor_dir(3, define.CW)
                if self.motor3_dir == define.CW and self.gpio_i2c_parsing_data['step3_enc1'][2] == 1:
                    return
                if self.motor3_dir == define.CCW and self.gpio_i2c_parsing_data['step3_enc2'][2] == 1:
                    return                
                data.st_motor_speed = speed
                data.st_motor_count = abs(count)
                fcntl.ioctl(self.dev_gpio, SET_DATA, data)
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.STOP_STEP_MOTOR3, ctypes.sizeof(data))
                data.st_motor_speed = 0
                data.st_motor_count = 0
                
                if self.motor3_dir != define.STOP:
                    self.motor3_dir = define.STOP
                    fcntl.ioctl(self.dev_gpio, SET_DATA, data)   
        elif st_motor_number == 4: 
            if start == True:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.START_STEP_MOTOR4, ctypes.sizeof(data))
                
                if count < 0:
                    self.st_motor_dir(4, define.CCW)
                else:
                    self.st_motor_dir(4, define.CW)
                if self.motor4_dir == define.CW and self.gpio_i2c_parsing_data['step4_enc1'][2] == 1:
                    return
                if self.motor4_dir == define.CCW and self.gpio_i2c_parsing_data['step4_enc2'][2] == 1:
                    return                
                data.st_motor_speed = speed
                data.st_motor_count = abs(count)
                fcntl.ioctl(self.dev_gpio, SET_DATA, data)
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.STOP_STEP_MOTOR4, ctypes.sizeof(data))
                data.st_motor_speed = 0
                data.st_motor_count = 0
                
                if self.motor4_dir != define.STOP:
                    self.motor4_dir = define.STOP
                    fcntl.ioctl(self.dev_gpio, SET_DATA, data)  

