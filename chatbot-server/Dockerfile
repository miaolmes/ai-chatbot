FROM python:3.11.11

COPY  . /app
WORKDIR /app

RUN pip install poetry
RUN poetry install

CMD ["poetry", "run", "python", "main.py"]
