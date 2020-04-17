from functools import partial
import json

import requests


class AuthenticationError(Exception):
    pass


class ZBaseballClient(object):

    # TODO(joe): make this point to the actual domain
    API_URL = "http://localhost:8000"

    def __init__(self, username, password):
        self._username = username
        self._password = password
        self._token = None

    def _request(self, method="GET"):
        """Prebuild generic get requests for API endpoints"""
        headers = {"Content-Type": "application/json"}
        if self._token:
            headers.update({"Authorization": "Token {}".format(self._token)})
        if method == "GET":
            return partial(requests.get, headers=headers)
        elif method == "POST":
            return partial(requests.post, headers=headers)
        else:
            msg = "method: {} not a supported HTTP/HTTPS method for prebuilt requests"
            raise ValueError(msg.format(method))

    def _login(self):
        """Use credentials to receive a new api token"""
        login_endpoint = self.API_URL + "/api/auth/login/"
        response = self._request(method="POST")(
            url=login_endpoint,
            data=json.dumps({"username": self._username, "password": self._password}),
        )
        if response.status_code == 200:
            self._token = response.json()["token"]
        else:
            print(response.__dict__)
            msg = response.json()["msg"]
            raise AuthenticationError(msg)

    def _logout(self):
        """Indicate to the API we are done with our current token"""
        login_endpoint = self.API_URL + "/api/auth/logout/"
        response = self.__request("POST")(url=login_endpoint)
        self._token = None

    def get_game(self, game_id):
        """Retrieve data for a specific game"""
        if self._token is None:
            self._login()
        game_endpoint = self.API_URL + "/api/v1/games/{}/".format(game_id)
        response = self._request()(url=game_endpoint)
        if response.status_code != 200:
            raise Exception()
        return response.json()

    def list_games(self, year=None, team_id=None):
        """List games & allow some filters

        Args:
            year: int or None, you may filter games by year (or season if you prefer).
                  The API will return all regular season games as well as post season games.
                  The API does not distinguish between regular season games and post-season.
            team_id: str or None, filter games by a teams 3 character "team-id". E.g. "NYA"
                     NB! 3 Character team-id's are NOT neccessarily unique! Specifically, for
                     MIL and HOU, there are 2 "teams" with each of those ID's. Generally, this
                     happens when a particular team switches leagues from AL to NL or vice versa.

        Returns:
            a generator of dicts, such that each dict has some simple facts about each game.
            E.g.
            {
                "game_id": "NYA192104140",
                "date": "1921-04-14",
                "start_time": null,
                "home_team": 9,
                "away_team": 98
            }
            "home_team" and "away_team" are the UNIQUE team identifiers. Details about
            a team can be found using the teams API or the "list_teams" client method.
        """
        games_endpoint = self.API_URL + "/api/v1/games/"
        response = self._request()(url=games_endpoint)
        if response.status_code != 200:
            raise Exception()
        data = response.json()
        while len(data["results"]) > 0:
            print(len(data["results"]))
            for game in data["results"]:
                yield game
            next_url = data["next"]
            response = self._request()(url=next_url)
            data = response.json()
