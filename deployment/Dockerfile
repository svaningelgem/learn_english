# app/Dockerfile

FROM python:3.9-slim

WORKDIR /html

# RUN apt-get update && apt-get -y upgrade && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /html

RUN pip3 install -r requirements.txt && rm requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

VOLUME /html/videos

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]


COPY html/main.py /html
