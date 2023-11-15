<p align="center">
<img height="150" width="150" src="https://cdn.simpleicons.org/premierleague/gray"/>
</p>

<h1 align="center">Premier League Data Pipeline</h1>

<p align="center">
    <img src="https://img.shields.io/github/actions/workflow/status/digitalghost-dev/premier-league/ci_streamlit.yaml?style=flat-square&logo=github&label=CI%2FCD"/>
    <a href="https://github.com/digitalghost-dev/premier-league/blob/main/CHANGELOG.md">
        <img src="https://img.shields.io/badge/Dashboard_Version-2.11.1-FF4B4B?style=flat-square&logo=streamlit"/>
    </a>
    <a href="https://hub.docker.com/repository/docker/digitalghostdev/premier-league/general"> 
        <img src="https://img.shields.io/docker/image-size/digitalghostdev/premier-league/2.11.1?style=flat-square&logo=docker&label=Image%20Size&color=0DB7ED"/>
    </a>
    <img src="https://img.shields.io/github/repo-size/digitalghost-dev/premier-league?style=flat-square&label=Repo%20Size&color=DEA584">
</p>


## Overview
> This repository holds the code for a personnal project that I use to learn and experiment with different technologies cenetered around Data Engineering. The goal of this project is to create a data pipelines that extracts data from multiple sources, transforms the data, and loads the data into different database types and then creating visualizations with Streamlit.

> **Note**  
> Many items in this project do not make efficent sense on purpose for the sake of practicing and learning.

## Important Links

* [Documentation](https://docs.digitalghost.dev/) - currently under construction 🔨
* [Streamlit App](https://streamlit.digitalghost.dev/)
* [Version History](https://github.com/digitalghost-dev/premier-league/blob/main/CHANGELOG.md)

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

#### Data Pipeline 1
1. Data from the [Financial Modeling Prep API](https://site.financialmodelingprep.com) is extracted with Python using the `/quote` endpoint.
2. The data is loaded directly into a PostgreSQL database hosted on [Cloud SQL](https://cloud.google.com/sql?hl=en) with no transformations.
3. The prior steps are orchestrated with [Prefect](https://www.prefect.io).
4. Once the data is loaded into PostgreSQL, Datastream replicates the data into BigQuery. Datastream checks for staleness every 15 minutes.
5. [dbt](https://getdbt.com) is used to transform the data in BigQuery and create a view with transformed data.

#### Data Pipeline 2
1. Data is extracted from multiple API sources with Python:
    * Data from the [Football Data API](https://www.football-data.org/) is extracted with Python using the `/standings`, `/teams`, and `top_scorers` endpoints.
    * Data from the [NewsAPI](https://newsapi.org) is extracted with Python using the `/everything` endpoint with parameters set to search for the Premier League.
    * Data from the Go & Gin API is extracted with Python using the `/stadiums` endpoint.
2. Python performs any necessary transformations and loads the data into BigQuery.
3. The prior steps are orchestrated with [Prefect](https://www.prefect.io).

#### Data Pipeline 3
1. Data from the [Football Data API](https://www.football-data.org/) is extracted with Python using the `/fixtures` endpoint.
2. Python creates dictionaries from the data and loads the data into Firestore
3. The prior steps are orchestrated with Cloud Scheduler as a Docker container hosted on Cloud Run as a Job.

#### Pipeline Diagram
![data-pipeline](https://storage.googleapis.com/premier-league/data_pipelines.png)

### CI/CD Pipeline
The CI/CD pipeline is focused on building the Streamlit app into a Docker container that is then pushed to Artifact Registry and deployed to Cloud Run as a Service. Different architecutres are buit for different machine types and pushed to Docker Hub.

1. The repository code is checked out and a Docker image containing the updated `streamlit_app.py` file will build.
2. The newly built Docker image will be pushed to [Artifact Registry](https://cloud.google.com/artifact-registry).
3. The Docker image is then deployed to [Cloud Run](https://cloud.google.com/run/docs/overview/what-is-cloud-run) as a Service.

#### Pipeline Diagram
![cicd_pipeline](https://storage.googleapis.com/premier-league/cicd_pipeline.png)

---

## Security
* [Syft](https://github.com/anchore/syft) and [Grype](https://github.com/anchore/grype) work together to scan the Streamlit Docker image. Syft creates an [`SBOM`](https://www.linuxfoundation.org/blog/blog/what-is-an-sbom) and Grype scans the `SBOM` for vulnerabilities. The results are sent to the repository's Security tab.
* [Snyk](https://github.com/snyk/actions/tree/master/python-3.10) is also used to scan the repository for vulnerabilities in the Python packages.