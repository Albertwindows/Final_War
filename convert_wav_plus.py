# encoding=utf-8
# 本文件用来测试读入wav文件
import wave
import pyaudio
import numpy as np
from configure_class import Configure
import os
import matplotlib.pyplot as plt
import sys

class ZCR:
    """
    计算过零率
    """
    def __init__(self,digit_wav_data,unit_samples=256):
        """
        :param digit_wav_data: 是一个每个数为16位的数组
        """
        #每帧的数据是256个
        self.unit_samples = unit_samples
        # 阈值
        self.zcr_threshold = 0.3
        self.energy_threshold = 0.5
        self.top_k = 2
        self.digit_wav_data = digit_wav_data[:]
        self.zcr_rate,self.energy = self.calc_zcr_and_energy()
        # self.energy = self.calc_energy()
        # self.maximum_pos = 0
        # self.maximum_pos = 0
        # self.zcr_rate = self.calc_zcr()
        # self.maximum_pos = self.maximum_zcr()
        # self.maximum_pos = self.maximum_energy()

        # print(self.maximum_pos)
        # self.calc_energy()

    def maximum_zcr(self):
        """
        找到zcr的极大值的位置
        :return:
        """
        # 使用过零率初步筛选极大值
        maximum_pos = []
        for i in range(1,len(self.zcr_rate)-1):
            x = self.zcr_rate[i-1]
            y = self.zcr_rate[i]
            z = self.zcr_rate[i+1]
            if x < y and z < y:
                maximum_pos.append(i)

        while len(maximum_pos) > self.top_k + 2:
            new_maximum_pos = []
            for i in range(1,len(maximum_pos)-1):
                x = self.zcr_rate[maximum_pos[i - 1]]
                y = self.zcr_rate[maximum_pos[i]]
                z = self.zcr_rate[maximum_pos[i + 1]]
                if x < y and z < y:
                    new_maximum_pos.append(maximum_pos[i])
            maximum_pos = new_maximum_pos
        return maximum_pos

    def calc_total_energy(self):
        energy_sum = 0
        for d in self.digit_wav_data:
            energy_sum += abs(d)
        
        return energy_sum

    def maximum_energy(self):
        energy = []
        for i in range(len(self.maximum_pos) - 1):
            x = self.maximum_pos[i]
            y = self.maximum_pos[i + 1]
            e_sum = 0
            for e in range(x * self.unit_samples, y * self.unit_samples):
                e_sum += abs(self.digit_wav_data[e])
            energy.append(e_sum)

        top_k_energy = np.argsort(energy)[::-1][:self.top_k]
        result = set()
        for t in top_k_energy:
            result.add(self.maximum_pos[t])
            result.add(self.maximum_pos[t+1])
        result = list(result)
        return result

    def calc_zcr_and_energy(self):
        # 0-255 :256
        zcr_rate = []
        energy = []
        zcr_sum = 0
        energy_sum = 0
        max_energy = 0
        for i in range(len(self.digit_wav_data)-1):
            if (i+1) % self.unit_samples == 0:
                zcr_rate.append(zcr_sum/float(self.unit_samples))
                energy.append(energy_sum/float(self.unit_samples)/2**15)
                zcr_sum,energy_sum = 0,0
            x = self.digit_wav_data[i]
            y = self.digit_wav_data[i+1]

            max_energy = max(max_energy,abs(self.digit_wav_data[i]))
            energy_sum += abs(self.digit_wav_data[i])
            if float(x)*float(y) < 0:
                zcr_sum += 1

        if zcr_sum != 0:
            zcr_rate.append(zcr_sum/float(self.unit_samples))
            # energy.append(energy_sum/float(self.unit_samples)/2**15)
            energy.append((max_energy/2**15))
        return zcr_rate[:],energy[:]

    def analysis_zcr(self):
        """
        根据zcr_rate来找到分单个字的位置：
        :return:
        """
        pass

    def get_weather_start_record_state(self):
        zcr_flag = max(self.zcr_rate) > self.zcr_threshold
        energy_flag = max(self.energy) > self.energy_threshold
        print(max(self.zcr_rate),max(self.energy))
        return zcr_flag,energy_flag

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
        self.configure = Configure(0.7)
        self.output_file_name=output_file_name
        self.frames = wave.open(input_file_name,"rb")

        self.binary_wav_data = self.frames.readframes(self.frames.getnframes())

        # 如果if False 那么就没有 digit_wav_data 了
        if self.configure.FORMAT == pyaudio.paInt16:
            self.digit_wav_data = np.fromstring(self.binary_wav_data, dtype=np.short)
        else:
            print("Error!->Configure.FORMAT != pyaudio.paInt16:")
            sys.exit(-1)

        self.input_size = len(self.digit_wav_data)

        self.record_seconds = self.configure.RECORD_SECONDS
        self.rate = self.configure.RATE
        self.output_size = int(self.rate*self.record_seconds)

        #存储处理之后的结果，预测len(self.wave_data_after)==self.output_size
        self.wave_data_after = []
        self.run()
        self.save_file()



    def save_file(self):
        c=self.configure
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
        # if self.output_size <= self.configure.RECORD_SECONDS * self.configure.RATE:
        #     self.wave_data_after = self.digit_wav_data
        #     return
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
        loudest_begin_index = loudest_end_index - output_size
        self.wave_data_after = input_data[loudest_begin_index:loudest_end_index + 1]
        print(len(self.wave_data_after))
        # self.save_file()


