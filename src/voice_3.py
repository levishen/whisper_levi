import pyaudio
import wave
import threading
import os
import whisper
from flask import Flask, request, jsonify
from zhconv import convert
import time

# 配置录制参数

app = Flask(__name__)

model = whisper.load_model("base")

flag = False


def voice():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    RECORD_SECONDS = 20
    OUTPUT_WAV_FILENAME = "recorded_audio.wav"
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
        voice()  # 执行 voice 函数

    # 创建并启动线程
    voice_thread = threading.Thread(target=voice_thread)
    voice_thread.start()

    return jsonify(response)


@app.route('/voice_end', methods=['GET'])
def voice2text():
    global flag
    flag = True
    time.sleep(0.2)

    # 语音转文本.
    OUTPUT_WAV_FILENAME = "recorded_audio.wav"
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
    app.run(port=8080, host='0.0.0.0')

