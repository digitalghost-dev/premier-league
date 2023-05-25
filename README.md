# Premier League Data Visualization with Streamlit

![builds](https://img.shields.io/github/actions/workflow/status/digitalghost-dev/premier-league/ci.yml?style=flat-square)
![version](https://img.shields.io/badge/streamlit_app_version-2.3.0-blue?style=flat-square)
![size](https://img.shields.io/github/repo-size/digitalghost-dev/premier-league?style=flat-square)
![black](https://img.shields.io/badge/code%20style-black-black?style=flat-square)
![pyling](https://img.shields.io/badge/linting-pylint-yellowgreen?style=flat-square)

## Overview
* Extracts Premier League data with a self written API in Go and a Football API using Python.
* Data is transformed and processed, loaded into BigQuery, then sent to a Streamlit dashboard.
* Project is containerized with Docker and uses GitHub Actions for CI/CD.

### Important Links

* [Documentation](https://digitalghost-dev.notion.site/12d644bff83f46359c3de9036d84f0b0?v=4c615e0378304f499d6fdfeaf223fa77)
* [Visualization](https://premierleague.streamlit.app/)
* [Version History](https://github.com/digitalghost-dev/premier-league/blob/main/CHANGELOG.md)

## How the Pipeline Works
### Data Pipeline
1. Cloud Scheduler triggers Cloud Run Job executions twice a day at 12AM and 12PM PST.
2. Docker containers that are stored in Artifact Registry are ran as Jobs.
3. Each Docker container holds a Python script that is responsible for calling its respective API endpoint to extract, transform, and load the data.

|            | Fixtures      | Locations      | Players      | Standings      | Teams        |
| ---------- | ------------- | -------------- | ------------ | -------------- | ------------ |
| File       | `fixtures.py` | `locations.py` | `players.py` | `standings.py` | `teams.py`   |
| API Source | Football API  | Cloud Run      | Football API | Football API   | Football API |
| Storage    | Firestore     | BigQuery       |  BigQuery    | BigQuery       |  BigQuery    |

4. The data is transformed, dataframes and dictionaries are created.
5. Dataframes are sent to BigQuery and dictionaries are sent to Firestore.
6. When the Streamlit app loads, the BigQuery tables and Firestore documents are queried to return and load the data.

### CI/CD Pipeline
1. The endpoint Python files will be checked with the [Black](https://github.com/psf/black) code formatter. 
2. If Black finds changes to make, they will be made then committed to the repository.
    * If there are no changes to be made, this step will be skipped.
3. Five jobs take place simultaneously which build each Docker image related to the endpoint. [Pylint](https://github.com/pylint-dev/pylint) is also used to lint the same Python files as Black in job 1 and store the output to a Google Cloud Cloud Storage bucket.
4. The Docker images are then pushed to Artifact Registry and deployed as new Cloud Run Jobs.

### Pipeline Flowchart
![football-data-flowchart](https://storage.googleapis.com/pipeline-flowcharts/football-data-pipeline-flowchart.png)

## Services Used
* **API:** [Football API](https://www.api-football.com), [self-built API written in Go](https://github.com/digitalghost-dev/football-data-pipeline/tree/main/locations-api)
* **CI/CD:** [GitHub Actions](https://github.com/features/actions)
* **Containerization:** [Docker](https://www.docker.com)
* **Google Cloud Services:**
    * **Data Warehouse:** [Google Cloud BigQuery](https://cloud.google.com/bigquery)
    * **NoSQL Document Database:** [Firestore](https://cloud.google.com/firestore/)
    * **Scheduler:** [Cloud Scheduler](https://cloud.google.com/scheduler)
    * **Serverless Computing:** [Cloud Run](https://cloud.google.com/run/docs/overview/what-is-cloud-run)
    * **Docker Repository:** [Artifact Registry](https://cloud.google.com/artifact-registry)
* **Visualization:** [Streamlit](https://streamlit.io)