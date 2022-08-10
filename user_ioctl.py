import struct
import ctypes
from ioctl import IOCTL

MMAPSIZE = 512 * 4
IOCTL_MAGIC = ord('R')

SET_GPIO  = 2
GET_GPIO  = 3
SET_I2C_GPIO_A = 4
SET_I2C_GPIO_B  = 5
GET_I2C_GPIO_A = 6
GET_I2C_GPIO_B = 7
SET_I2C_POT = 8
GET_I2C_POT = 9
SET_COLLIMATOR_MUX = 10
SET_COLLIMATOR = 11
GET_COLLIMATOR = 12
# SET_I2C_COLLIMATOR_2 = 13
# GET_I2C_COLLIMATOR_2 = 14
ADC_START = 15
ADC_STOP = 16
START_STEP_MOTOR1 = 17		
START_STEP_MOTOR2 = 18		
START_STEP_MOTOR3 = 19		
START_STEP_MOTOR4 = 20	
STOP_STEP_MOTOR1 = 21	
STOP_STEP_MOTOR2 = 22	
STOP_STEP_MOTOR3 = 23		
STOP_STEP_MOTOR4 = 24
START_DC_MOTOR1 = 25		
START_DC_MOTOR2 = 26		
#START_DC_MOTOR3 = 27		
STOP_DC_MOTOR1 = 28
STOP_DC_MOTOR2 = 29	
#STOP_DC_MOTOR3 = 30	
# START_COLL_MOTOR1 = 31
# START_COLL_MOTOR2 = 32
# START_COLL_MOTOR3 = 33
# START_COLL_MOTOR4 = 34
# START_COLL_MOTOR5 = 35
# STOP_COLL_MOTOR1 = 36
# STOP_COLL_MOTOR2 = 37
# STOP_COLL_MOTOR3 = 38
# STOP_COLL_MOTOR4 = 39
# STOP_COLL_MOTOR5 = 40

# XRAY GPIO PIN NUMBER
XRAY1_READY = 9
XRAY1_ON = 10

XRAY2_READY = 11
XRAY2_ON = 12

	
class StructIOCTL(ctypes.Structure):  
    _pack_ = 1  
    _fields_ = [('exout',ctypes.c_int8*13), ('exin',ctypes.c_int8*3), ('gpio_i2c_out_a',ctypes.c_int8),
                ('gpio_i2c_out_b',ctypes.c_int8), ('gpio_i2c_in_a',ctypes.c_int8), ('gpio_i2c_in_b',ctypes.c_int8),
                ('st_motor_count',ctypes.c_int32), ('st_motor_speed',ctypes.c_int32), 
                ('dc_motor_count',ctypes.c_int32), ('dc_motor_speed',ctypes.c_int32), ('dc_motor_dir',ctypes.c_int8),
                ('dc_motor_freq',ctypes.c_int32),
                ('collimator_motor_number',ctypes.c_int8), ('collimator_motor_count',ctypes.c_int32),
                ('collimator_motor_sensor',ctypes.c_int8), ('collimator_motor_acc',ctypes.c_int8), 
                ('collimator_motor_speed',ctypes.c_int8), ('collimator_motor_sleep',ctypes.c_int8), 
                ('collimator_motor_mode',ctypes.c_int8), ('collimator_motor_laser',ctypes.c_int8), 
                ('collimator_motor_res;',ctypes.c_int8), ('collimator_motor_status',ctypes.c_int32)]  
IOCTL_MAGIC = ord('R') 

class IOCTLRequest():
    IOCPARM_MASK = 0x3fff
    IOC_NONE = 0x20000000
    IOC_WRITE = 0x40000000
    IOC_READ = 0x80000000

    def FIX(self,x): 
        return struct.unpack("i", struct.pack("I", x))[0]
    def _IO(self,type,number): 
        return self.FIX(self.IOC_NONE|type<<8|number)
    def _IOR(self,type,number,size): 
        return self.FIX(self.IOC_READ|((size&self.IOCPARM_MASK)<<16)|type<<8|number)
    def _IOW(self,type,number,size): 
        return self.FIX(self.IOC_WRITE|((size&self.IOCPARM_MASK)<<16)|type<<8|number)
    def _IOWR(self,type,number,size): 
        return self.FIX(self.IOC_READ|self.IOC_WRITE|((size&self.IOCPARM_MASK)<<16)|type<<8|number)

