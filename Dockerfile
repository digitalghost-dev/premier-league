FROM python:3.9

ADD main.py .

COPY requirements.txt .

COPY standings.py .

COPY config.py .

COPY auth.json .

RUN pip3 install -r requirements.txt

CMD [ "python", "./main.py" ]