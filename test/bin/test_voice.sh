#!/bin/bash
cd "`dirname $0`"

declare -a files=("test_english_alex_how.wav"
                  "test_english_ava_peter.wav"
                  "test_english_oliver_she.wav"
                  "test_english_samantha_six.wav"
                  "test_german_anna_falsches.wav"
                  "test_german_markus_franz.wav"
                  "test_german_petra_im.wav"
                  "test_german_yannick_zwölf.wav")

declare -a models=("whisper-1" "tiny" "base" "small" "medium" "large")
# whisper = 0M (cloud), tiny = 72M, base = 139M, small = 461M, medium = 1.42G, large = 2.87G

for model in "${models[@]}"
do

    start_time=$(date +%s)
    for file in "${files[@]}"
    do
	curl -X POST http://localhost:8080/api/audio/voice/transcriptions -H "Content-Type: multipart/form-data" -F file="@./../wav/${file}" -F model="${model}"
    done
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    echo "Total time for model '${model}': ${duration} seconds"
done

# Speed Tests (time should be less or equal to 30s to be usable):
# OpenAI Cloud: whisper-1 9-15s
# iMac 2015 4GHz 4x i7   : tiny 23s, base 30s, small 101s, medium 332s, large 631s
# MacBook Pro M1 Max 2021: tiny  7s, base 11s, small  32s, medium  88s, large 145s
