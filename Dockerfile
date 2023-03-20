# run this i.e. with
# docker build -t susi_api .
# docker run -d -p 8080:8080 -e OPENAI_API_KEY=<apikey> --name susi_api susi_api
FROM python:3.11-slim
ENV DEBIAN_FRONTEND noninteractive
ARG default_branch=master

COPY requirements.txt /app/
COPY src/ ./app/src/

WORKDIR /app
RUN \
    apt-get update && apt-get install -y ca-certificates bash build-essential && \
    export PYTHONHTTPSVERIFY=0 && \
    pip3 install --upgrade pip && \
    pip3 install --trusted-host=pypi.python.org --trusted-host=pypi.org --trusted-host=files.pythonhosted.org --no-cache-dir -r requirements.txt && \
    rm -rf /tmp/* /var/tmp/* /var/cache/apk/* /var/cache/distfiles/*

EXPOSE 8080
CMD ["python3", "src/main.py"]