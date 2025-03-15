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

class TcpServerThread(threading.Thread):
    def __init__(self, main_win):
        threading.Thread.__init__(self)
        self.daemon = True
        
        global main_window
        main_window = main_win
        
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
                    
                try:
                    json_data = json.loads(text)
                    pprint(json_data)
                    
                    # JSON 응답 전송
                    self.request.send(bytes(json.dumps(json_data), 'UTF-8'))
                    
                    # 커맨드 처리
                    if json_data.get('command') == 'xray-onoff':
                        self.on_xray_power(json_data)
                        
                except json.JSONDecodeError as e:
                    print(f'JSON 파싱 오류: {str(e)}')
                    error_response = {'status': 'error', 'message': 'Invalid JSON format'}
                    self.request.send(bytes(json.dumps(error_response), 'UTF-8'))
                    
            except ConnectionError as e:
                print(f'연결 오류: {str(e)}')
                break
            except Exception as e:
                print(f'예상치 못한 오류: {str(e)}')
                break
                
        print(f'클라이언트 핸들러를 종료합니다: {self.client_address[0]}')
    
    def close_socket(self):
        self.request.close()
    
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
                
                main_window.uart_power1.send_serial(continuse_or_pulse_mode, None)
                time.sleep(0.01)
                main_window.uart_power1.send_serial(power_buz, None)
                time.sleep(0.01)
                
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                
                for i in range(13):
                    data.exout[i] = 0
                data.exout[user_ioctl.XRAY1_READY] = 1
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
                fcntl.ioctl(main_window.init.dev_gpio_handle['dev_gpio'], SET_DATA, data)
                time.sleep(0.2)  
                
                data.exout[user_ioctl.XRAY1_ON] = 1
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
                fcntl.ioctl(main_window.init.dev_gpio_handle['dev_gpio'], SET_DATA, data)
            else:
                if text['continue'] == 'on':
                    continuse_or_pulse_mode = "[XMC]"
                else:
                    continuse_or_pulse_mode = "[XMP]"    
                
                if text['buzzer'] == 'on':
                    power_buz = "[XBON]"
                else:
                    power_buz = "[XBOF]"
                
                main_window.uart_power2.send_serial(continuse_or_pulse_mode, None)
                time.sleep(0.01)
                main_window.uart_power2.send_serial(power_buz, None)
                time.sleep(0.01)
                
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                
                for i in range(13):
                    data.exout[i] = 0
                data.exout[user_ioctl.XRAY2_READY] = 1
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
                fcntl.ioctl(main_window.init.dev_gpio_handle['dev_gpio'], SET_DATA, data)
                time.sleep(0.2)  
                
                data.exout[user_ioctl.XRAY2_ON] = 1
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
                fcntl.ioctl(main_window.init.dev_gpio_handle['dev_gpio'], SET_DATA, data)
        else:
            print(f'onff_xray_power{text["sel"]}')
            if text['sel'] == '1':
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                
                for i in range(13):
                    data.exout[i] = 0
                data.exout[user_ioctl.XRAY1_ON] = 0
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
                fcntl.ioctl(main_window.init.dev_gpio_handle['dev_gpio'], SET_DATA, data)
                time.sleep(0.5)  
                
                data.exout[user_ioctl.XRAY1_READY] = 0
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
                fcntl.ioctl(main_window.init.dev_gpio_handle['dev_gpio'], SET_DATA, data)
            else:
                _ioctl = user_ioctl.IOCTLRequest()
                data = user_ioctl.StructIOCTL()
                
                for i in range(13):
                    data.exout[i] = 0
                data.exout[user_ioctl.XRAY2_ON] = 0
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
                fcntl.ioctl(main_window.init.dev_gpio_handle['dev_gpio'], SET_DATA, data)
                time.sleep(0.5)  
                
                data.exout[user_ioctl.XRAY2_READY] = 0
                SET_DATA = _ioctl._IOW(user_ioctl.IOCTL_MAGIC, user_ioctl.SET_GPIO, ctypes.sizeof(data))
                fcntl.ioctl(main_window.init.dev_gpio_handle['dev_gpio'], SET_DATA, data)    


class JsonServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    # Ctrl-C will cleanly kill all spawned threads
    daemon_threads = True
    # much faster rebinding
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass):
        socketserver.TCPServer.__init__(self, server_address, RequestHandlerClass)

        
