FROM python:3.10-slim

RUN adduser --system nonroot
USER nonroot

WORKDIR /home/nonroot
RUN mkdir /home/nonroot/app

COPY ./requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY ./data/teams .

CMD ["python3", "teams.py"]