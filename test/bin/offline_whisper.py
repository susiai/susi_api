import whisper

model = whisper.load_model("tiny")
result = model.transcribe("./../wav/test_english_alex_how.wav")
print(result["text"])
