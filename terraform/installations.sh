sudo apt-get remove -y --purge man-db
sudo apt-get install -y python3-pip 
sudo apt-get install -y python3-venv
sudo apt install -y  git
git clone https://github.com/digitalghost-dev/premier-league.git
cd premier-league
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
pip install -U prefect
prefect deployment build -n premier-league-etl -p premier-league-work-pool -q premier-league-work-queue prefect/flows.py:premier_league_flow
prefect work-pool create 'premier-league-work-pool'
prefect deployment apply premier_league_flow-deployment.yaml