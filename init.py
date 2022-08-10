"""
2022-08-02
픽젠 GUI작업 시작
@K2H
"""
import os
import sys


class HardwareInit():
    def __init__(self, logging):
        self.init_done = False
        try:
            self.dev_gpio_handle = {
                "dev_gpio"          : None,
                "dev_gpio_i2c_0"    : None,
                "dev_gpio_i2c_1"    : None,
                "dev_coll_i2c"      : None
            }
            self.gpio_i2c_datas = {    
                "gpio_i2c_1_output_a" : 0,
                "gpio_i2c_1_output_b" : 0,
                
                "gpio_i2c_0_input_a" : 0,
                "gpio_i2c_0_input_b" : 0
            }
            self.gpio_i2c_parsing_data = {
                #첫번째 파라미터 = 디바이스 드라이버 값, 두번째 파라미터 = 센서에서 검출 될 때 입력 신호, 세 번째 파라미터 = 프로그램에서 사용
                #1이면 검출 0이면 비 검출 <-- 사용자가 셋팅해서 사용
                "step1_enc1" : [0, "active_low", 0],    #[0] = 센서 입력 값 저장, [1] = #active low = 평상시 1 검출시 0, [2] = 1이면 검출, 0이면 비검출
                "step1_enc2" : [0, "active_low", 0],   #[0] = 센서 입력 값 저장, [1] = #active high = 평상시 0 검출시 1, [2] = 1이면 검출, 0이면 비검출
                "step1_enc3" : [0, "active_low", 0],                   
                
                "step2_enc1" : [0, "active_low", 0],
                "step2_enc2" : [0, "active_low", 0],
                "step2_enc3" : [0, "active_low", 0],     
                
                "step3_enc1" : [0, "active_low", 0],
                "step3_enc2" : [0, "active_low", 0],
                "step4_enc1" : [0, "active_low", 0],
                "step4_enc2" : [0, "active_low", 0],  
                
                "dc1_enc1" : [0, "active_high", 0],
                "dc1_enc2" : [0, "active_high", 0],
                "dc2_enc1" : [0, "active_high", 0],
                "dc2_enc2" : [0, "active_high", 0]                        
            }
            self.dev_gpio_handle['dev_gpio'] = os.open("/dev/pixxgen_gpio", os.O_RDWR)
            self.dev_gpio_handle['dev_gpio_i2c_0'] = os.open("/dev/pixxgen_gpio_i2c_0", os.O_RDWR)
            self.dev_gpio_handle['dev_gpio_i2c_1'] = os.open("/dev/pixxgen_gpio_i2c_1", os.O_RDWR)
            self.dev_gpio_handle['dev_coll_i2c'] = os.open("/dev/pixxgen_collimator", os.O_RDWR)
            self.init_done = True

            self.logging = logging
            self.logging.info('하드웨어 초기화 성공')
        except OSError as os_err:
            self.init_done = False
            logging.info('하드웨어 초기화 실패')


