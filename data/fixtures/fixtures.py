# Importing needed libraries.
import os

import firebase_admin
from firebase_admin import firestore
from google.cloud import secretmanager

import requests

os.environ["GCLOUD_PROJECT"] = "cloud-data-infrastructure"

def gcp_secret():
    client = secretmanager.SecretManagerServiceClient()
    name = "projects/463690670206/secrets/rapid-api/versions/1"
    response = client.access_secret_version(request={"name": name})
    payload = response.payload.data.decode("UTF-8")

    # Headers used for RapidAPI.
    headers = {
        "content-type": "application/octet-stream",
        "X-RapidAPI-Key": payload,
        "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
    }

    return headers

class Fixture(object):
    def __init__(self, date, teams, goals=None):
        self.date = date
        self.teams = teams
        self.goals = goals

    def __repr__(self):
        return (
            f'Fixture(\
                name={self.date}, \
                country={self.teams}, \
                goals={self.goals}\
            )'
        )

    def to_dict(self):
        return {
            'date': self.date,
            'teams': self.teams,
            'goals': self.goals
        }

def get_current_round():
    # Calling variables from previous functions.
    headers = gcp_secret()

    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures/rounds"
    querystring = {"league":"39","season":"2022","current":"true"}
    response = requests.get(url, headers=headers, params=querystring)

    current_round_response = response.json()["response"][0]

    return current_round_response

def build_current_round():
    # Calling variables from previous functions.
    headers = gcp_secret()
    current_round_response = get_current_round()
    
    url = "https://api-football-v1.p.rapidapi.com/v3/fixtures"
    querystring = {"league":"39","season":"2022","round":current_round_response}
    build_current_response = requests.get(url, headers=headers, params=querystring)

    return build_current_response

def firestore_load():
    current_round_response = get_current_round()
    build_current_response = build_current_round()
    db = firestore.Client()

    count = 0
    while count < 10:

        # Dictionaries to be written to each document.
        fixture_date = (build_current_response.json()['response'][count]['fixture']['date'])
        teams_dict = (build_current_response.json()['response'][count]['teams'])
        goal_dict = (build_current_response.json()['response'][count]['goals'])

        # Calling the away and home team names to build document name.
        away_team = (build_current_response.json()['response'][count]['teams']['away']['name'])
        home_team = (build_current_response.json()['response'][count]['teams']['home']['name'])

        fixture = Fixture(date=(fixture_date), teams=teams_dict, goals=goal_dict)
        db.collection(f'{current_round_response}').document(f'{away_team} vs {home_team}').set(fixture.to_dict())

        count += 1

    print(f"Document {current_round_response} has been loaded!")

if __name__ == "__main__":
    firestore_load()
