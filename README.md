# Premier League Data Visualization with Streamlit

<div>
    <img alt="Version" src="https://img.shields.io/badge/Current Version-1.0-blue.svg?cacheSeconds=2592000" />
    <img alt="Version" src="https://img.shields.io/badge/Project Number-2-orange.svg?cacheSeconds=2592000" />
</div>

## Description

> My second project, built to gain skills in: Python, BigQuery, Streamlit, Docker, GitHub Actions (CI/CD), plus working with and creating APIs.

This project uses the [Football API](https://rapidapi.com/api-sports/api/api-football/) and a self-built API (found in `/go-api`) to retrieve statistics from England's Premier League, the top division for men's soccer.

Using Python, some SQL, and BigQuery, this data pipeline turns raw JSON data into an interactive visualization on Streamlit.

Docker, GitHub Actions, and cron is also used to automate processes.

View the dashboard on [Streamlit](https://premierleague.streamlit.app/).

## How the Pipeline Works
1. A scheduled `cronjob` runs a Docker container everyday at 9:00AM PST. 
    1. The Docker image that creats the container builds from all files in `src/` and `./` 
2. `main.py` runs and calls the classes from files in `src/`.
3. API calls take place:
    1. `players.py`, `standings.py`, and `teams.py` reach out to the [Football API](https://rapidapi.com/api-sports/api/api-football/).
    2. `locations.py` reaches out to a self-built API written in Go and hosted on Cloud Run. (View the source code for the API in `go-api/`)
4. Each file on `src/` loads its data in its own table in BigQuery.
5. When the Streamlit page is loaded, it queries the data from BigQuery to present the data.
6. GitHub Actions has been set up for CI/CD which triggers on Pushes and Pull Requests.
    1. The CI/CD pipeline builds and pushes a new Docker image/tag to my private DockerHub repository.

### Pipeline Flowchart
![football-data-flowchart](https://storage.googleapis.com/personal-website-nv-bucket/flowcharts/football-data-pipeline-flowchart.png)

## Services Used
* **Scheduler:** [cron](https://en.wikipedia.org/wiki/Cron)
* **API:** [Football API](https://www.api-football.com), self-built API written in Go.
* **Visualization:** [Streamlit](https://streamlit.io)
* **Containerization:** [Docker](https://www.docker.com)
* **CI/CD:** [GitHub Actions](https://github.com/features/actions)
* **Google Cloud Services:**
    * **Data Warehouse:** [Google Cloud BigQuery](https://cloud.google.com/bigquery)
    * **Serverless Computing:** [Cloud Run](https://cloud.google.com/run/docs/overview/what-is-cloud-run)

## Changelog
### Version 1.0

* Initial stable release.