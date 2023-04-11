# Premier League Data Visualization with Streamlit

![builds](https://img.shields.io/github/actions/workflow/status/digitalghost-dev/premier-league/cloudrun-build-and-deploy.yml?style=flat-square)
![version](https://img.shields.io/badge/streamlit_app_version-1.1.0-blue?style=flat-square)
![size](https://img.shields.io/github/repo-size/digitalghost-dev/premier-league?style=flat-square)
![black](https://img.shields.io/badge/code%20style-black-black?style=flat-square)

## Overview
* Extracts Premier League data with a self written API in Go and a Football API using Python.
* Data is transformed and processed, loaded into BigQuery, then sent to a Streamlit dashboard.
* Project is containerized with Docker and uses GitHub Actions for CI/CD.

### Important Links

* [Visualization](https://premierleague.streamlit.app/)
* [Documentation](https://github.com/digitalghost-dev/football-data-pipeline/wiki/Football-Data-Pipeline-Documentation)

## How the Pipeline Works
### Data Pipeline
1. Cloud Scheduler triggers Cloud Run Job executions twice a day at 12AM and 12PM PST.
2. Docker containers that are stored in Artifact Registry are ran as Jobs.
3. Each Docker container holds a Python script that is responsible for calling its respective API endpoint and extracting the data. The following files: `teams.py`, `standings.py`, and `players` call the Football API which is hosted on [RapidAPI](https://rapidapi.com/search/marketplace). While `locations.py` calls the self-built API written in Go which is hosted on Cloud Run as a Service.
4. The data is then transformed and dataframes are created.
5. Dataframes are sent to BigQuery.
6. When the Streamlit app loads, the BigQuery tables are queried to return the data.

### CI/CD Pipeline
1. When a push is made to the GitHub Repository on `main` branch, a workflow with GitHub Actions starts which begins by building a new Docker image.
2. The Docker image is then pushed to Artifact Registry.
3. The new image is then deployed to Cloud Run as a Job.

### Pipeline Flowchart
![football-data-flowchart](https://storage.googleapis.com/pipeline-flowcharts/football-data-pipeline-flowchart.png)

## Services Used
* **API:** [Football API](https://www.api-football.com), [self-built API written in Go](https://github.com/digitalghost-dev/football-data-pipeline/tree/main/locations-api)
* **CI/CD:** [GitHub Actions](https://github.com/features/actions)
* **Containerization:** [Docker](https://www.docker.com)
* **Google Cloud Services:**
    * **Data Warehouse:** [Google Cloud BigQuery](https://cloud.google.com/bigquery)
    * **Scheduler:** [Cloud Scheduler](https://cloud.google.com/scheduler)
    * **Serverless Computing:** [Cloud Run](https://cloud.google.com/run/docs/overview/what-is-cloud-run)
    * **Docker Repository:** [Artifact Registry](https://cloud.google.com/artifact-registry)
* **Visualization:** [Streamlit](https://streamlit.io)