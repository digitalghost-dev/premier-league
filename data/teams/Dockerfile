FROM python:3.10-slim

ARG USERNAME=nonroot-user
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME

USER $USERNAME

WORKDIR /home/nonroot
RUN mkdir /home/nonroot/app


COPY teams-requirements.txt .
RUN pip3 install --no-cache-dir -r teams-requirements.txt

COPY . .

CMD ["python3", "teams.py"]