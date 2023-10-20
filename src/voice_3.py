import pyaudio
import wave
import threading
import os
import whisper
from flask import Flask, request, jsonify
from zhconv import convert
import time
import random
import datetime


# 配置录制参数

app = Flask(__name__)

model = whisper.load_model("base")

flag = False

random_num = 0
folder_path = ""
OUTPUT_WAV_FILENAME = ""
used_set = set()

def make_dir():
    # 获取当前日期和时间
    current_datetime = datetime.datetime.now()

    # 格式化日期和时间作为文件夹名称（例如，2023-10-20-14-35-18）
    folder_name = current_datetime.strftime("%Y-%m-%d-%H-%M-%S")

    # 指定文件夹的完整路径
    global folder_path
    folder_path = os.path.join('../data/', folder_name)

    # 创建文件夹
    os.makedirs(folder_path)


def generate_random_num():
    global used_set
    random_8_digit = random.randint(10000000, 99999999)
    while random_8_digit in used_set:
        random_8_digit = random.randint(10000000, 99999999)

    used_set.add(random_8_digit)


    return random_8_digit

def voice():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 20
    global OUTPUT_WAV_FILENAME
    global folder_path
    global random_num
    OUTPUT_WAV_FILENAME = os.path.join(folder_path, "record_" + str(random_num) + ".wav")
    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    print("录音开始...")

    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
        if flag:
            break

    stream.stop_stream()
    stream.close()
    audio.terminate()

    # 保存录音为WAV文件
    with wave.open(OUTPUT_WAV_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    wf.close()

    print("录音结束.")


@app.route('/voice_start', methods=['GET'])
def startVoice():
    response = {"result": "OK"}

    def voice_thread():
        global random_num
        random_num = generate_random_num()
        voice()  # 执行 voice 函数

    # 创建并启动线程
    voice_thread = threading.Thread(target=voice_thread)
    #voice_thread.daemon = True
    voice_thread.start()

    return jsonify(response)


@app.route('/voice_end', methods=['GET'])
def voice2text():
    global flag
    flag = True
    time.sleep(0.2)

    # 语音转文本.
    global OUTPUT_WAV_FILENAME
    if not os.path.exists(OUTPUT_WAV_FILENAME):
        response = {"result": "请再尝试一次"}
        return jsonify(response)

    print("语音转换开始.")
    result = model.transcribe(OUTPUT_WAV_FILENAME)
    text = "请再尝试一次"
    if "text" in result:
         text = convert(result["text"], 'zh-cn')

    response = {"result": text}

    flag = False

    print("语音转文本完成.")

    return jsonify(response)


if __name__ == '__main__':
    make_dir()
    app.run(port=8080, host='0.0.0.0')

