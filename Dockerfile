FROM python:3.9

WORKDIR /data-visualization

ADD main.py .

COPY . .

RUN pip3 install -r requirements.txt

CMD [ "python", "./main.py" ]