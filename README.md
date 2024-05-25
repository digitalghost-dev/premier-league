<p align="center">
<img height="150" width="150" src="https://cdn.simpleicons.org/premierleague/gray"/>
</p>

<h1 align="center">Premier League Data Pipeline</h1>

<p align="center">
    <img src="https://img.shields.io/github/actions/workflow/status/digitalghost-dev/premier-league/ci_streamlit.yaml?style=flat-square&logo=github&label=CI%2FCD"/>
    <a href="https://github.com/digitalghost-dev/premier-league/blob/main/CHANGELOG.md">
        <img src="https://img.shields.io/badge/Dashboard_Version-2.17.1-FF4B4B?style=flat-square&logo=streamlit"/>
    </a>
    <a href="https://hub.docker.com/repository/docker/digitalghostdev/premier-league/general"> 
        <img src="https://img.shields.io/docker/image-size/digitalghostdev/premier-league/2.17.1?style=flat-square&logo=docker&label=Image%20Size&color=0DB7ED"/>
    </a>
    <img src="https://img.shields.io/github/repo-size/digitalghost-dev/premier-league?style=flat-square&label=Repo%20Size&color=DEA584">
</p>

> [!WARNING]
> After a year and some change of building this project, it's time for me to archive it. I've started to use these tools in my current position so learning these on my own and spending my own money on paying for the Football API and Google Cloud services no longer makes sense. I'm switching my focus on learning Golang!

## Overview
This repository contains a personal project designed to enhance my skills in Data Engineering. It focuses on developing data pipelines that extract, transform, and load data from various sources into diverse databases. Additionally, it involves creating a dashboard with visualizations using Streamlit.

> [!IMPORTANT]
> Many architectural choices and decisions in this project may not make the most efficent sense on purpose for the sake of practicing and learning.

## Infrastructure
### Tools & Services
![cloud](https://img.shields.io/badge/Google_Cloud-4285F4?style=flat-square&logo=googlecloud&logoColor=white) ![streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) ![terraform](https://img.shields.io/badge/Terraform-844FBA?style=flat-square&logo=terraform&logoColor=white) ![docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) ![prefect](https://img.shields.io/badge/-Prefect-070E10?style=flat-square&logo=prefect) ![dbt](https://img.shields.io/badge/dbt-FF694B?style=flat-square&logo=dbt&logoColor=white)

### Databases
![firestore](https://img.shields.io/badge/Firestore-FFCA28?style=flat-square&logo=firebase&logoColor=white) ![postgres](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white) ![bigquery](https://img.shields.io/badge/BigQuery-669DF6?style=flat-square&logo=googlebigquery&logoColor=white)

### Code Quality
![pre-commit](https://img.shields.io/badge/pre--commit-FAB040?style=flat-square&logo=pre-commit&logoColor=white)

| Security Linter | Code Formatting | Type Checking | Code Linting |
| --- | --- | --- | --- |
| [`bandit`](https://github.com/PyCQA/bandit) | [`ruff-format`](https://github.com/astral-sh/ruff) | [`mypy`](https://github.com/python/mypy) | [`ruff`](https://github.com/astral-sh/ruff) |

---

## Data and CI/CD Pipelines
### Data Pipelines

<h4><u>Data Pipeline 1</u></h4>

Orchestrated with [Prefect](https://www.prefect.io), a Python file is ran to extract stock data for Manchester United.

1. Data from the [Financial Modeling Prep API](https://site.financialmodelingprep.com) is extracted with Python using the `/quote` endpoint.
2. The data is loaded directly into a PostgreSQL database hosted on [Cloud SQL](https://cloud.google.com/sql?hl=en) with no transformations.
3. Once the data is loaded into PostgreSQL, Datastream replicates the data into BigQuery. Datastream checks for staleness every 15 minutes.
4. [dbt](https://getdbt.com) is used to transform the data in BigQuery and create a view with transformed data.

<h4><u>Data Pipeline 2</u></h4>

Orchestrated with [Prefect](https://www.prefect.io), Python files are ran that perform a full ETL process.

1. Data is extracted from multiple API sources:
    * Data from the [Football Data API](https://www.football-data.org/) is extracted to retrieve information on the current standings, team statistics, top scorers, squads, fixtures, and the current round. The following endpoints are used:
        * `/standings`
        * `/teams`
        * `/top_scorers`
        * `/squads`
        * `/fixtures/current_round`
        * `/fixtures`
    * Data from the [NewsAPI](https://newsapi.org) is extracted to retrieve news article links with filters set to the Premier League from Sky Sports, The Guardian, and 90min. The following endpoints are used:
        * `/everything`
    * Data from a self-built API written in Golang is extracted to retrieve information on teams' stadiums. The following endpoints are used:
        * `/stadiums`
    * Data from the [YouTube API](https://developers.google.com/youtube/v3) is extracted to retrieve the latest highlights from NBC Sports YouTube channel.
2. Python performs any necessary transformations such as coverting data types or checking for `NULL` values
3. Majority of the data is then loaded into **BigQuery** in their respective tables. Fixture data is loaded into **Firestore** as documents categoirzed by the round number.

<h4><u>Data Pipeline 3</u></h4>
1. Daily exports of the standings and top scorers data in BigQuery are exported to a Cloud Storage bucket using Cloud Scheduler to be used in another project.
    * The other project is a [CLI](https://github.com/digitalghost-dev/pl-cli/) tool written in Golang.

<h4><u>Pipeline Diagram</u></h4>

![data-pipeline-flowchart](https://storage.googleapis.com/premier_league_bucket/flowcharts/data_pipelines_flowchart.png)

### CI/CD Pipeline
The CI/CD pipeline is focused on building the Streamlit app into a Docker container that is then pushed to Artifact Registry and deployed to Cloud Run as a Service. Different architecutres are buit for different machine types and pushed to Docker Hub.

1. The repository code is checked out and a Docker image containing the updated `streamlit_app.py` file will build.
2. The newly built Docker image will be pushed to [Artifact Registry](https://cloud.google.com/artifact-registry).
3. The Docker image is then deployed to [Cloud Run](https://cloud.google.com/run/docs/overview/what-is-cloud-run) as a Service.

#### Pipeline Diagram
![cicd_pipeline](https://storage.googleapis.com/premier_league_bucket/flowcharts/cicd_pipeline_flowchart.png)

---

## Security
* [Syft](https://github.com/anchore/syft) and [Grype](https://github.com/anchore/grype) work together to scan the Streamlit Docker image. Syft creates an [`SBOM`](https://www.linuxfoundation.org/blog/blog/what-is-an-sbom) and Grype scans the `SBOM` for vulnerabilities. The results are sent to the repository's Security tab.
* [Snyk](https://github.com/snyk/actions/tree/master/python-3.10) is also used to scan the repository for vulnerabilities in the Python packages.
