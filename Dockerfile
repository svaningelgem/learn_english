# app/Dockerfile

FROM python:3.9-slim

WORKDIR /html

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

VOLUME /html/videos

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]

RUN \
    --mount=type=cache,target=/var/cache/apt \
    apt update && apt -y upgrade && \
    apt install -y curl

COPY requirements.txt /html
RUN \
    --mount=type=cache,target=/root/.cache/pip \
    pip3 install -U -r requirements.txt && rm requirements.txt

COPY html/main.py /html
