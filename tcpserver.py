"""
2022-08-02
픽젠 GUI작업 시작
@K2H
"""

import socketserver, subprocess, sys
import threading
import json
import time
from pprint import pprint

import fcntl
import user_ioctl
import ctypes
import socket
import RPi.GPIO as GPIO
import datetime

HOST = '192.168.100.120'
PORT = 9527

main_window = None
uart_power1 = None
uart_power2 = None
dev_gpio_handle = None
xray_time = 0

xray1_uart_response = None
xray2_uart_response = None

motor1_is_stop = True
motor2_is_stop = True   
motor3_is_stop = True
dc_motor_is_stop = True
motor_x = 0
motor_y = 0
dc_motor_up = False
count_clock = 0

class JsonServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    # Ctrl-C will cleanly kill all spawned threads
    daemon_threads = True
    # much faster rebinding
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass):
        socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass)

class TcpServerThread(threading.Thread):
    def __init__(self, main_win):
        threading.Thread.__init__(self)
        self.daemon = True
        
        global main_window, dc_motor_up
        main_window = main_win
        dc_motor_up = main_win.motor_poistion.get_stand_status()
        # UART 객체들을 전역 변수로 설정
        global uart_power1, uart_power2
        uart_power1 = main_win.uart_power1
        uart_power2 = main_win.uart_power2
        
        # GPIO 핸들도 전역 변수로 설정
        global dev_gpio_handle
        dev_gpio_handle = main_win.init.dev_gpio_handle
        
    def run(self):
        self.server = JsonServer((HOST, PORT), JsonTCPHandler)    #JSON TCP Server
        self.server.serve_forever()
        self.ser
        while True:
            time.sleep(100)
            
    def close_socket(self):
        self.server.shutdown()
        self.server.server_close()
        
