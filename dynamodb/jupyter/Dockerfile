FROM python:3

WORKDIR /app

RUN apt-get update

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN python -m pip install -r requirements.txt

CMD exec jupyter lab --allow-root --no-browser --ip "*"