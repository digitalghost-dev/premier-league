# Dockerfile to build and host the Streamlit app.

# build and run commands while in pwd:
# build: docker build -t streamlit:{tag} .
# run: docker run -p 8501:8501 -v $(pwd)/.streamlit/secrets.toml:/app/.streamlit/secrets.toml streamlit:{tag}

FROM python:3.10.12-slim-buster

# Create streamlit_group
RUN groupadd -r streamlit_group

# Create streamlit_user abd add it to the streamlit_group
RUN useradd -r -g streamlit_group streamlit_user

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY streamlit_app.py .
COPY .streamlit/config.toml ./.streamlit/config.toml

RUN pip3 install --no-cache-dir -r requirements.txt

RUN chown -R streamlit_user:streamlit_group /app

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Switch to streamlit_user for execution
USER streamlit_user

ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]