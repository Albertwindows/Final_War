# encoding=utf-8
import serial
import serial.tools.list_ports
import sys
#from serial_conect import speech_recognition
from speech_recognition import Recognition
import time

def open_serial_and_recognize():
    cov_data = {'停止': '0', '左转': '1', '前进': '3', '后退': '4', '右后转': '5', '快速右转': '6', '右转': '7', '快速左转': '9'}
    # linux
    ser = serial.Serial('/dev/ttyACM0', 9600)
    # 树莓派中必须要sleep 2秒，不然后续的命令不能用。
    time.sleep(2)
    # windows
    # ser = serial.Serial('com3', 9600)
    
    # port_list = serial.tools.list_ports.comports()
    # if len(port_list) != 1:
    #     print("Too many or less serials. Cannot decide which to connect! Please check!")
    #     sys.exit(-1)
    # ser = serial.Serial('com3', 9600)
    sp = Recognition('./866_895.pb','./conv_labels.txt')
    # sp = Recognition('./969_914.pb','./conv_labels.txt')
    speech_str = None
    while speech_str != '结束':
        speech_str = sp.go()
        temp_str = speech_str['result']
        print(speech_str)
        if temp_str in cov_data:
            ser.write(bytes(cov_data[temp_str],'ascii'))

if __name__=="__main__":
    open_serial_and_recognize()
