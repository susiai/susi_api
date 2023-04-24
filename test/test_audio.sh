#curl http://localhost:8080/voice/transcriptions \
curl http://localhost:8080/v1/audio/transcriptions \
  -H "Content-Type: multipart/form-data" \
  -F file="@wav/test_english_oliver_she.wav" \
  -F model="whisper-1"