class StandardWav:
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
    def makedir(default_path='./result'):

        if not os.path.exists(default_path):
            os.makedirs(default_path)
            return True
        else:
            print("{}已经存在".format(default_path))
            return False

    def max_standard_wav(self):
        """
        对音频文件进行标准化，即音频中声音最大的位置变成30000
        :return:
        """
        max_volume = 0
        for s in self.digit_wav_data:
            if s > max_volume:
                max_volume = s

        k = self.max_volum / float(max_volume)#需要变大的比例

        for i in range(len(self.digit_wav_data)):
            self.digit_wav_data[i] = int(self.digit_wav_data[i] * k)

    def __init__(self,input_file_name,output_file_name):
        self.max_volum = 30000
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

        # 存储处理之后的结果，预测len(self.wave_data_after)==self.output_size
        self.wave_data_after = []
        zcr = ZCR(self.digit_wav_data)
        plt.subplot(211)
        plt.plot(list(range(len(zcr.zcr_rate))),zcr.zcr_rate)
        plt.subplot(212)
        plt.plot(list(range(len(zcr.digit_wav_data))),zcr.digit_wav_data)
        plt.show()
        print("____________")
        print(zcr.maximum_pos)
        self.max_standard_wav()
        # self.run()
        # self.save_file()

    def save_file(self):
        c = Configure()
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
        # print(len(self.wave_data_after))
        # self.save_file()


if __name__=="__main__":
    sh = StandardWav('./lijiaxin_nohash_启动_1_1s.wav',None)
    # sl = StandardWav('./yao_low.wav',None)
    # hmax,lmax = 0,0
    # for s in sh.digit_wav_data:
    #     if s>hmax:
    #         hmax = s
    # for s in sl.digit_wav_data:
    #     if s>lmax:
    #         lmax = s
    #
    # print("h={},l={}".format(hmax,lmax))

    # from_dir = './wavs/'
    # to_dir='./results/'
    # labels = ["前进", "后退", "左转", "右转", "停止", "启动"]
    # for la in labels:
    #     StandardWav.makedir('./'+la+'/')
    # for file in StandardWav.get_wav_file_names(from_dir):
    #     for la in labels:
    #         if la in file:
    #             which_dir = la
    #             break;
    #     to_dir = './'+which_dir+'/'
    #     to_dir_file = to_dir+file[:-4]+str(Configure.RECORD_SECONDS)+'s'+'.wav'
    #     p = StandardWav(from_dir+file,to_dir_file)
