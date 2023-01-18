FROM python:3.9

ENV PORT 8080
ENV HOST 0.0.0.0

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]