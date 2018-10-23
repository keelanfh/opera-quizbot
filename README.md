# Opera Quiz Chatbot

A quiz question-based bot which recommends an opera to the user based on their interests, using the Facebook API

## Architecture description

This is a Django application. In testing, it ran on a free Heroku dyno.

The app primarily interacts with users through the Facebook API, receiving Messenger webhook requests and pushing out requests to the Facebook API.

If running on Heroku, the config vars can be entered in the web interface.

## Setup - for running locally

### Requirements
- make sure you have Python 3 installed (get it [here](https://www.python.org/))
- make sure you've installed the Heroku CLI (get it [here](https://devcenter.heroku.com/articles/heroku-cli#download-and-install))

### Local setup

- Clone this repository with `git clone https://github.com/keelanfh/opera-quizbot`

- Rename `.env.example` to `.env`

- Once you've done this, `cd` into `opera-quizbot` and run `./setup.sh`

- Activate the `virtualenv` by running `source venv/bin/activate`

- Run the server by running `heroku local`

- Navigate to [http://127.0.0.1:5000](http://127.0.0.1:5000). If you see a simple web page, setup has worked!

- Run `python manage.py makemigrations` followed by `python manage.py migrate`

- Set `DEBUG` in the `.env` to 1 for test purposes, but leave it set to 0 if it's publicly accessible

- Set `DJANGO_SECRET_KEY` to something complex

- Set up the database URL to whatever you are using

- Add the configuration files (separately) to the `operaQuizbot/management/commands` folder.

- `python manage.py importoperas` to import the operas and their categorisations

- `python manage.py importquestions` to import the questions, their categorisations and weightings

- `python manage.py importfbpages` to import the Facebook page information

- `python manage.py importprofilecategories` to import the user's profile categories

- `python manage.py importdidyouknows` to import the "Did you know?" statements

### Facebook setup

- Set up a Facebook app at `https://developers.facebook.com`

- You must have admin access to a Facebook page. Its ID should be entered as `FACEBOOK_PAGE_ID` in your `.env`. Enable Messenger for your Facebook app, selecting the page you wish to use. Generate a Page Access Token and enter this as `FACEBOOK_PAGE_ACCESS_TOKEN` in your `.env`

- Enable Messenger webhooks for `messages` and `messaging_postbacks`, subscribing to your page. Generate a random value to use as the Verify Token, and update this as your `FACEBOOK_VERIFY_TOKEN` in your `.env`

- Update your server URL as your App Domain with Facebook. This should also go in as `SERVER_URL` in your `.env`. An `ngrok` or similar URL will work fine if you're running it locally - otherwise use a Heroku URL

- Enable Facebook Login for your app. Set your `SERVER_URL` as a valid OAuth Redirect URL

- Generate a Facebook App Access Token with the following request (see [here](https://developers.facebook.com/docs/facebook-login/access-tokens/#apptokens)) from the details on your developer account. Once generated it, add it as `APP_ACCESS_TOKEN` in your `.env`:
```
curl -X GET "https://graph.facebook.com/oauth/access_token
  ?client_id=your-app-id
  &client_secret=your-app-secret
  &redirect_uri=your-redirect-url
  &grant_type=client_credentials
```

## Facebook IDs

Facebook issues two types of User IDs through the API: the `psid` and `asid`.

### psid: page-scoped ID

- This is the ID which we receive when we get a message.
- This ID must be used to send messages to users.
- API calls using the `psid` must be made with the page access token.

### asid: application-scoped ID

- This is the ID given when the user authorises the app.
- This ID must be used to make API calls to receive information such as user likes.
- API calls using the `asid` must be made with the app access token.

### Example usage in the app
The helper functions `facebook_get_json` and `facebook_app_get_json` use the page token and app token respectively.

```python
from .helpers import facebook_get_json, facebook_app_get_json
from .models import User

user = User.objects.get_or_create(username="foobar")
asid = user.profile.facebook_asid
psid = user.profile.facebook_psid

facebook_get_json(str(psid))

facebook_app_get_json(str(asid))
```

## Other help

If you have modified the models:

`python manage.py makemigrations`

`python manage.py migrate`
