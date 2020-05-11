from datetime import datetime

import requests

from .constants import GAME_TYPES
from .exceptions import (
    APIException,
    ClientException,
    GameNotFoundException,
    LoginError,
    PaymentRequiredException,
    PlayerNotFoundException,
    TooManyRequestsException,
    TeamNotFoundException,
    ParkNotFoundException,
)


class ZBaseballDataClient(object):

    # TODO(joe): make this point to the actual domain
    API_URL = "http://localhost:8000"

    def __init__(self, username=None, password=None):
        self._username = username
        self._password = password
        self._token = None
        self._session = requests.Session()
        self._session.headers.update({"Accept": "application/json"})
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
        elif response.status_code == 402:
            msg = response.json()["detail"]
            raise PaymentRequiredException(msg)
        return response

    def _login(self):
        """Use credentials to grab a new api token"""
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
        game = response.json()
        game["date"] = datetime.strptime(game["date"], "%Y-%m-%d").date()
        return game

    def get_game_events(self, game_id):
        """Get a list of play-by-play events for a specific game"""
        game_endpoint = self.API_URL + "/api/v1/games/{}/events/".format(game_id)
        response = self._get(url=game_endpoint)
        if response.status_code == 404:
            raise GameNotFoundException(response.json()["detail"])
        elif response.status_code != 200:
            msg = "Received HTTP status {} when fetching events for game_id={}".format(
                response.status_code, game_id
            )
            raise APIException(msg)
        return response.json()

    def get_games(
        self,
        year: int = None,
        team_id: str = None,
        start_date: str = None,
        end_date: str = None,
        game_type: str = None,
    ):
        """Get games & allow some filters

        Args:
            year: int or None, you may filter games by year (or season if you prefer).
                  The API will return all regular season games as well as post season games.
                  The API does not distinguish between regular season games and post-season.
            team_id: str or None, filter games by a teams 3 character "team-id". E.g. "NYA"
                     NB! 3 Character team-id's are NOT neccessarily unique! Specifically, for
                     MIL and HOU, there are 2 "teams" with each of those ID's. Generally, this
                     happens when a particular team switches leagues from AL to NL or vice versa.
            start_date: str, e.g. 2019-01-01 only return games after this date
            end_date: str, only return games before this date
            game_type: str, filter based on regular season games, postseason, allstar etc.
                       SEE constants.py for the full list of options. Use POST for only postseason
                       games, REG for only regular season games, None for all games.

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
            a team can be found using the teams API or the "get_teams" client method.
        """
        filters = []
        if year:
            filters.append("year={}".format(year))
        if team_id:
            filters.append("team-id={}".format(team_id))
        if start_date:
            filters.append("start-date={}".format(start_date))
        if end_date:
            filters.append("end-date={}".format(end_date))
        if game_type:
            if game_type != "POST" and game_type not in GAME_TYPES:
                msg = "game_type must be 'POST' or one of {}".format(GAME_TYPES)
                raise ClientException(msg)
            filters.append("game-type={}".format(game_type))

        games_endpoint = self.API_URL + "/api/v1/games/"
        if len(filters) > 0:
            games_endpoint += "?" + "&".join(filters)

        response = self._get(url=games_endpoint)
        if response.status_code == 400:
            msg = response.json()["detail"]
            raise APIException(msg)
        elif response.status_code != 200:
            msg = "Received HTTP status {} when fetching games".format(
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

    def get_players(self, search=None):
        """Get players, with some searching capacity

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
            msg = "Received HTTP status {} when fetching players.".format(
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

    def get_parks(self, city=None, state=None, league=None):
        """Get gen of ballparks known to the retrosheet universe"""
        query_params = []
        if city:
            query_params.append("city={}".format(city))
        if state:
            query_params.append("state={}".format(state))
        if league:
            query_params.append("league={}".format(city))

        if len(query_params) > 0:
            query_string = "?" + "&".join(query_params)
        else:
            query_string = ""

        parks_endpoint = self.API_URL + "/api/v1/parks/" + query_string
        response = self._get(parks_endpoint)
        if response.status_code != 200:
            msg = "Received HTTP status {} when fetching parks".format(
                response.status_code
            )
            raise APIException(msg)
        data = response.json()
        while len(data["results"]) > 0:
            for park in data["results"]:
                park["start_date"] = datetime.strptime(
                    park["start_date"], "%Y-%m-%d"
                ).date()
                if park["end_date"] is not None:
                    park["end_date"] = datetime.strptime(
                        park["end_date"], "%Y-%m-%d"
                    ).date()
                yield park
            next_url = data["next"]
            if next_url is None:
                break
            response = self._get(url=next_url)
            data = response.json()

    def get_park(self, park_id):
        """Get a specific park object"""
        park_endpoint = self.API_URL + "/api/v1/parks/{}".format(park_id)
        response = self._get(url=park_endpoint)
        if response.status_code == 404:
            msg = "Park with park-id={} not found.".format(park_id)
            raise ParkNotFoundException(msg)
        elif response.status_code != 200:
            msg = "Received HTTP status {} when fetching park w/ park-id={}".format(
                response.status_code, park_id
            )
            raise APIException(msg)
        park_data = response.json()
        park_data["start_date"] = datetime.strptime(
            park_data["start_date"], "%Y-%m-%d"
        ).date()
        if park_data["end_date"] is not None:
            park_data["end_date"] = datetime.strptime(
                park_data["end_date"], "%Y-%m-%d"
            ).date()
        return park_data

    def get_teams(self, search: str = None, only_active: bool = False):
        """Get a generator of teams

        Args:
            search: str, search parameter which returns teams based on their "nickname"
                         city or string team-id (e.g. NYA). Matches exactly to city and team-id,
                         of partially to nick-name
            active: bool, only return teams that still exist. Defaults to false

        Returns:
            generator of team-object/dicts that match search criteria.
        """
        if only_active:
            params = "?only-active=1"
        else:
            params = "?only-active=0"
        if search is not None:
            params += "&search={}".format(search)
        team_endpoint = self.API_URL + "/api/v1/teams/" + params
        response = self._get(team_endpoint)
        if response.status_code != 200:
            msg = "Received HTTP status {} when fetching teams".format(
                response.status_code
            )
            raise APIException(msg)

        data = response.json()
        while len(data["results"]) > 0:
            for team in data["results"]:
                yield team
            next_url = data["next"]
            if next_url is None:
                break
            response = self._get(url=next_url)
            data = response.json()

    def get_team(self, int_team_id: int):
        """Get details about a team"""
        team_endpoint = self.API_URL + "/api/v1/teams/{}/".format(int_team_id)
        response = self._get(team_endpoint)
        if response.status_code == 404:
            msg = "Team with ID: {} not found".format(int_team_id)
            raise TeamNotFoundException(msg)
        elif response.status_code != 200:
            msg = "Received HTTP status {} when fetching team with id: {}".format(
                response.status_code, int_team_id
            )
            raise APIException(msg)
        return response.json()

    def get_lineup(self, game_id: str):
        """Return a list of lineup Objects for a game"""
        raise NotImplementedError()

    def get_player_events(
        self, retro_id: str, start_date: str = None, end_date: str = None
    ):
        """Get paginated events for a player

        The API exposes an endpoint to filter play-by-play events by player. All events are
        returned for a specific player, regardless of whether the player was the hitter or the pitcher.
        Therefore, the user should be careful to understand this point!

        A user may also filter based on a date window, i.e. return all events within this
        range of dates, or if only a start_date or end_date is supplied, the events will be
        bounded by those respective dates.

        Args:
            retro_id: str, unique retrosheet ID of the player events should be returned for.
            start_date: str, YYYY-MM-DD string to return events after
            end_date: str, YYYY-MM-DD string to return events before

        Returns:
            a generator of tuples, which have the form:
            {
                "game_id": "HOU201805010",
                "date": "2018-05-01",
                "hitter_retro_id": "judga001",
                "pitcher_retro_id": "verlj001",
                "pitch_sequence": "F1*BBCS",
                "event_description": "K",
                "count_on_play": "22",
                "inning": 1,
                "event_count": 1
            }
        """
        filters = []
        if start_date:
            filters.append("start-date=" + start_date)
        if end_date:
            filters.append("end-date=" + end_date)

        player_events_endpoint = self.API_URL + "/api/v1/players/{}/events/".format(
            retro_id
        )
        if filters:
            player_events_endpoint += "?" + "&".join(filters)

        response = self._get(url=player_events_endpoint)
        if response.status_code != 200:
            msg = "Received HTTP status {} when fetching events for player: {}".format(
                response.status_code, retro_id
            )
            raise APIException(msg)

        data = response.json()
        while len(data["results"]) > 0:
            for event in data["results"]:
                event["date"] = datetime.strptime(event["date"], "%Y-%m-%d").date()
                yield event
            next_url = data["next"]
            if next_url is None:
                break
            response = self._get(url=next_url)
            data = response.json()
