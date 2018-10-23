import hmac
import os

from .models import Profile
from .helpers import facebook_base_get_json


def load_user(response, *a, **kw):
    """
    Part of the authorisation pipeline.
    When a user authorises the application, it queries Facebook with the ASID
    to find the PSID, enabling us to link with the existing User.
    """
    asid = response['id']

    FACEBOOK_APP_SECRET = os.environ.get('SOCIAL_AUTH_FACEBOOK_SECRET')
    APP_ACCESS_TOKEN = os.environ.get('APP_ACCESS_TOKEN')
    FACEBOOK_PAGE_ID = os.environ.get('FACEBOOK_PAGE_ID')
    t = facebook_base_get_json(str(asid) + '/ids_for_pages', params={
        "page": FACEBOOK_PAGE_ID,
        "access_token": APP_ACCESS_TOKEN,
        "appsecret_proof": hmac.new(key=FACEBOOK_APP_SECRET.encode('utf-8'),
                                    msg=APP_ACCESS_TOKEN.encode('utf-8'),
                                    digestmod="SHA256").hexdigest()})

    psid = t['data'][0]['id']
    user = Profile.objects.get(facebook_psid=psid).user
    return {"user": user}

def auth_complete(user, *a, **kw):
    """
    Sends a message when authentication is complete.
    """
    user.profile.ask_to_start(oauth=True)
    user.profile.get_likes()
