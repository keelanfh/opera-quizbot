import requests
import os
import dotenv

dotenv.read_dotenv('../.env')

# TODO incorporate this into a setup flow

print(requests.get('https://graph.facebook.com/v2.10/oauth/access_token', params=
{
    "client_id": os.environ.get('SOCIAL_AUTH_FACEBOOK_KEY'),
    "client_secret": os.environ.get('SOCIAL_AUTH_FACEBOOK_SECRET'),
    "grant_type": "client_credentials"
}).json())
