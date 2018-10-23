import os
import requests
from urllib.parse import urljoin

from .settings import FACEBOOK_API_URL


def facebook_base_get_json(endpoint, params):
    """Base function to make a GET request to Facebook."""

    url = urljoin(FACEBOOK_API_URL, str(endpoint))
    r = requests.get(url, params=params)
    print("GET request made to: {}. Response status {}".format(url, r.status_code))
    if not r.ok:
        print("Response: ".format(r.text))
    return r.json()


def facebook_get_json(endpoint, params={}):
    """Fetches the JSON body of a GET request to the specified endpoint.
    Uses the page token."""

    params["access_token"] = os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
    json = facebook_base_get_json(endpoint, params)
    return json


def facebook_app_get_json(endpoint, params={}):
    """Fetches the JSON body of a GET request to the specified endpoint.
    Uses the app token."""

    params["access_token"] = os.environ.get("APP_ACCESS_TOKEN")
    json = facebook_base_get_json(endpoint, params)
    return json

def facebook_base_post_json(endpoint, json, params):
    url = urljoin(FACEBOOK_API_URL, str(endpoint))
    print("Making POST request to: {} with body {}".format(url, json))
    return requests.post(url, json=json, params=params)


def facebook_post_json(endpoint, json):
    """Makes a POST request to the specified endpoint with a JSON body"""
    params = {"access_token": os.environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")}
    return facebook_base_post_json(endpoint, json, params)