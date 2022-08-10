import time
import fcntl
import user_ioctl
import ctypes


class Collimator:
    def __init__(self, dev_gpio, logging):
        print("Collimator Class Init")
        self.dev_coll_i2c = dev_gpio['dev_coll_i2c']
        self.CW = 1
        self.CCW = 2
        self.STOP = 3
        self.logging = logging

    def coll_motor_start(self, motor_number, start, speed, count, sensor):
        if start:
            _ioctl = user_ioctl.IOCTLRequest()
            data = user_ioctl.StructIOCTL()
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_COLLIMATOR, ctypes.sizeof(data))

            data.collimator_motor_count = count
            data.collimator_motor_number = motor_number  # 1, 2, 4, 8, 16, 1F = all , 0 = Laser on, off
            data.collimator_motor_sensor = sensor
            data.collimator_motor_acc = 1
            data.collimator_motor_speed = speed  # 0 = stop
            data.collimator_motor_sleep = 0
            data.collimator_motor_mode = 1  # 0=full, 1=harf, 2=quarter
            data.collimator_motor_laser = 0  # 0비트 = laser 1, 1비트 = laser 2 ...
            data.collimator_motor_res = 0
            fcntl.ioctl(self.dev_coll_i2c, SET_DATA, data)
        else:
            _ioctl = user_ioctl.IOCTLRequest()
            data = user_ioctl.StructIOCTL()
            data.collimator_motor_number = motor_number  # 1, 2, 4, 8, 16, 1F = all , 0 = Laser on, off
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_COLLIMATOR, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_coll_i2c, SET_DATA, data)

    def coll_extout_start(self, number, on_off):
        _ioctl = user_ioctl.IOCTLRequest()
        data = user_ioctl.StructIOCTL()
        data.collimator_motor_number = number  # 1, 2, 4, 8, 16, 1F = all , 6 = Laser on, off
        data.collimator_motor_laser = on_off  # 1, 2, 4, 8, 16, 1F = all , 0 = Laser on, off
        SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_COLLIMATOR, ctypes.sizeof(data))
        fcntl.ioctl(self.dev_coll_i2c, SET_DATA, data)