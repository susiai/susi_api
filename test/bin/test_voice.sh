cd "`dirname $0`"
curl -X POST http://localhost:8080/api/audio/transcriptions -H "Content-Type: multipart/form-data" -F file="@./../wav/test_english_alex_how.wav"
#curl -X POST http://localhost:8080/api/audio/transcriptions -H "Content-Type: multipart/form-data" -F file="@./../wav/test_english_alex_how.wav" -F model="whisper-1"
