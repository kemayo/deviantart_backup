#!/usr/bin/env python

import sanction

from urllib.parse import urlencode
from urllib.error import HTTPError


class ApiError(Exception):
    pass


class Api:
    def __init__(self, client_id, client_secret, scope="browse feed message note stash user user.manage comment.post collection"):
        self.client_id = client_id
        self.client_secret = client_secret

        self.auth_endpoint = "https://www.deviantart.com/oauth2/authorize"
        self.token_endpoint = "https://www.deviantart.com/oauth2/token"
        self.resource_endpoint = "https://www.deviantart.com/api/v1/oauth2"

        self.oauth = sanction.Client(
            auth_endpoint=self.auth_endpoint,
            token_endpoint=self.token_endpoint,
            resource_endpoint=self.resource_endpoint,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )

        self.auth()

    def auth(self):
        try:
            self.oauth.request_token(grant_type='client_credentials')
        except HTTPError as e:
            if e.code == 401:
                raise ApiError("Unauthorized: Please check your credentials (client_id and client_secret).")
            else:
                raise ApiError(e)

    def request(self, endpoint, get={}, post={}):
        if get:
            endpoint = "{}?{}".format(endpoint, urlencode(get))

        try:
            response = self.oauth.request(endpoint, data=bytes(urlencode(post), 'ascii'))
            if 'error' in response:
                raise ApiError(response['error_description'])
        except HTTPError as e:
            raise ApiError(e)

        return response
