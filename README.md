# Premier League Data Pipeline & Visualization with Streamlit

![builds](https://img.shields.io/github/actions/workflow/status/digitalghost-dev/premier-league/ci.yaml?style=flat-square)
![version](https://img.shields.io/badge/streamlit_app_version-3.0.0-blue?style=flat-square)
![size](https://img.shields.io/github/repo-size/digitalghost-dev/premier-league?style=flat-square)
![black](https://img.shields.io/badge/code%20style-black-black?style=flat-square)
![pylint](https://img.shields.io/badge/linting-pylint-yellowgreen?style=flat-square)
![sbom](https://img.shields.io/badge/sbom-syft-D939AB?style=flat-square)
![scanning](https://img.shields.io/badge/scanning-grype-4A8CFF?style=flat-square)
![dependency-security](https://img.shields.io/badge/dependency%20security-snyk-E5E4E2?style=flat-square)

## Overview
* Airflow orchestrates Python scripts that extract data from two API sources, perfom transformations, then load processed data into a PostgreSQL database.
* Cloud Scheduler triggers a Docker container to run using Cloud Run Jobs. This container also performs ETL but loads the data into Firestore.
* The Streamlit App is containerized with Docker and hosted on Cloud Run as a Service.
* CI/CD is implemented with GitHub Actions to push a new Streamlit App image to Artifact Registry abnd deploy to Cloud Run as a Service when `streamlit_app.py` and/or `Dockerfile` files are updated.
    * Security scanning also takes place with Snyk, Bandit, Syft, and Grype.

## Important Links

* [Documentation](https://digitalghost-dev.notion.site/12d644bff83f46359c3de9036d84f0b0?v=8e7efc5e047840a1adfce3c9cf1c63ba&pvs=4)
* [Visualization](https://premierleague.streamlit.app/)
* [Version History](https://github.com/digitalghost-dev/premier-league/blob/main/CHANGELOG.md)

---

## ETL and CI/CD Pipelines
### Data Pipeline
1. Airflow and Cloud Scheduler are the orchestration tools that trigger the ETL scripts.
2. Cloud Scheduler triggers the Cloud Run Job to execute.
3. The ETL process starts.
    * `ETL 1` calls the Football API `standings`, `teams`, and `top-scorers` endpoints and calls the `stadiums` endpoints from the Go API (`api/`); applies tranformations, creates dataframes, and defines schemas; then loads the dataframes into PostgreSQL. 
    * `ETL 2` calls the Football API `fixtures` endpoint; applies transforms and creates dictionaries; then loads the data as documents into a Firestore collection.
4. Data is then visualized on a dashboard using Streamlit.

### CI/CD Pipeline
#### Formatting and Linting
1. `streamlit_app.py` will be checked with the [Black](https://github.com/psf/black) code formatter. 
2. If Black finds changes to make, they will be made then committed to the repository.
    * If there are no changes to be made, this step will be skipped.
3. `pylint` is used as a linter and its output is captured as a `.txt` file and sent to a [Cloud Storage](https://cloud.google.com/storage) bucket.

#### Docker Image
1. The repository code is checked out and a Docker image containing the updated `streamlit_app.py` file will build.
2. The newly built Docker image will be pushed to [Artifact Registry](https://cloud.google.com/artifact-registry).
3. The Docker image is then deployed to [Cloud Run](https://cloud.google.com/run/docs/overview/what-is-cloud-run) as a Service.

#### Security
1. An [`SBOM`](https://www.linuxfoundation.org/blog/blog/what-is-an-sbom) is created with [Syft](https://github.com/anchore/syft).
2. The `SBOM` is then scanned with [Grype](https://github.com/anchore/grype).
3. The repository's dependencies are scanned with [Snyk](https://github.com/snyk/actions/tree/master/python-3.10).
4. The `streamlit_app.py` file is scanned with [Bandit](https://github.com/PyCQA/bandit).

### Pipeline Flowchart
![football-data-flowchart](https://storage.googleapis.com/pipeline-flowcharts/football-data-pipeline-flowchart.png)

## Services Used
* **API:** [Football API](https://www.api-football.com), [self-built API written in Go](https://github.com/digitalghost-dev/football-data-pipeline/tree/main/locations-api)
* **CI/CD:** [GitHub Actions](https://github.com/features/actions)
* **Containerization:** [Docker](https://www.docker.com)
* **Google Cloud Services:**
    * **Relational Database:** [PostgreSQL on Cloud SQL](https://cloud.google.com/sql)
    * **NoSQL Document Database:** [Firestore](https://cloud.google.com/firestore/)
    * **Object Storage:** [Cloud Storage](https://cloud.google.com/storage)
    * **Repository:** [Artifact Registry](https://cloud.google.com/artifact-registry)
    * **Scheduler:** [Cloud Scheduler](https://cloud.google.com/scheduler)
    * **Serverless Computing:** [Cloud Run](https://cloud.google.com/run/docs/overview/what-is-cloud-run)
* **Orchestration:** [Airflow](https://airflow.apache.org/)
* **Visualization:** [Streamlit](https://streamlit.io)