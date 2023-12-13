# Dockerfile to build the Streamlit app.

FROM python:3.12-slim-bookworm

RUN groupadd -r streamlit_group

RUN useradd -r -g streamlit_group streamlit_user

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY components components
COPY streamlit_app.py .

RUN pip3 install --no-cache-dir -r requirements.txt

RUN chown -R streamlit_user:streamlit_group /app

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

USER streamlit_user

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0", "--theme.primaryColor=indigo", "--theme.textColor=black", "--theme.backgroundColor=#FFF", "--theme.secondaryBackgroundColor=#FFF"]