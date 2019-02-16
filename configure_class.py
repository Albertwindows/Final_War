import pyaudio
class Configure:
    """
    配置信息存储，使用类别来存储
    """
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 0.5
    # 只是后缀名
    WAVE_OUTPUT_FILENAME = ".wav"