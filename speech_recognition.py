# encoding=utf-8
from recoder import Recoder
import label_wav
from configure_class import Configure
import time
import wave
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from convert_wav_plus import ShorterWav


class Recognition():
    def __init__(self, graph, labels):
        self.graph = graph
        self.labels = labels

    def get_result(self, filename):
        # graph_name = './866_895.pb'
        # labels_name = './conv_labels.txt'
        wav = filename
        input_name = 'wav_data:0'
        output_name = 'labels_softmax:0'
        how_many_labels = 1
        result_dict = label_wav.label_wav(wav, self.labels, self.graph, input_name, output_name, how_many_labels)
        return result_dict

    def run(self,binary_str,unit_time):
        """
        :param binary_str: 外层录音所得到的二进制的字符串
        :return: 返回识别的结果集合
        """
        # digit_data = np.fromstring(binary_str, np.int16)
        # plt.plot(list(range(len(digit_data))),digit_data)
        # plt.show()
        c = Configure(unit_time=unit_time)
        wf = wave.open('before.wav', 'wb')
        wf.setnchannels(c.CHANNELS)
        wf.setsampwidth(pyaudio.get_sample_size(c.FORMAT))
        wf.setframerate(c.RATE)
        wf.writeframes(binary_str)
        wf.close()
        print("Identify ...")
        print("录音的时间长度 %.2f" %(len(binary_str)/32000))
        p = ShorterWav('before.wav', 'after.wav')
        result_dict = self.get_result('after.wav') # 识别语音指令
        return result_dict

    def go(self):
        #请说出语音指令，例如["向上", "向下", "向左", "向右"]
        print("\n\n==================================================")
        print("Please tell me the command(limit within 2 seconds):")
        #print("Please tell me what you want to identify(limit within 10 seconds):")
        print("Recodering.......")
        r = Recoder()
        r.recoder()
        # r.savewav('after.wav') # 录制语音指令
        r.savewav('before.wav') # 录制语音指令
        p = ShorterWav('before.wav','after.wav')
        print("Identify ...")
        result = self.get_result('after.wav') # 识别语音指令
        time.sleep(0)   # 延时1秒
        return result


if __name__ == '__main__':
    r = Recognition('./866_895.pb', './conv_labels.txt')
    while True:
        result = r.go()
        print(result)
