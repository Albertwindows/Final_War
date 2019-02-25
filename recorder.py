from tkinter import *
from tkinter.ttk import *
import pyaudio
import wave
import random
import os
from configure_class import Configure
class Recorder:
    """
    这是一个录音文件，为收集资料进行前期的工作。
    """

    def __init__(self):

        self.cur_num=0#本次录音的编号，0对应“前进”（labels）
        self.labels=["前进","后退","左转","右转","停止","启动"]
        self.format_dir()
        self.label_len=len(self.labels)
        # 对应编号的次数
        self.times=[1]*len(self.labels)
        self.user_name=""
        self.font_size=12

        self.window = Tk()
        # 声明一个bar用来显示录音的进程
        self.pro = Progressbar(self.window, length=200, style='black.Horizontal.TProgressbar')

        # labels：
        self.lb_name = Label(self.window, text="您的名字设置：", font=("Arial Bold", self.font_size))
        self.lb_pro_left = Label(self.window, text="进度条：", font=("Arial Bold", self.font_size))
        self.lb_pro_right = Label(self.window, text="0%", font=("Arial Bold", self.font_size))
        # 需要设置text
        self.lb_please = Label(self.window, text="请说：", font=("Arial Bold", self.font_size))
        # 这个设置成第i遍说相同的词，需要在初始化中进行更改
        self.lb_times = Label(self.window, text="第1次", font=("Arial Bold", self.font_size))
        self.lb_time_set = Label(self.window, text="时间长度设置：", font=("Arial Bold", self.font_size))

        #Entry控件
        self.et_name=Entry(self.window,width=15)
        self.et_name.insert(0,'default')
        self.et_time=Entry(self.window,width=15)
        self.et_time.insert(0, '2.5')

        self.begin_button=Button(self.window,text="录音",command=self.record_run)
        self.save_button=Button(self.window,text="保存",command=self.save_wav)
        #设置按钮的初始化状态
        self.save_button['state']='disable'
        self.save_wav=True

        # 保存每次录音的中间结果，然后决定是不是要保存。
        self.frames=[]
        self.p=[]
        self.configure=Configure()
        # 初始化每个组件的位置
        self.place_all()


    def format_dir(self):
        for m_dir in self.labels:
            if not os.path.exists(m_dir):
                os.makedirs(m_dir)


    def read_configure(self):
        """
        function:读取配置信息，主要是时长，其他的配置暂时不进行改变
        文件命名的要求：录制人的昵称+_+nohash+_+录音的内容+编号+.wav
        :return:
        """

        self.user_name=self.et_name.get()
        self.configure.WAVE_OUTPUT_FILENAME=self.user_name + \
                                            '_nohash_' + \
                                            self.labels[self.cur_num] + \
                                            '_'+str(self.times[self.cur_num]) + '_'\
                                            '.wav'

        self.configure.RECORD_SECONDS=float(eval(self.et_time.get()))

    def get_cur_label(self):
        """

        :return: 返回的是str类型的label
        """
        return self.labels[self.cur_num]

    def update_labels(self):
        """
        更新labels
        :return:
        """
        # 产生一个随机数来显示说明要说内容的编号
        self.cur_num = int((random.random()) * len(self.labels))
        self.lb_please.configure(text='请说：'+self.get_cur_label())
        self.lb_times.configure(text='第'+str(self.times[self.cur_num])+'次')
        self.window.update()

    def save_wav(self):
        self.times[self.cur_num] += 1  # 计数


        self.save_button['state']='disable'
        frames=self.frames
        p=self.p
        c=self.configure
        wf = wave.open('./'+self.get_cur_label()+'/'+c.WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(c.CHANNELS)
        wf.setsampwidth(p.get_sample_size(c.FORMAT))
        wf.setframerate(c.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()


    def record_run(self):
        """
        点击开始录音的按钮，开始录音并且随着录音的进程更新进度条。
        :return:
        """

        self.update_labels()
        self.begin_button['state']='disable'
        self.read_configure()

        p = pyaudio.PyAudio()
        # 加载配置信息
        c=self.configure
        stream = p.open(format=c.FORMAT,
                        channels=c.CHANNELS,
                        rate=c.RATE,
                        input=True,
                        frames_per_buffer=c.CHUNK)

        print("* recording")

        frames = []

        n=int(c.RATE / c.CHUNK * c.RECORD_SECONDS)

        for i in range(0, n):
            data = stream.read(c.CHUNK)
            self.pro['value']=int(100/(n-1)*i)
            self.lb_pro_right.configure(text=str(int(100/(n-1)*i))+"%")
            self.window.update()
            frames.append(data)

        print("* done recording")

        stream.stop_stream()
        stream.close()
        p.terminate()

        self.frames=frames
        self.p=p



        self.begin_button['state']='normal'
        self.save_button['state']='normal'



    def place_all(self):
        # 控件的分布情况
        self.lb_name.grid(column=0, row=0)
        self.lb_pro_left.grid(column=0, row=1)
        self.pro.grid(column=1, row=1)
        self.lb_pro_right.grid(column=2, row=1)
        self.lb_please.grid(column=0, row=2)
        self.lb_times.grid(column=0,row=3)
        self.lb_time_set.grid(column=0,row=4)

        self.begin_button.grid(column=0,row=5)
        self.save_button.grid(column=1,row=5)

        self.et_name.grid(column=1,row=0)
        self.et_time.grid(column=1,row=4)

    def main(self):
        self.window.title("Record")
        self.window.geometry('400x290')
        self.window.mainloop()






if __name__=="__main__":
    c=Recorder()
    c.main()
