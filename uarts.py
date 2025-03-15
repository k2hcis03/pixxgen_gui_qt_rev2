import time
import threading
import fcntl
import user_ioctl
import ctypes
import serial as UART
import datetime


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
            
    def run(self):
        if self.serial.isOpen():
            while True:
                read = self.serial.readline().decode("ascii").strip()
                if read:
                    print(datetime.datetime.now(), read)
                    # if self.port == '/dev/ttyAMA2':
                    if self.status_edit is not None:
                        self.status_edit.setText(str(read))
                    else:
                        self.logging.info(str(read))
                    # else:
                    #     # self.builder.get_object("uart2_rx_entry").set_text(str(read))
                    #     self.logging.info('port2' + str(read))
                time.sleep(0.1)

