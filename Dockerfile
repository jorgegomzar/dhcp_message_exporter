FROM python:3.13-slim

WORKDIR /src

RUN apt update && apt install libpcap-dev gcc -y

COPY dhcp_message_exporter /src/dhcp_message_exporter
COPY main.py /src/main.py

COPY pyproject.toml /src/pyproject.toml
COPY poetry.lock /src/poetry.lock

RUN pip install "poetry==1.8.3"
RUN poetry install

CMD ["poetry", "run", "python", "main.py"]
