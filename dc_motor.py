import time
import threading
import fcntl
import user_ioctl
# import user_thread
import ctypes


class DcMotor:
    def __init__(self, dev_gpio, gpio_i2c_datas, gpio_i2c_parsing_data, logging):
        print("DC motor Class Init")
        self.dev_gpio = dev_gpio['dev_gpio']
        self.dev_gpio_i2c_0 = dev_gpio['dev_gpio_i2c_0']
        self.dev_gpio_i2c_1 = dev_gpio['dev_gpio_i2c_1']

        self.gpio_i2c_datas = gpio_i2c_datas
        self.gpio_i2c_parsing_data = gpio_i2c_parsing_data
        self.CW = 1
        self.CCW = 2
        self.STOP = 3
        self.motor1_dir = self.motor2_dir = self.CW

        self.motor1_speed = 10  # dc motor speed is 0 ~ 100
        self.motor2_speed = 10  # dc motor speed is 0 ~ 100
        self.logging = logging

    def dc_motor_start(self, motor_number, start, speed, count, freq):
        if motor_number == 1:
            if start == True:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.START_DC_MOTOR1, ctypes.sizeof(data))

                if count < 0:
                    self.dc_motor_dir(1, self.CCW)
                else:
                    self.dc_motor_dir(1, self.CW)

                if self.motor1_dir == self.CW and self.gpio_i2c_parsing_data['dc1_enc1'][2] == 1:
                    return
                if self.motor1_dir == self.CCW and self.gpio_i2c_parsing_data['dc1_enc2'][2] == 1:
                    return
                data.dc_motor_speed = speed
                data.dc_motor_count = abs(count)
                data.dc_motor_dir = self.motor1_dir
                data.dc_motor_freq = freq
                fcntl.ioctl(self.dev_gpio, SET_DATA, data)
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.STOP_DC_MOTOR1, ctypes.sizeof(data))
                data.st_motor_speed = 0
                data.st_motor_count = 0
                data.dc_motor_dir = self.motor1_dir
                data.dc_motor_freq = freq
                fcntl.ioctl(self.dev_gpio, SET_DATA, data)

                if self.motor1_dir != self.STOP:
                    self.motor1_dir = self.STOP
                    self.motor1_start = False
        elif motor_number == 2:
            if start == True:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.START_DC_MOTOR2, ctypes.sizeof(data))

                if count < 0:
                    self.dc_motor_dir(2, self.CCW)
                else:
                    self.dc_motor_dir(2, self.CW)

                if self.motor2_dir == self.CW and self.gpio_i2c_parsing_data['dc2_enc1'][2] == 1:
                    return
                if self.motor2_dir == self.CCW and self.gpio_i2c_parsing_data['dc2_enc2'][2] == 1:
                    return
                data.dc_motor_speed = speed
                data.dc_motor_count = abs(count)
                data.dc_motor_dir = self.motor2_dir
                data.dc_motor_freq = freq
                fcntl.ioctl(self.dev_gpio, SET_DATA, data)
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.STOP_DC_MOTOR2, ctypes.sizeof(data))
                data.st_motor_speed = 0
                data.st_motor_count = 0
                data.dc_motor_dir = self.motor1_dir
                data.dc_motor_freq = freq
                fcntl.ioctl(self.dev_gpio, SET_DATA, data)

                if self.motor2_dir != self.STOP:
                    self.motor2_dir = self.STOP
                    self.motor2_start = False
        else:
            print("motor number error")

    def dc_motor_dir(self, motor_number, dir):
        if motor_number == 1:
            if dir == self.CW:
                self.motor1_dir = self.CW
            else:
                self.motor1_dir = self.CCW
        elif motor_number == 2:
            if dir == self.CW:
                self.motor2_dir = self.CW
            else:
                self.motor2_dir = self.CCW
