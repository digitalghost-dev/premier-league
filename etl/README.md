<p align="center">
<img height="150" width="150" src="https://cdn.simpleicons.org/premierleague/gray"/>
</p>

# Data Pipelines

This directory contains the ETL (Extract, Transform, Load) scripts and related files for the Premier League project. 

## Overview

The `etl` directory is responsible for extracting data from various sources, transforming it into a consistent format, and loading it into BigQuery, Firestore, and PostgreSQL.

## Data Pipelines Diagram
<figure>
    <img 
        src="https://storage.googleapis.com/premier_league_bucket/flowcharts/data_pipelines_flowchart.png" 
        alt="data-pipeline" 
        width="800"
    />
    <figcaption>Diagram of a data pipelines in this project</figcaption>
</figure>

## Data Sources
* [Football API](https://rapidapi.com/api-sports/api/api-football)
* [News API](https://newsapi.org)
* [Financial Modeling Prep](https://site.financialmodelingprep.com/developer)
* [MapBox](https://www.mapbox.com)
* [YouTube API](https://developers.google.com/youtube/v3)