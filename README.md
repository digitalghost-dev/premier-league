# Premier League Data Visualization with Streamlit

<div>
    <img alt="Version" src="https://img.shields.io/badge/Project Number-2-orange.svg?cacheSeconds=2592000" />
</div>

## Description

This pipeline provides statistics and data from the current [Premier League](https://en.wikipedia.org/wiki/Premier_League) season. The metrics shown are:

* League Standings
* Map with points of stadium locations
* Statistics for Top 5 Teams
    * Form (last 5 games)
    * Clean Sheets
    * Penalties Scored
    * Penalties Missed
* Statistics for Top 5 Players
    * Name
    * Goals
    * Team
    * Nationality

View the dashboard on [Streamlit](https://premierleague.streamlit.app/).

## How the Pipeline Works
### Main Data Pipeline
1. Cloud Scheduler triggers a Cloud Run Job execution everyday at 9am PST.
2. Cloud Run Job runs a Docker container (which is stored in Artifact Registry).
3. Docker container consists of four Python files under `src/` which are separated by the specific API endpoint they call and `main.py` which acts as the primary driver of those four files by calling their classes and functions.
4. The following files: `src/teams.py`, `src/standings.py`, and `src/players` call the [Football API](https://rapidapi.com/api-sports/api/api-football/) which is hosted on [RapidAPI](https://rapidapi.com/search/marketplace). While `src/locations.py` calls the [self-built API written in Go](https://github.com/digitalghost-dev/football-data-pipeline/tree/main/locations-api) which is hosted on Cloud Run as a Service. All files extract, tranform, and load (ETL) the data. File names are based on the endpoints they reach.
5. Data processed from APIs are sent to BigQuery.
6. When the Streamlit app loads, the BigQuery tables are queried to return the data.

### CI/CD
1. When a push is made to the GitHub Repository, a workflow with [GitHub Actions](https://github.com/features/actions) starts which begins by building a new Docker image.
2. That Docker image is then pushed to [Artifact Registry](https://cloud.google.com/artifact-registry).
3. The workflow finishes by deploying that new image from Artifact Registry to a new Cloud Run Job.

### Pipeline Flowchart
![football-data-flowchart](https://storage.googleapis.com/pipeline-flowcharts/football-data-pipeline-flowchart.png)

## Services Used
* **Scheduler:** [Cloud Scheduler](https://cloud.google.com/scheduler)
* **API:** [Football API](https://www.api-football.com), [self-built API written in Go](https://github.com/digitalghost-dev/football-data-pipeline/tree/main/locations-api)
* **Visualization:** [Streamlit](https://streamlit.io)
* **Containerization:** [Docker](https://www.docker.com)
* **CI/CD:** [GitHub Actions](https://github.com/features/actions)
* **Google Cloud Services:**
    * **Data Warehouse:** [Google Cloud BigQuery](https://cloud.google.com/bigquery)
    * **Serverless Computing:** [Cloud Run](https://cloud.google.com/run/docs/overview/what-is-cloud-run)
    * **Docker Repository:** [Artifact Registry](https://cloud.google.com/artifact-registry)