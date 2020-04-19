from datetime import datetime

import requests

from .exceptions import (
    APIException,
    GameNotFoundException,
    LoginError,
    PaymentRequiredException,
    PlayerNotFoundException,
    TooManyRequestsException,
)


class ZBaseballDataClient(object):

    # TODO(joe): make this point to the actual domain
    API_URL = "http://localhost:8000"

    def __init__(self, username=None, password=None, anon_user=False):
        """Init a client, anon users are allowed, but request rate is throttled server side"""
        self._username = username
        self._password = password
        self._token = None
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})
        if not anon_user:
            self._login()

    def _get(self, *args, **kwargs):
        """Get wrapper to catch and retry all HTTP 401s (token may be stale)"""
        response = self._session.get(*args, **kwargs)
        if response.status_code == 401:
            self._login()
            response = self._session.get(*args, **kwargs)
        elif response.status_code == 429:
            msg = "API query rate exceeded"
            raise TooManyRequestsException(msg)
        return response

    def _login(self):
        """Use credentials to receive a new api token"""
        login_endpoint = self.API_URL + "/api/auth/login/"
        response = self._session.post(
            url=login_endpoint,
            data={"username": self._username, "password": self._password},
        )
        if response.status_code == 200:
            token = response.json()["token"]
            self._session.headers.update({"Authorization": "Token {}".format(token)})
        else:
            msg = response.json()["msg"]
            raise LoginError(msg)

    def _logout(self):
        """Indicate to the API we are done with our current token"""
        login_endpoint = self.API_URL + "/api/auth/logout/"
        self._session.post(url=login_endpoint)
        del self._session.headers["Authorization"]

    def get_game(self, game_id):
        """Retrieve data for a specific game

        Args:
            game_id: str, the unique identifier for a particular game. E.g. "NYA192104130"

        Returns:
            A dict with details about that particular game. Fields including but not limited
            to: time, attendance, umpires, winning pitcher, losing pitcher, game site,
            weather, wind dir, temperature, game duration, date and a few more.
        """
        game_endpoint = self.API_URL + "/api/v1/games/{}/".format(game_id)
        response = self._get(url=game_endpoint)
        if response.status_code == 404:
            raise GameNotFoundException(response.json()["detail"])
        elif response.status_code != 200:
            msg = "Received HTTP status {} when fetching game_id={}".format(
                response.status_code, game_id
            )
            raise APIException(msg)
        return response.json()

    def list_game_events(self, game_id):
        """Get a list of play-by-play events for a specific game"""
        game_endpoint = self.API_URL + "/api/v1/games/{}/events/".format(game_id)
        response = self._get(url=game_endpoint)
        if response.status_code == 404:
            raise GameNotFoundException(response.json()["detail"])
        elif response.status_code == 403:
            raise PaymentRequiredException(response.json()["detail"])
        elif response.status_code != 200:
            msg = "Received HTTP status {} when fetching events for game_id={}".format(
                response.status_code, game_id
            )
            raise APIException(msg)
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
        filters = []
        if year:
            filters.append("year={}".format(year))
        if team_id:
            filters.append("team-id={}".format(team_id))

        games_endpoint = self.API_URL + "/api/v1/games/"
        if len(filters) > 0:
            games_endpoint += "?" + "&".join(filters)

        response = self._get(url=games_endpoint)
        if response.status_code != 200:
            msg = "Received HTTP status {} when listing games".format(
                response.status_code
            )
            raise APIException(msg)
        data = response.json()
        while len(data["results"]) > 0:
            for game in data["results"]:
                yield game
            next_url = data["next"]
            if next_url is None:
                break
            response = self._get(url=next_url)
            data = response.json()

    def get_player(self, retro_id):
        """Get some basic details about a player"""
        player_endpoint = self.API_URL + "/api/v1/players/{}/".format(retro_id)
        response = self._get(url=player_endpoint)
        if response.status_code == 404:
            msg = "Player with retro-id={} not found.".format(retro_id)
            raise PlayerNotFoundException(msg)
        elif response.status_code != 200:
            msg = "Received HTTP status {} when fetching player w/ retro-id={}".format(
                response.status_code, retro_id
            )
            raise APIException(msg)
        player_data = response.json()
        player_data["debut"] = datetime.strptime(
            player_data["debut"], "%Y-%m-%d"
        ).date()
        return player_data

    def list_players(self, search=None):
        """List players

        Args:
            search: str | None, an optional parameter that you can search for players
            on. The search term will return players with either first-names, last-names
            or retro_ids that are "LIKE" (read startswith) the search term.

        Returns:
            a generator of player-dict/objects, where each dict has first-name, last-name
            unique "retro_id" and the player's MLB debut.
        """
        player_endpoint = self.API_URL + "/api/v1/players/"
        if search:
            search.replace(" ", "%20")
            player_endpoint += "?search={}".format(search)

        response = self._get(url=player_endpoint)
        if response.status_code != 200:
            msg = "Received HTTP status {} when listing players.".format(
                response.status_code
            )
            raise APIException(msg)
        data = response.json()
        while len(data["results"]) > 0:
            for player in data["results"]:
                player["debut"] = datetime.strptime(player["debut"], "%Y-%m-%d").date()
                yield player
            next_url = data["next"]
            if next_url is None:
                break
            response = self._get(url=next_url)
            data = response.json()
