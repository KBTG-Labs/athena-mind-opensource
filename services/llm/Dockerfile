FROM python:3.10.12

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*
    
COPY ./requirements.txt ./requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt 

COPY ./src/client ./src/client
COPY ./src/common ./src/common
COPY ./src/internal ./src/internal
COPY ./src/main.py ./src/main.py

CMD ["python", "-u", "./src/main.py"]