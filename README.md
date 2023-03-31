# Premier League Data Visualization with Streamlit
<sup>*Backend infrastructure source code for https://premierleague.streamlit.app*</sup>

## Overview
* Extracts Premier League data with a self written API in Go and a Football API using Python.
* Data is transformed and processed, loaded into BigQuery then sent to a Streamlit dashboard.
* Project is containerized with Docker and uses GitHub Actions for CI/CD.

### Important Links

* [Visualization](https://premierleague.streamlit.app/)
* [Documentation](https://github.com/digitalghost-dev/football-data-pipeline/wiki/Football-Data-Pipeline-Documentation)

## How the Pipeline Works
### Main Data Pipeline
1. Cloud Scheduler triggers a Cloud Run Job execution everyday at 9am PST.
2. Cloud Run Job runs a Docker container that is stored in Artifact Registry.
3. The Docker container consists of four Python files under `src/` which are separated by the specific API endpoint they call and `main.py` which acts as the primary driver of those four files by calling their classes and functions.
4. The following files: `src/teams.py`, `src/standings.py`, and `src/players` call the Football API which is hosted on [RapidAPI](https://rapidapi.com/search/marketplace). While `src/locations.py` calls the self-built API written in Go which is hosted on Cloud Run as a Service. All files extract, tranform, and load (ETL) the data. File names are based on the endpoints they reach.
5. Data processed from APIs are sent to BigQuery.
6. When the Streamlit app loads, the BigQuery tables are queried to return the data.

### CI/CD
1. When a push is made to the GitHub Repository on the `main` branch, a workflow with GitHub Actions starts which begins by building a new Docker image.
2. The Docker image is then pushed to Artifact Registry.

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