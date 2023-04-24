# API for solved AI challenges

In the last years a lot of challenges in the area of text understanding, image
and speech recognition and generation has been solved. This project aims to
channel well-known solutions into one proxy-like API which can be accessed
from a client application easily. The purpose of this approach is to replace
these proxy functions with on-site hosted AI functions.
The recent achievements in transformer models for the named function gives the
perspective that this is doable in the near future.

## API Design

To create a properly structured and well-named API we clone API defitions from
existing providers. To give different implementations a good structure, we
distinguish the challenge fields:

- text
- audio
- image
- video

More fields may arise in the future if these topics are fully covered with AI
functions and more challenging targets become into sight. Even if an
exponential growth in the named topics become vertical, new topics may appear
which have not yet reached human-level AI abilities.

To be able to have an easier approach to test the AI functions we also
provide a drop-in replacement to OpenAI API functions. Therefore we
re-implement specific OpenAI API endpoints as well.

## Integration into SUSI

SUSI (the new SUSI) will use this API as intelligent back-end. Since the
beginning of the SUSI project it was a target to bring all functions to a
RaspberryPi device "which could be used on Mars".
The final product should work completely offline.

During the first phase of the SUSI project until 2021 the biggest challenge was
on-device speech recognition. It looks like this is now possible. This project
therefore shall bootstrap a second SUSI development phase where we can build
upon now-existing technology.

## Usage

Install the python3 requirements first:

```
pip3 install -r requirements.txt
```

The API server can be started with

```
python3 src/main.py --openai_api_key <OPENAI-API-KEY>
```

This requires a OpenAI API key. Further versions of susi_api will not require
such a key because we implemented free and open replacements.

## Testing the API

There is a `test` subdirectory with test scripts and test data. Once the server
is running, you can do:

```
cd test/src
./test_voice.sh
```

This will use one of the provided test audio in `test/wav` to make a audio
transscription.

## Deployment using Docker

There is a Dockerfile included which encapsulates the server into a docker
image. During the creation of the image two voice decoder models are pre-
loaded (tiny and base) so that these models are present when the image is
deployed. You can make the image with

```
docker build -t susi_api .
```

The image can then be started with

```
docker run -d -p 8080:8080 -e OPENAI_API_KEY=<apikey> --name susi_api susi_api
```

..if a OpenAI API key shall be submitted. Otherwise you can just omit
the key:

```
docker run -d -p 8080:8080 --name susi_api susi_api
```
