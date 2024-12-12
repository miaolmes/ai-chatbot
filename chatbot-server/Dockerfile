FROM python:3.11.11

COPY  . /app
WORKDIR /app

RUN pip install poetry
RUN poetry install

EXPOSE 8000
CMD ["poetry", "run", "python", "main.py"]
