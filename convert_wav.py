# 本文件用来测试读入wav文件
import wave
import pyaudio
import numpy as np
from matplotlib import pyplot as plt
from EndPointDetect import EndPointDetect
from configure_class import Configure
class ShorterWav:
    def __init__(self,wave_file_name,output_file_name):
        self.output_file_name=output_file_name
        self.frames = wave.open(wave_file_name,"rb")
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



p = ShorterWav('default_nohash_前进_1_.wav','gogogo2.wav')












#
# print(f.getnframes())
# binary_wav_data=f.readframes(f.getnframes())
# print(type(binary_wav_data))
# digit_wav_data=np.fromstring(binary_wav_data,dtype=np.short)
#
#
# end_point_detect = EndPointDetect(digit_wav_data)
# print(max(digit_wav_data)**2)
# print(max(end_point_detect.energy))
# #处理digit_wav_data
# after_data=[]
# # for i in range(len(end_point_detect.zeroCrossingRate)):
# #
# #     if end_point_detect.wave_data_detected[0] <= end_point_detect.zeroCrossingRate[i] <= end_point_detect.wave_data_detected[1]:
# #         if (i+1)*255<=len(digit_wav_data):
# #             after_data+=digit_wav_data[i*255:(i+1)*255].tolist()
# #         else:
# #             after_data += digit_wav_data[i * 255:-1].tolist()
#
# for i in range(len(end_point_detect.energy)):
#     temp=np.sqrt(end_point_detect.energy[i]/256)
#     if end_point_detect.wave_data_detected[1] <= temp :
#         print(temp)
#         if (i+1)*255<=len(digit_wav_data):
#             after_data+=digit_wav_data[i*255:(i+1)*255].tolist()
#         else:
#             after_data += digit_wav_data[i * 255:-1].tolist()
#
#
# print("len(digit_wav_data) = {}".format(len(digit_wav_data)))
# print("len(after_data = {}".format(len(after_data)))
#
#
# plt.subplot(411)
# plt.plot(np.array(list(range(len(digit_wav_data)))),digit_wav_data)
#
# plt.subplot(412)
# plt.plot(np.array(list(range(len(end_point_detect.energy)))),end_point_detect.energy)
# plt.subplot(413)
# plt.plot(np.array(list(range(len(end_point_detect.zeroCrossingRate)))),end_point_detect.zeroCrossingRate)
#
# plt.subplot(414)
# plt.plot(list(range(len(after_data))),after_data)
# plt.show()
# print(end_point_detect.energy)