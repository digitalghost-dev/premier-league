FROM python:3.9

RUN mkdir /data-visualization
WORKDIR /data-visualization

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]