<p align="center">
<img height="150" width="150" src="https://cdn.simpleicons.org/premierleague/black/lightgray"/>
</p>

<h1 align="center">Premier League Data Pipeline</h1>

<p align="center">
<img src="https://img.shields.io/github/actions/workflow/status/digitalghost-dev/premier-league/ci.yaml?style=flat-square&logo=github&label=CI%2FCD"/>
<img src="https://img.shields.io/badge/Streamlit_App_Version-3.1.0-FF4B4B?style=flat-square&logo=streamlit"/>
<img src="https://img.shields.io/github/repo-size/digitalghost-dev/premier-league?style=flat-square&label=Repo%20Size&color=DEA584">
</p>


## Overview
* Prefect orchestrates Python scripts that extract data from two API sources, perfom transformations, then load processed data into a PostgreSQL database.
* Cloud Scheduler triggers a Docker container to run using Cloud Run Jobs. This container also performs ETL but loads the data into Firestore.
* The Streamlit App is containerized with Docker and hosted on Cloud Run as a Service.
* CI/CD is implemented with GitHub Actions to push a new Streamlit App image to Artifact Registry abnd deploy to Cloud Run as a Service when `streamlit_app.py` and/or `Dockerfile` files are updated.
    * Security scanning also takes place with Snyk, Syft, and Grype.

## Tests

### Checks
[![pre-commit](https://img.shields.io/badge/validation-pre--commit-FAB040?style=flat-square&logo=pre-commit)](https://pre-commit.com)

[![bandit](https://img.shields.io/badge/security-bandit-yellow?style=flat-square)](https://github.com/PyCQA/bandit)
[![black](https://img.shields.io/badge/style-black-black?style=flat-square)](https://github.com/psf/Black)
[![mypy](https://img.shields.io/badge/type_checking%20-mypy-0096c7?style=flat-square)](https://github.com/python/mypy)
[![Imports: isort](https://img.shields.io/badge/sorting-isort-ef8336?style=flat-square)](https://pycqa.github.io/isort/)
[![ruff](https://img.shields.io/badge/linter-ruff-FCC21B?style=flat-square&)](https://github.com/astral-sh/Ruff)

### Image Scanning
[![syft](https://img.shields.io/badge/SBOM-Syft-D939AB?style=flat-square)](https://github.com/anchore/syft)
[![grype](https://img.shields.io/badge/Image_Scanning-Grype-4A8CFF?style=flat-square)](https://github.com/anchore/grype)
[![snyk](https://img.shields.io/badge/Dependency_Security-Snyk-E5E4E2?style=flat-square)](https://snyk.io)


## Important Links

* [Documentation](https://docs.digitalghost.dev/)
* [Visualization](https://premierleague.streamlit.app/)
* [Version History](https://github.com/digitalghost-dev/premier-league/blob/main/CHANGELOG.md)

---

## Data and CI/CD Pipelines
### Data Pipeline
1. Prefect and Cloud Scheduler are the orchestration tools that trigger the ETL scripts.
2. Cloud Scheduler triggers the Cloud Run Job to execute.
3. The ETL process starts.
    * `ETL 1` calls the Football API `standings`, `teams`, and `top-scorers` endpoints and calls the `stadiums` endpoints from the Go API (`api/`); applies tranformations, creates dataframes, and defines schemas; then loads the dataframes into PostgreSQL. 
    * `ETL 2` calls the Football API `fixtures` endpoint; applies transforms and creates dictionaries; then loads the data as documents into a Firestore collection.
4. Data is then visualized on a dashboard using Streamlit.

### CI/CD Pipeline
The CI/CD pipeline is focused on the `streamlit_app.py` file and the Docker image that is built from it.

#### Building, Pushing, Deploying
1. The repository code is checked out and a Docker image containing the updated `streamlit_app.py` file will build.
2. The newly built Docker image will be pushed to [Artifact Registry](https://cloud.google.com/artifact-registry).
3. The Docker image is then deployed to [Cloud Run](https://cloud.google.com/run/docs/overview/what-is-cloud-run) as a Service.

#### Security
1. An [`SBOM`](https://www.linuxfoundation.org/blog/blog/what-is-an-sbom) is created with [Syft](https://github.com/anchore/syft).
2. The `SBOM` is then scanned with [Grype](https://github.com/anchore/grype).
3. The repository's dependencies are scanned with [Snyk](https://github.com/snyk/actions/tree/master/python-3.10).

### Pipeline Flowchart
![football-data-flowchart](https://storage.googleapis.com/pipeline-flowcharts/football-data-pipeline-flowchart.png)

### Infrastructure
![cloud](https://img.shields.io/badge/Cloud-GCP-4285F4?style=flat-square&logo=google-cloud)
![terraform](https://img.shields.io/badge/IaC-Terraform-5C4EE5?style=flat-square&logo=terraform)
![docker](https://img.shields.io/badge/Containers-Docker-2496ED?style=flat-square&logo=docker)
![prefect](https://img.shields.io/badge/Orchestration-Prefect-024DFD?style=flat-square&logo=prefect)

### Databases
![postgres](https://img.shields.io/badge/RDMS-PostgreSQL-336791?style=flat-square&labelColor=white&logo=postgresql)
![firestore](https://img.shields.io/badge/NoSQL-Firestore-FFA611?style=flat-square&logo=firebase)