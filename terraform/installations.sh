#!/bin/bash

sudo apt-get remove -y --purge man-db
sudo apt-get install -y python3-pip 
sudo apt-get install -y python3-venv
sudo apt install -y git
git clone https://github.com/digitalghost-dev/premier-league.git
cd premier-league
python3 -m venv env
source env/bin/activate
pip install -r terraform/req.txt
prefect --version
sleep 10
prefect deployment build -n premier-league-etl -p premier-league-work-pool -q premier-league-work-queue prefect/flows.py:premier_league_flow
prefect work-pool create 'premier-league-work-pool' --type prefect-agent
prefect deployment apply premier_league_flow-deployment.yaml