class JsonTCPHandler(socketserver.BaseRequestHandler):
    "One instance per connection.  Override handle(self) to customize action."
    
    def __init__(self, request, client_address, server):
        # UART 객체들을 인스턴스 변수로 설정
        self.uart_power1 = uart_power1
        self.uart_power2 = uart_power2
        self.dev_gpio_handle = dev_gpio_handle
        super().__init__(request, client_address, server)
    
    def extract_json_from_http(self, data):
        """HTTP 요청에서 JSON 데이터를 추출합니다.

        Args:
            data (str): HTTP 요청 문자열

        Returns:
            tuple: (is_http, json_data)
                - is_http: HTTP 요청 여부
                - json_data: JSON 데이터 문자열 또는 None
        """
        try:
            # HTTP 요청인지 확인
            if data.startswith('POST') or data.startswith('GET'):
                # 헤더와 본문 분리
                parts = data.split('\r\n\r\n', 1)
                if len(parts) == 2:
                    return True, parts[1].strip()
            return False, data
        except Exception as e:
            print(f'HTTP 파싱 오류: {str(e)}')
            return False, None
    
    def send_response(self, data, is_http=False):
        """JSON 응답을 전송합니다.

        Args:
            data (dict): 전송할 JSON 데이터
            is_http (bool): HTTP 응답 헤더 포함 여부
        """
        try:
            json_response = json.dumps(data, ensure_ascii=False)
            
            if is_http:
                response = f"HTTP/1.1 200 OK\r\n"
                response += f"Content-Type: application/json; charset=utf-8\r\n"
                response += f"Content-Length: {len(json_response.encode('utf-8'))}\r\n"
                response += f"Access-Control-Allow-Origin: *\r\n"  # CORS 지원
                response += f"Connection: close\r\n"
                response += f"\r\n"
                response += json_response
            else:
                response = json_response
                
            self.request.send(response.encode('utf-8'))
        except Exception as e:
            print(f'응답 전송 오류: {str(e)}')
    
    def handle(self):
        print(f'클라이언트가 접속했습니다:{self.client_address[0]}.')
        while True:
            try:
                # self.request is the client connection
                data = self.request.recv(1024)  # clip input at 1Kb
                if not data:  # 연결이 종료된 경우
                    print(f'클라이언트 연결이 종료되었습니다: {self.client_address[0]}')
                    break
                    
                text = data.decode('utf-8')
                if not text.strip():  # 빈 데이터 체크
                    continue
                
                # HTTP 요청에서 JSON 데이터 추출
                is_http, json_text = self.extract_json_from_http(text)
                if not json_text:
                    error_response = {'status': 'error', 'message': 'No valid JSON data found'}
                    self.send_response(error_response, is_http)
                    continue
                    
                try:
                    json_data = json.loads(json_text)
                    pprint(json_data)
                    
                    # JSON 응답 전송
                    if json_data.get('command') !='GetStatus':
                        response = {'status': 'success', 'data': json_data}
                        self.send_response(response, is_http)
                    
                    # 커맨드 처리
                    if json_data.get('command') == 'xray-onoff':
                        self.on_xray_power(json_data)
                    elif json_data.get('command') == 'SetReady':
                        self.xray_set_ready(json_data)
                    elif json_data.get('command') == 'StartXRAY':
                        self.xray_start(json_data)
                    elif json_data.get('command') == 'StopXRAY':
                        self.xray_stop(json_data)
                    elif json_data.get('command') == 'GetStatus':
                        self.xray_get_status(json_data, is_http)   
                    elif json_data.get('command') == 'Move':
                        self.system_move(json_data)
                    elif json_data.get('command') == 'Stand':
                        self.detector_stand(json_data)
                except json.JSONDecodeError as e:
                    print(f'JSON 파싱 오류: {str(e)}')
                    error_response = {'status': 'error', 'message': 'Invalid JSON format'}
                    self.send_response(error_response, is_http)
                    
            except ConnectionError as e:
                print(f'연결 오류: {str(e)}')
                break
            except Exception as e:
                print(f'예상치 못한 오류: {str(e)}')
                break
                
        print(f'클라이언트 핸들러를 종료합니다: {self.client_address[0]}')
    
    def close_socket(self):
        self.request.close()
    
    def xray_set_ready(self, text):
        self.xray_stop(text)

        lineEdit_xray_status = ""
        continuse_or_pulse_mode = "[XMC]"   

        global xray_time
        self.xray_stop({"command": "StopXRAY",
            "param":{
                "xray": 1
            }
            })
        self.xray_stop({"command": "StopXRAY",
            "param":{
                "xray": 2
            }
            })
        
        if text['param']['bp'] == 1:
            power_buz = "[XBON]"
        else:
            power_buz = "[XBOF]"
        
        if text['param']['xray'] == 1:
            GPIO.output(20, GPIO.HIGH)
            time.sleep(0.05)
            self.uart_power1.send_serial(continuse_or_pulse_mode, lineEdit_xray_status)
            time.sleep(0.01)
            self.uart_power1.send_serial(power_buz, lineEdit_xray_status)
            time.sleep(0.01)
        
            power_volt = "[XV{:04}]".format(int(float(text['param']['kv']) * 10))
            self.uart_power1.send_serial(power_volt, lineEdit_xray_status)
            time.sleep(0.01)
            power_current = "[XA{:03}]".format(int(float(text['param']['ma'])))
            self.uart_power1.send_serial(power_current, lineEdit_xray_status)
            time.sleep(0.01)
            power_time = "[XT{:03}]".format(int(float(text['param']['sec']) * 10))
            self.uart_power1.send_serial(power_time, lineEdit_xray_status)
            
            xray_time = int(float(text['param']['sec']))
            time.sleep(0.01)
            
            _ioctl = user_ioctl.IOCTLRequest()
            data = user_ioctl.StructIOCTL()
            
            for i in range(13):
                data.exout[i] = 0
            data.exout[user_ioctl.XRAY1_READY] = 1
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
            
            colimeter = text['param']['cb']
            main_window.chang_collimator_remote(colimeter)
            print(lineEdit_xray_status)
        elif text['param']['xray'] == 2:
            GPIO.output(20, GPIO.LOW)
            time.sleep(0.05)
            self.uart_power2.send_serial(continuse_or_pulse_mode, lineEdit_xray_status)
            time.sleep(0.01)
            self.uart_power2.send_serial(power_buz, lineEdit_xray_status)
            time.sleep(0.01)
        
            power_volt = "[XV{:04}]".format(int(float(text['param']['kv']) * 10))
            self.uart_power2.send_serial(power_volt, lineEdit_xray_status)
            time.sleep(0.01)
            power_current = "[XA{:03}]".format(int(float(text['param']['ma'])))
            self.uart_power2.send_serial(power_current, lineEdit_xray_status)
            time.sleep(0.01)
            power_time = "[XT{:03}]".format(int(float(text['param']['sec']) * 10))
            self.uart_power2.send_serial(power_time, lineEdit_xray_status)
            
            xray_time = int(float(text['param']['sec']))
            time.sleep(0.01)
            
            _ioctl = user_ioctl.IOCTLRequest()
            data = user_ioctl.StructIOCTL()
            
            for i in range(13):
                data.exout[i] = 0
            data.exout[user_ioctl.XRAY2_READY] = 1
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)

    def xray_start(self, text):
        _ioctl = user_ioctl.IOCTLRequest()
        data = user_ioctl.StructIOCTL()
        lineEdit_xray_status = ""
        
        for i in range(13):
            data.exout[i] = 0
        
        if text['param']['xray'] == 1:
            data.exout[user_ioctl.XRAY1_READY] = 1
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
            time.sleep(0.2)  
            
            data.exout[user_ioctl.XRAY1_ON] = 1
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
            time.sleep(0.2)
        elif text['param']['xray'] == 2:
            data.exout[user_ioctl.XRAY2_READY] = 1
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
            time.sleep(0.2)  
            
            data.exout[user_ioctl.XRAY2_ON] = 1
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
            time.sleep(0.2)
        
        # 타이머 시작 (예: self.power_time 초 후에 X-ray 중지)
        self.simple_timer(xray_time+0.5)

    def xray_stop(self, text):
        _ioctl = user_ioctl.IOCTLRequest()
        data = user_ioctl.StructIOCTL()
        
        for i in range(13):
            data.exout[i] = 0
        
        if text['param']['xray'] == 1:
            data.exout[user_ioctl.XRAY1_ON] = 0
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
            time.sleep(0.1)  
            
            data.exout[user_ioctl.XRAY1_READY] = 0
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
        elif text['param']['xray'] == 2:
            data.exout[user_ioctl.XRAY2_ON] = 0
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
            time.sleep(0.1)  
            
            data.exout[user_ioctl.XRAY2_READY] = 0
            SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
            fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)

    def xray_get_status(self, text, is_http):
        # JSON 응답 전송
        # global motor_x, motor_y
        
        motor_count_x = 0
        motor_count_y = 0

        current_time = datetime.datetime.now()
        timestamp = current_time.strftime('%Y%m%d%H%M%S') + f'{current_time.microsecond // 1000:03d}'
        # self.get_temp_form_xray(1)
        time.sleep(0.05)
        # self.get_temp_form_xray(2)
        # time.sleep(0.05)
        # with open('/sys/bus/platform/drivers/pixggen_gpio/equipment/pixxgen_sys/counter1') as count:
        #     motor_count_x = int(count.readline())
        # print(f'motor_count_x: {motor_count_x}')

        # with open('/sys/bus/platform/drivers/pixggen_gpio/equipment/pixxgen_sys/counter2') as count:
        #     motor_count_y = int(count.readline())
        # print(f'motor_count_y: {motor_count_y}')
        
        # if motor_count_x == 0:
        #     motor_x = remote_x
        # else:
        #     motor_x = motor_x + ((-1*count_clock) - (motor_count_x - motor_x))

        # if motor_count_y == 0:
        #     motor_y = remote_y
        # else:
        #     motor_y = motor_count_y

        response = {'status': 'success', 'data': {
            'command': 'GetStatus',
            'param': {
                'device': text['device'],
                'timestamp': timestamp,
                'xray1_temp': xray1_uart_response,
                'xray2_temp': xray2_uart_response,
                'motor1_is_stop': motor1_is_stop,
                'motor2_is_stop': motor2_is_stop,
                'motor3_is_stop': motor3_is_stop,
                'dc_motor_is_stop': dc_motor_is_stop,
                'motor_x_position': motor_x,
                'motor_y_position': motor_y,
                'stand_position': dc_motor_up
            }
        }}
        self.send_response(response, is_http)

    def system_move(self, text):
        # JSON 응답 전송
        # main_window.logging.info(f'pushButton_move_left clicked')
        global motor1_is_stop, motor2_is_stop, motor3_is_stop, dc_motor_is_stop, remote_x, remote_y, motor_x, motor_y
        global dc_motor_up, count_clock
        remote_x =text['param']['x']
        remote_y =text['param']['y']
       
        count_clock = (motor_y - remote_y) * 1
        
        if dc_motor_up == False:
            if remote_y == 0:
                move_dir = main_window.cc.get_map('st_move_up')
                loop = move_dir['LOOP']
                motor2_is_stop = False
                motor3_is_stop = False
                for count in range(1, loop+1):
                    message = {
                        'position'  : move_dir[f'POSITION{count}'],
                        'speed'     : int(move_dir[f'SPEED{count}']),
                        'count'     : int(move_dir[f'COUNT{count}']), 
                        'timeout'   : int(move_dir[f'TIMEOUT{count}'])   #1분
                    }
                print(message)
                motor_y = 0
                main_window.command_queue.put(message)
            elif count_clock < 0:
                move_dir = main_window.cc.get_map('st_move_down')
                loop = move_dir['LOOP']
                motor2_is_stop = False
                motor3_is_stop = False
                for count in range(1, loop+1):
                    message = {
                        'position'  : move_dir[f'POSITION{count}'],
                        'speed'     : int(move_dir[f'SPEED{count}']),
                        'count'     : int(abs(count_clock)), 
                        'timeout'   : int(move_dir[f'TIMEOUT{count}'])   #1분
                    }
                print(message)
                motor_y = remote_y
                main_window.command_queue.put(message)
            else:
                move_dir = main_window.cc.get_map('st_move_up')
                loop = move_dir['LOOP']
                motor2_is_stop = False
                motor3_is_stop = False
                for count in range(1, loop+1):
                    message = {
                        'position'  : move_dir[f'POSITION{count}'],
                        'speed'     : int(move_dir[f'SPEED{count}']),
                        'count'     : int(abs(count_clock)), 
                        'timeout'   : int(move_dir[f'TIMEOUT{count}'])   #1분
                    }
                print(message)
                motor_y = remote_y
                main_window.command_queue.put(message)
            main_window.motor_poistion.set_command_stop(False) #큐를 시작할 수 있는 조건 FALSE
        
        count_clock = (motor_x - remote_x) * 1
        
        if remote_x == 0:
            move_dir = main_window.cc.get_map('st_move_left')
            loop = move_dir['LOOP']
            motor1_is_stop = False
            for count in range(1, loop+1):
                message = {
                    'position'  : move_dir[f'POSITION{count}'],
                    'speed'     : int(move_dir[f'SPEED{count}']),
                    'count'     : int(move_dir[f'COUNT{count}']), 
                    'timeout'   : int(move_dir[f'TIMEOUT{count}'])   #1분
                }
            print(message)
            motor_x = 0
            main_window.command_queue.put(message)
        elif count_clock < 0:   
            move_dir = main_window.cc.get_map('st_move_right')
            loop = move_dir['LOOP']
            motor1_is_stop = False
            for count in range(1, loop+1):
                message = {
                    'position'  : move_dir[f'POSITION{count}'],
                    'speed'     : int(move_dir[f'SPEED{count}']),
                    'count'     : int(abs(count_clock)), 
                    'timeout'   : int(move_dir[f'TIMEOUT{count}'])   #1분
                }
            print(message)
            motor_x = remote_x
            main_window.command_queue.put(message)
        else:
            move_dir = main_window.cc.get_map('st_move_left')
            loop = move_dir['LOOP']
            motor1_is_stop = False
            for count in range(1, loop+1):
                message = {
                    'position'  : move_dir[f'POSITION{count}'],
                    'speed'     : int(move_dir[f'SPEED{count}']),
                    'count'     : int(abs(count_clock)), 
                    'timeout'   : int(move_dir[f'TIMEOUT{count}'])   #1분
                }
            print(message)
            motor_x = remote_x
            main_window.command_queue.put(message)
        main_window.motor_poistion.set_command_stop(False) #큐를 시작할 수 있는 조건 FALSE

    def detector_stand(self, text):
        # JSON 응답 전송
        # main_window.logging.info(f'pushButton_move_left clicked')
        global motor1_is_stop, motor2_is_stop, motor3_is_stop, dc_motor_is_stop, remote_x, remote_y, motor_x, motor_y
        global dc_motor_up

        move_dir = main_window.cc.get_map('st2_move_down')
        loop = move_dir['LOOP']
        motor2_is_stop = False
        for count in range(1, loop+1):
            message = {
                'position'  : move_dir[f'POSITION{count}'],
                'speed'     : int(move_dir[f'SPEED{count}']),
                'count'     : int(move_dir[f'COUNT{count}']), 
                'timeout'   : int(move_dir[f'TIMEOUT{count}'])   #1분
            }
        print(message)
        main_window.command_queue.put(message)
        main_window.motor_poistion.set_command_stop(False) #큐를 시작할 수 있는 조건 FALSE

        if text['param']['up'] == 1:
            move_dir = main_window.cc.get_map('dc_motor_up')
            loop = move_dir['LOOP']
            dc_motor_is_stop = False
            dc_motor_up = True
            for count in range(1, loop+1):
                message = {
                    'position'  : move_dir[f'POSITION{count}'],
                    'speed'     : int(move_dir[f'SPEED{count}']),
                    'count'     : int(move_dir[f'COUNT{count}']), 
                    'timeout'   : int(move_dir[f'TIMEOUT{count}'])   #1분
                }
            print(message)
            main_window.command_queue.put(message)
        else:
            move_dir = main_window.cc.get_map('dc_motor_down')
            loop = move_dir['LOOP']
            dc_motor_is_stop = False
            dc_motor_up = False
            for count in range(1, loop+1):
                message = {
                    'position'  : move_dir[f'POSITION{count}'],
                    'speed'     : int(move_dir[f'SPEED{count}']),
                    'count'     : int(move_dir[f'COUNT{count}']), 
                    'timeout'   : int(move_dir[f'TIMEOUT{count}'])   #1분
                }
            print(message)
            main_window.command_queue.put(message)
        main_window.motor_poistion.set_command_stop(False) #큐를 시작할 수 있는 조건 FALSE

    def on_xray_power(self, text):
        if text['onoff'] == 'on':
            print(f'on_xray_power{text["sel"]}')
            
            if text['sel'] == '1':
                if text['continue'] == 'on':
                    continuse_or_pulse_mode = "[XMC]"
                else:
                    continuse_or_pulse_mode = "[XMP]"    
                
                if text['buzzer'] == 'on':
                    power_buz = "[XBON]"
                else:
                    power_buz = "[XBOF]"
                
                self.uart_power1.send_serial(continuse_or_pulse_mode, None)
                time.sleep(0.01)
                self.uart_power1.send_serial(power_buz, None)
                time.sleep(0.01)
                
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
                if text['continue'] == 'on':
                    continuse_or_pulse_mode = "[XMC]"
                else:
                    continuse_or_pulse_mode = "[XMP]"    
                
                if text['buzzer'] == 'on':
                    power_buz = "[XBON]"
                else:
                    power_buz = "[XBOF]"
                
                self.uart_power2.send_serial(continuse_or_pulse_mode, None)
                time.sleep(0.01)
                self.uart_power2.send_serial(power_buz, None)
                time.sleep(0.01)
                
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
        else:
            print(f'onff_xray_power{text["sel"]}')
            if text['sel'] == '1':
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
    
    def simple_timer(self, seconds):
        """지정된 시간 후에 한 번만 실행되는 타이머
        Args:
            seconds (int): 타이머 시간 (초)
        """
        def timer_job():
            time.sleep(seconds)
            print(f"{seconds}초 타이머 완료!")
            self.xray_stop({"command": "StopXRAY",
                            "param":{
                                "xray": 1
                            }
                            })
            self.xray_stop({"command": "StopXRAY",
                            "param":{
                                "xray": 2
                            }
                            })
            
        timer_thread = threading.Thread(target=timer_job)
        timer_thread.daemon = True
        timer_thread.start()


    def get_temp_form_xray(self, select_power):
        xray_temp = "[XTMP]"

        if select_power == 1:
            GPIO.output(20, GPIO.HIGH)
            time.sleep(0.05)
            self.uart_power1.send_serial(xray_temp, None)
        else:
            GPIO.output(20, GPIO.LOW)
            time.sleep(0.05)
            self.uart_power2.send_serial(xray_temp, None)
        time.sleep(0.1)
        GPIO.output(20, GPIO.HIGH)
        time.sleep(0.01)
        
