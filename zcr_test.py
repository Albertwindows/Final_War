# encoding=utf-8
import random
import numpy as np
from pyaudio import PyAudio
from convert_wav_plus import ZCR
from configure_class import Configure
from speech_recognition import Recognition
import matplotlib.pyplot as plt

def save_wav(filename,binary_str):
    c = Configure
    wf = wave.open(filename, 'wb')
    wf.setnchannels(c.CHANNELS)
    wf.setsampwidth(pyaudio.get_sample_size(c.FORMAT))
    wf.setframerate(c.RATE)
    wf.writeframes(binary_str)
    wf.close()

def recoder_and_decide(unit_time=0.3):

    pa = PyAudio()
    config = Configure(unit_time=unit_time)
    times = 0


    result_before = []
    binary_str = b""
    pre_str = b""
    temp_binary_str = b""
    print("begin_____________________")
    is_recording,pre_is_recording = False, False

    test_zcr_count = 0
    while times < 100 or True:
        stream = pa.open(format=config.FORMAT,
                         channels=config.CHANNELS,
                         rate=config.RATE,
                         input=True,
                         frames_per_buffer=config.CHUNK)

        frames = []
        times += 1
        pre_is_recording = is_recording

        pre_str = temp_binary_str
        stream.start_stream()
        for i in range(0, config.get_count_chunk()):
            data = stream.read(config.CHUNK)
            frames.append(data)
        stream.stop_stream()

        temp_binary_str = b''.join(frames)

        digit_data = np.fromstring(temp_binary_str, np.int16)
        zcr = ZCR(digit_data)
        zcr_flag,energy_flag = zcr.get_weather_start_record_state()

        is_recording = energy_flag or zcr_flag
        # is_recording = zcr_flag or energy_flag
        print(zcr_flag,energy_flag)
        if zcr_flag:
            test_zcr_count += 1


        # print("zcr_rate = {},max_energy = {}".format(max(zcr_rate),max(energy)))

        # zcr_flag = max(zcr_rate) > zcr.zcr_threshold
        # energy_flag = max(energy) > zcr.energy_threshold
        # print("max_zcr={},max_energy={}".format(max(zcr_rate),max(energy)))
        # print("t={}s,z={},e={}".format(times*config.RECORD_SECONDS,zcr_flag,energy_flag))
        # if zcr_flag or energy_flag:
        #     is_recording = True
        # else
        #     is_recording = False

        # result_before += list(digit_data)
        if is_recording:
            # print(type(binary_str),type(temp_binary_str))
            if not pre_is_recording:
                binary_str = pre_str
            binary_str += temp_binary_str
            print("Recording,time=%s" % str(len(binary_str)/32000))
            print("\n__________________________________________")
            # print("Recording@@@{}@@@{}".format(zcr_flag,energy_flag))
        elif pre_is_recording:
            # stop recording and start recognizing
            print("test_zcr_count = %d" % test_zcr_count)
            test_zcr_count = 0
            print("Recognizing......")
            sp = Recognition('./969_914.pb', './conv_labels.txt')
            recognized_dict = sp.run(binary_str,unit_time)
            print("识别结果：{}".format(recognized_dict))
            binary_str = b""

        else:
            print("Finding")
            # print("Finding+++{}+++{}".format(zcr_flag,energy_flag))

    stream.stop_stream()
    stream.close()
    pa.terminate()
    return None


result = recoder_and_decide(0.35)
# plt.subplot(211)
# plt.plot(list(range(len(result))),result)
# plt.subplot(212)
# plt.plot(list(range(len(result_before))),result_before)
# z = ZCR(r,unit_samples=64)
# zcr,energy = z.calc_zcr_and_energy()
# zcr_diff = []
# zcr_float = []
# for i in range(len(zcr)-1):
#     zcr_float.append(float(zcr[i])/64)
#     zcr_diff.append(zcr[i+1]-zcr[i])
# print(zcr)
# plt.subplot(411)
# plt.plot(list(range(len(zcr))),zcr)
# plt.subplot(412)
# plt.plot(list(range(len(r))),r)
# plt.subplot(413)
# plt.plot(list(range(len(zcr_diff))),zcr_diff)
# plt.subplot(414)
# plt.plot(list(range(len(z.energy))),z.energy)
plt.show()
