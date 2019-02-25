# 本文件用来测试读入wav文件
import wave
import pyaudio
import numpy as np
from configure_class import Configure
import os
class ShorterWav:
    @staticmethod
    def get_wav_file_names(BASE_DIR='.'):
        """

        :param BASE_DIR: 默认获取该py文件下的所有的wav文件
        :return:
        """
        L = []
        for root, dirs, files in os.walk(BASE_DIR):
            for file in files:
                if file[-4:] == '.wav':
                    L.append(file)
        return L

    @staticmethod
    def makedir(default_path = './result'):

        if not os.path.exists(default_path):
            os.makedirs(default_path)
            return True
        else:
            print("{}已经存在".format(default_path))
            return False


    def __init__(self,input_file_name,output_file_name):
        self.output_file_name=output_file_name
        self.frames = wave.open(input_file_name,"rb")

        self.binary_wav_data = self.frames.readframes(self.frames.getnframes())

        # 如果if False 那么就没有 digit_wav_data 了
        if Configure.FORMAT == pyaudio.paInt16:
            self.digit_wav_data = np.fromstring(self.binary_wav_data, dtype=np.short)

        self.input_size = len(self.digit_wav_data)

        self.record_seconds = Configure.RECORD_SECONDS
        self.rate = Configure.RATE
        self.output_size = int(self.rate*self.record_seconds)

        #存储处理之后的结果，预测len(self.wave_data_after)==self.output_size
        self.wave_data_after = []
        self.run()
        self.save_file()



    def save_file(self):
        c=Configure()
        wf = wave.open(self.output_file_name, 'wb')
        wf.setnchannels(c.CHANNELS)
        wf.setsampwidth(pyaudio.get_sample_size(c.FORMAT))
        wf.setframerate(c.RATE)
        wf.writeframes(b''.join(self.wave_data_after))
        wf.close()

    def run(self):
        """
        main function
        save to wave_data_after
        :return:
        """
        input_data = self.digit_wav_data
        output_size = self.output_size
        current_volume_sum = 0.0
        for i in range(self.output_size):
            current_volume_sum += abs(input_data[i])

        loudest_end_index = output_size
        loudest_volume = current_volume_sum
        for i in range(output_size,len(input_data)):
            trailing_value = input_data[i-output_size]
            current_volume_sum -= abs(trailing_value)
            leading_value = input_data[i]
            current_volume_sum += abs(leading_value)
            if current_volume_sum > loudest_volume:
                loudest_end_index = i
                loudest_volume = current_volume_sum

        # index 0 is a beginning
        loudest_begin_index = loudest_end_index - output_size + 1
        self.wave_data_after = input_data[loudest_begin_index:loudest_end_index + 1]
        print(len(self.wave_data_after))
        # self.save_file()

if __name__=="__main__":
    ShorterWav.makedir()
    from_dir = './wavs/'
    to_dir='./result/'
    for file in ShorterWav.get_wav_file_names(from_dir):
        p = ShorterWav(from_dir+file,to_dir+file[:-4]+str(Configure.RECORD_SECONDS)+'s'+'.wav')