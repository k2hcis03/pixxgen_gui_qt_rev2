import time
import threading
import fcntl
import user_ioctl
# import user_thread
import ctypes

STEP_MOTOR = 1
DC_MOTOR = 2


class GPIORead:
    def __init__(self, dev_gpio, gpio_i2c_datas, gpio_i2c_parsing_data, st_motor, dc_motor, logging, main_gui):
        self.start = False
        self.dev_gpio = dev_gpio['dev_gpio']
        self.dev_gpio_i2c_0 = dev_gpio['dev_gpio_i2c_0']
        self.dev_gpio_i2c_1 = dev_gpio['dev_gpio_i2c_1']
        self.gpio_i2c_datas = gpio_i2c_datas
        self.gpio_i2c_parsing_data = gpio_i2c_parsing_data
        self.st_motor = st_motor
        self.dc_motor = dc_motor
        self.logging = logging
        self.main_gui = main_gui

    def motor_limit_left_switch_detect(self, motor_type, motor_number, encoder_name):
        if (self.gpio_i2c_parsing_data[encoder_name][1] == 'active_high' and self.gpio_i2c_parsing_data[encoder_name][0] == 1) or \
                (self.gpio_i2c_parsing_data[encoder_name][1] == 'active_low' and self.gpio_i2c_parsing_data[encoder_name][0] == 0):
            if motor_type == STEP_MOTOR:
                if motor_number == 1:
                    motor_dir = self.st_motor.motor1_dir
                elif motor_number == 2:
                    motor_dir = self.st_motor.motor2_dir
                elif motor_number == 3:
                    motor_dir = self.st_motor.motor3_dir
                elif motor_number == 4:
                    motor_dir = self.st_motor.motor4_dir
                
                if motor_dir == self.st_motor.CW:
                    self.st_motor.st_motor_start(motor_number, False, 0, 0) 
            else:
                if motor_number == 1:
                    motor_dir = self.dc_motor.motor1_dir
                elif motor_number == 2:
                    motor_dir = self.dc_motor.motor2_dir
                if motor_dir == self.dc_motor.CW:
                    self.dc_motor.dc_motor_start(motor_number, False, 1, self.dc_motor.CW, 0)

            self.gpio_i2c_parsing_data[encoder_name][2] = 1     # 검출 플래그 설정

            if motor_type == STEP_MOTOR:
                if motor_number == 1:
                    pass
                    # self.main_gui.label_left_limit.setText('DETECT')
                    # self.logging.info(f'스텝모터 {motor_number} 좌측 센서 검출')
                # elif motor_number == 2:
                #     self.main_gui.label_left_limit.setText('DETECT')
                #     self.logging.info(f'스텝모터 {motor_number} 좌측 센서 검출')
                # elif motor_number == 3:
                #     self.main_gui.label_left_limit.setText('DETECT')
                #     self.logging.info(f'스텝모터 {motor_number} 좌측 센서 검출')
            else:
                # self.logging.info('DC모터 좌측 센서 검출')
                pass
        else:
            self.gpio_i2c_parsing_data[encoder_name][2] = 0
            if motor_type == STEP_MOTOR:
                # self.main_gui.label_left_limit.setText('')
                pass
            else:
                # self.logging.info('DC모터 좌측 센서 비 검출')
                pass

    # def motor_limit_middle_switch_detect(self, motor_type, motor_number, encoder_name):
    #     if (self.gpio_i2c_parsing_data[encoder_name][1] == 'active_high' and self.gpio_i2c_parsing_data[encoder_name][
    #         0] == 1) or \
    #             (self.gpio_i2c_parsing_data[encoder_name][1] == 'active_low' and
    #              self.gpio_i2c_parsing_data[encoder_name][0] == 0):
    #         if motor_type == STEP_MOTOR:
    #             if motor_number == 1:
    #                 motor_dir = self.st_motor.motor1_dir
    #             elif motor_number == 2:
    #                 motor_dir = self.st_motor.motor2_dir
    #             elif motor_number == 3:
    #                 motor_dir = self.st_motor.motor3_dir
    #             elif motor_number == 4:
    #                 motor_dir = self.st_motor.motor4_dir
    #
    #         else:
    #             if motor_number == 1:
    #                 motor_dir = self.dc_motor.motor1_dir
    #             elif motor_number == 2:
    #                 motor_dir = self.dc_motor.motor2_dir
    #         self.gpio_i2c_parsing_data[encoder_name][2] = 1
    #
    #         if motor_type == STEP_MOTOR:
    #             self.builder.get_object("motor{}_toggle_middlelimit".format(motor_number)).set_active(1)
    #         else:
    #             self.builder.get_object("motor{}_toggle_middlelimit1".format(motor_number)).set_active(1)
    #     else:
    #         self.gpio_i2c_parsing_data[encoder_name][2] = 0
    #         if motor_type == STEP_MOTOR:
    #             self.builder.get_object("motor{}_toggle_middlelimit".format(motor_number)).set_active(0)
    #         else:
    #             self.builder.get_object("motor{}_toggle_middlelimit1".format(motor_number)).set_active(0)

    def motor_limit_right_switch_detect(self, motor_type, motor_number, encoder_name):
        if (self.gpio_i2c_parsing_data[encoder_name][1] == 'active_high' and self.gpio_i2c_parsing_data[encoder_name][0] == 1) or \
            (self.gpio_i2c_parsing_data[encoder_name][1] == 'active_low' and self.gpio_i2c_parsing_data[encoder_name][0] == 0):
            if motor_type == STEP_MOTOR:
                if motor_number == 1:
                    motor_dir = self.st_motor.motor1_dir
                elif motor_number == 2:
                    motor_dir = self.st_motor.motor2_dir
                elif motor_number == 3:
                    motor_dir = self.st_motor.motor3_dir
                elif motor_number == 4:
                    motor_dir = self.st_motor.motor4_dir
                if motor_dir == self.st_motor.CCW:
                    self.st_motor.st_motor_start(motor_number, False, 0, 0)   
            else:
                if motor_number == 1:
                    motor_dir = self.dc_motor.motor1_dir
                elif motor_number == 2:
                    motor_dir = self.dc_motor.motor2_dir
                    
                if motor_dir == self.dc_motor.CCW:
                    self.dc_motor.dc_motor_start(motor_number, False, 1, self.dc_motor.CCW, 0)  
                    
            self.gpio_i2c_parsing_data[encoder_name][2] = 1     # 검출 플래그 설정

            if motor_type == STEP_MOTOR:
                if motor_number == 1:
                    # self.main_gui.label_right_limit.setText('DETECT')
                    # self.logging.info(f'스텝모터 {motor_number} 우측 센서 검출')
                    pass
                # elif motor_number == 2:
                #     self.main_gui.label_left_limit.setText('DETECT')
                #     self.logging.info(f'스텝모터 {motor_number} 좌측 센서 검출')
                # elif motor_number == 3:
                #     self.main_gui.label_left_limit.setText('DETECT')
                #     self.logging.info(f'스텝모터 {motor_number} 좌측 센서 검출')
            else:
                # self.logging.info('DC모터 우측 센서 검출')
                pass
        else:
            self.gpio_i2c_parsing_data[encoder_name][2] = 0
            if motor_type == STEP_MOTOR:
                # self.main_gui.label_right_limit.setText('')
                pass
            else:
                # self.logging.info('DC모터 좌측 센서 비 검출')
                pass

    def thread_gpio_read(self):
        if self.start:
            datas = user_ioctl.StructIOCTL()
            _ioctl = user_ioctl.IOCTLRequest()

            GET_DATA = _ioctl._IOR(user_ioctl.IOCTL_MAGIC, user_ioctl.GET_I2C_GPIO_A, ctypes.sizeof(datas))
            fcntl.ioctl(self.dev_gpio_i2c_0, GET_DATA, datas)
            self.gpio_i2c_datas['gpio_i2c_0_input_a'] = datas.gpio_i2c_in_a

            GET_DATA = _ioctl._IOR(user_ioctl.IOCTL_MAGIC, user_ioctl.GET_I2C_GPIO_B, ctypes.sizeof(datas))
            fcntl.ioctl(self.dev_gpio_i2c_0, GET_DATA, datas)
            self.gpio_i2c_datas['gpio_i2c_0_input_b'] = datas.gpio_i2c_in_b

            #
            self.gpio_i2c_parsing_data["step1_enc1"][0] = (self.gpio_i2c_datas['gpio_i2c_0_input_a']) & 0x01
            self.gpio_i2c_parsing_data["step1_enc2"][0] = (self.gpio_i2c_datas['gpio_i2c_0_input_a'] >> 1) & 0x01
            self.gpio_i2c_parsing_data["step1_enc3"][0] = (self.gpio_i2c_datas['gpio_i2c_0_input_a'] >> 2) & 0x01
            self.gpio_i2c_parsing_data["step2_enc1"][0] = (self.gpio_i2c_datas['gpio_i2c_0_input_a'] >> 3) & 0x01
            self.gpio_i2c_parsing_data["step2_enc2"][0] = (self.gpio_i2c_datas['gpio_i2c_0_input_a'] >> 4) & 0x01
            self.gpio_i2c_parsing_data["step2_enc3"][0] = (self.gpio_i2c_datas['gpio_i2c_0_input_a'] >> 5) & 0x01
            self.gpio_i2c_parsing_data["step3_enc1"][0] = (self.gpio_i2c_datas['gpio_i2c_0_input_a'] >> 6) & 0x01
            self.gpio_i2c_parsing_data["step3_enc2"][0] = (self.gpio_i2c_datas['gpio_i2c_0_input_a'] >> 7) & 0x01

            self.gpio_i2c_parsing_data["step4_enc1"][0] = (self.gpio_i2c_datas['gpio_i2c_0_input_b']) & 0x01
            self.gpio_i2c_parsing_data["step4_enc2"][0] = (self.gpio_i2c_datas['gpio_i2c_0_input_b'] >> 1) & 0x01
            self.gpio_i2c_parsing_data["dc1_enc1"][0] = (self.gpio_i2c_datas['gpio_i2c_0_input_b'] >> 2) & 0x01
            self.gpio_i2c_parsing_data["dc1_enc2"][0] = (self.gpio_i2c_datas['gpio_i2c_0_input_b'] >> 3) & 0x01
            self.gpio_i2c_parsing_data["dc2_enc1"][0] = (self.gpio_i2c_datas['gpio_i2c_0_input_b'] >> 4) & 0x01
            self.gpio_i2c_parsing_data["dc2_enc2"][0] = (self.gpio_i2c_datas['gpio_i2c_0_input_b'] >> 5) & 0x01
            #
            self.motor_limit_left_switch_detect(STEP_MOTOR, 1, "step1_enc1")
            # self.motor_limit_middle_switch_detect(STEP_MOTOR, 1, "step1_enc2")
            self.motor_limit_right_switch_detect(STEP_MOTOR, 1, "step1_enc3")

            self.motor_limit_left_switch_detect(STEP_MOTOR, 2, "step2_enc1")
            # self.motor_limit_middle_switch_detect(STEP_MOTOR, 2, "step2_enc2")
            self.motor_limit_right_switch_detect(STEP_MOTOR, 2, "step2_enc3")

            self.motor_limit_left_switch_detect(STEP_MOTOR, 3, "step3_enc1")
            self.motor_limit_right_switch_detect(STEP_MOTOR, 3, "step3_enc2")

            self.motor_limit_left_switch_detect(STEP_MOTOR, 4, "step4_enc1")
            self.motor_limit_right_switch_detect(STEP_MOTOR, 4, "step4_enc2")

            self.motor_limit_left_switch_detect(DC_MOTOR, 1, "dc1_enc1")
            self.motor_limit_right_switch_detect(DC_MOTOR, 1, "dc1_enc2")
            self.motor_limit_left_switch_detect(DC_MOTOR, 2, "dc2_enc1")
            self.motor_limit_right_switch_detect(DC_MOTOR, 2, "dc2_enc2")

            threading.Timer(0.005, self.thread_gpio_read).start()  # 폴링 시간은 5ms

    def thread_timer_gpio_read_start(self):
        if not self.start:
            self.start = True
            self.thread_gpio_read()

    def thread_timer_gpio_read_stop(self):
        self.start = False


