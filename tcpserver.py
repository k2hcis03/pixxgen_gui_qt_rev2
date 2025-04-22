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

HOST = '192.168.100.120'
PORT = 9527

main_window = None
uart_power1 = None
uart_power2 = None
dev_gpio_handle = None
xray_time = 0

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
        
        global main_window
        main_window = main_win
        
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
        global main_windows
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
                        self.xray_get_status(json_data)    
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
        lineEdit_xray_status = ""
        
        
        continuse_or_pulse_mode = "[XMC]"    
        power_buz = "[XBON]"
        
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
        
        global xray_time
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

    def xray_start(self, text):
        _ioctl = user_ioctl.IOCTLRequest()
        data = user_ioctl.StructIOCTL()
        lineEdit_xray_status = ""
        
        for i in range(13):
            data.exout[i] = 0
        data.exout[user_ioctl.XRAY1_READY] = 1
        SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
        fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
        time.sleep(0.2)  
        
        data.exout[user_ioctl.XRAY1_ON] = 1
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
        data.exout[user_ioctl.XRAY1_ON] = 0
        SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
        fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
        time.sleep(0.5)  
        
        data.exout[user_ioctl.XRAY1_READY] = 0
        SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
        fcntl.ioctl(self.dev_gpio_handle['dev_gpio'], SET_DATA, data)
    
    def xray_get_status(self, text):
        pass
    
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
            self.xray_stop({"command": "StopXRAY"})
            
        timer_thread = threading.Thread(target=timer_job)
        timer_thread.daemon = True
        timer_thread.start()



        
