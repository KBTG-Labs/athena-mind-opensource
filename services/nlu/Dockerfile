FROM python:3.10.12
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY ./data ./data
COPY ./lib ./lib
COPY ./requirements.txt ./requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt 

COPY ./.chainlit ./.chainlit
COPY ./src/client ./src/client
COPY ./src/common ./src/common
COPY ./src/language_models ./src/language_models
COPY ./src/router ./src/router
COPY ./src/main.py ./src/main.py
COPY ./chainlit.md ./chainlit.md

CMD ["chainlit", "run", "src/main.py"]