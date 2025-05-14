import time
import threading
import fcntl
import user_ioctl
import ctypes
import serial as UART
import datetime
import tcpserver
import re

class Uarts(threading.Thread):
    def __init__(self, dev_gpio, port, baud, logging):
        threading.Thread.__init__(self)
        self.dev_gpio = dev_gpio['dev_gpio']
        self.serial = UART.Serial(port, baud, timeout=0)
        self.daemon = True
        self.port = port
        self.logging = logging
        self.status_edit = None
        
    def send_serial(self, data, status_edit):
        if self.serial.isOpen():
            self.serial.write(bytes(data, 'ascii'))
            
            if status_edit:
                self.status_edit = status_edit
            
    def extract_number(self, text):
        # [S_T027] 형식에서 숫자만 추출하여 문자열로 반환
        match = re.search(r'\[S_T(\d+)\]', text)
        if match:
            number = match.group(1)
            return str(number)  # 명시적으로 문자열로 반환
        return str(text)  # 매칭되지 않으면 원본 텍스트를 문자열로 반환
            
    def run(self):
        if self.serial.isOpen():
            while True:
                read = self.serial.readline().decode("ascii").strip()
                if read:
                    print(datetime.datetime.now(), read)
                    processed_read = self.extract_number(read)
                    
                    if self.status_edit is not None:
                        self.status_edit.setText(processed_read)
                    else:
                        self.logging.info(processed_read)

                    if self.port == '/dev/ttyAMA2':
                        tcpserver.xray1_uart_response = processed_read
                    else:
                        tcpserver.xray2_uart_response = processed_read
                time.sleep(0.1)

