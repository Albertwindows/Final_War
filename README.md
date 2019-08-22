# 一个通过深度学习训练得到的离线小型关键字识别模型。
recorder.py :这个文件是为了收集录音文件，可以设置每次录音的时间长度和录音者的自己起的姓名用来区分不同的使用者。
configure_class.py :这个文件主要是调录音的参数
convert.py: 主要是用来标准化录音，采用基本声频的能量来处理。
参考：https://petewarden.com/2017/07/17/a-quick-hack-to-align-single-word-audio-recordings/
启动录音机：python recorder.py
