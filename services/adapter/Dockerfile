FROM python:3.10.12
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY ./data ./data
COPY ./lib ./lib
COPY ./requirements.txt ./requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt 

COPY ./src/client ./src/client
COPY ./src/common ./src/common
COPY ./src/language_models ./src/language_models
COPY ./src/embeddings ./src/embeddings
COPY ./src/custom_chain ./src/custom_chain
COPY ./src/rag ./src/rag
COPY ./src/main.py ./src/main.py

CMD ["python", "src/main.py"]