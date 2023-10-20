import whisper

model = whisper.load_model("base")

result = model.transcribe("recorded_audio.wav")
text = result["text"]

print(text)
