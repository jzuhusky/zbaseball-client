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
            data=json.dumps({
                "username": self._username,
                "password": self._password
            })
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
