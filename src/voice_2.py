import pyaudio
import wave
import os
from flask import Flask, request, jsonify


# 参数设置
FORMAT = pyaudio.paInt16  # 采样格式为16位整数
CHANNELS = 1  # 单声道
RATE = 44100  # 采样率（每秒采样点数）
CHUNK = 1024  # 每次读取的音频数据块大小
RECORD_SECONDS = 5  # 录音时长（秒）
OUTPUT_FILENAME = "output.wav"  # 录音保存的WAV文件名
MP3_FILENAME = "output.mp3"  # 转换后的MP3文件名

app = Flask(__name__)

audio = pyaudio.PyAudio()


@app.route('/voice_start', methods=['GET'])
def startVoice():
    response = {"result": "OK"}
    # 打开音频流
    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, frames_per_buffer=CHUNK)

    print("录音中...")

    frames = []

    # 录音
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("录音结束")

    # 停止音频流和PyAudio
    stream.stop_stream()
    stream.close()
    audio.terminate()

    global OUTPUT_FILENAME
    # 保存录音为WAV文件
    with wave.open(OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    text = "OK"

    print(f"录音已保存为{MP3_FILENAME}")

    response = {"result": text}

    return jsonify(response)


@app.route('/voice_end', methods=['GET'])
def voice2text():
    global flag
    flag = False
    # time.sleep(0.2)

    #语音转文本.
    global OUTPUT_FILENAME
    if not os.path.exists(OUTPUT_FILENAME):
        response = {"result": "请再尝试一次"}
        return jsonify(response)

    result = model.transcribe(OUTPUT_WAV_FILENAME)
    text = "请再尝试一次"
    if "text" in result:
        text = convert(result["text"], 'zh-cn')

    response = {"result": text}

    return jsonify(response)



if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')
