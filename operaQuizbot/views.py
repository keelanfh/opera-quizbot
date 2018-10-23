import json
import os
import time
from urllib.parse import urlencode

from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .models import User, Question, UserAnswer, ReceivedMessage
from .settings import DEBUG


def process_payload(user, payload):
    """Function that processes the payload from any incoming quick_replies message."""
    if payload == "ad_go":
        user.profile.get_info()
        user.profile.request_oauth()
    elif payload == "operafinder_yes":
        user.profile.send_opera_goer_q()
    elif payload == "operafinder_no":
        user.profile.send_operafinder_no()
    elif payload == "operafinder_nono":
        user.profile.send_message("We understand. We hope you’ll change your mind!")
    elif payload == "operafinder_more":
        user.profile.send_operafinder_info()
    elif payload == "operafinder_more_inquiz":
        user.profile.send_operafinder_info_inquiz()
    elif payload == "restart_yes":
        user.profile.recorded_answers.clear()
        user.profile.start_quiz()
    #try:
    if payload.startswith('question'):
        user.profile.sender_action("mark_seen")
        user.profile.sender_action("typing_on")
        time.sleep(1.5)
        _, id, text = payload.split('_')
        try:
            q = Question.objects.get(id=id)
        except:
            raise Exception('Problem finding question object.')

        # Only serve a "did you know" statement once every three questions
        # Only ever serve a "did you know" if there's another question
        if int(id) % 3 == 1 and q.next_question:
            user.profile.sender_action("typing_off")
            user.profile.send_dyk_message()
            time.sleep(0.5)
            user.profile.sender_action("typing_on")
            time.sleep(2)

        if text != "none":
            a = q.answer_set.filter(text=text)[0]
            try:
                user_answer = UserAnswer.objects.create(question=q,
                                                        profile=user.profile,
                                                        answer=a)
                user_answer.save()
            except IntegrityError:
                user.profile.send_message(
                    "Sorry, you can't answer the same question twice!")
        if q.next_question:
            user.profile.sender_action("typing_off")
            user.profile.send_question(q.next_question)
        else:
            user.profile.end_quiz()
    #except:
     #   print('Problem replying to response to question')

    return HttpResponse("EVENT_RECEIVED")


def process_button_payload(user, payload):
    # We only respond if the user denies us permission to read their likes.
    # If they allow us to read their likes, a message is sent once authorisation
    # is complete [see pipelines.oauth_complete()].
    if payload == "oauth_refused":
        user.profile.ask_to_start(oauth=False)
    elif payload.startswith("opera_goer"):
        *_, id = payload.split("_")
        user.profile.opera_goer_id = id
        user.profile.save()

        user.profile.send_culture_q()

    elif payload.startswith("culture"):
        *_, id = payload.split("_")
        user.profile.approach_culture_id = id
        user.profile.save()

        user.profile.send_financial_q()

    elif payload.startswith("financial"):
        *_, id = payload.split("_")
        user.profile.financial_id = id

        user.profile.save()
        # Now make the calculations.
        user.profile.find_dyk_questions()
        # Finally, begin the quiz
        user.profile.start_quiz()
    user.profile.sender_action("typing_off")


def home(request):
    """Very simple response, just to check that the app is working"""
    return render(request, 'home.html')


# CSRF exemption overrides a security setting in Django.
# It allows the server to respond where the POST data doesn't come from a form.
@csrf_exempt
def webhook(request):
    """Responds to all webhook requests from Facebook."""
    #  GET requests are sent to verify the app on first activation.
    if request.method == "GET":

        FACEBOOK_VERIFY_TOKEN = os.environ['FACEBOOK_VERIFY_TOKEN']
        mode = request.GET["hub.mode"]
        verify_token = request.GET["hub.verify_token"]
        challenge = request.GET["hub.challenge"]

        # Check that Facebook is sending correct token and send 200 response
        if mode == "subscribe" and verify_token == FACEBOOK_VERIFY_TOKEN:
            return HttpResponse(challenge)

        # Otherwise, return an error to Facebook
        else:
            return HttpResponse(status=403)

    # POST requests are sent with data from Facebook
    if request.method == "POST":

        # First load in the JSON of the POST body
        # There might be a syntactically simpler way of doing this
        incoming_message = json.loads(request.body.decode('utf-8'))

        # Loop through the structure of the JSON data
        for entry in incoming_message['entry']:
            # Check if messaging is actually in the entry - if not, return 200
            if 'messaging' in entry:
                for message in entry['messaging']:
                    # Discard repeated instances of the same message coming in
                    if 'message' in message:
                        _, first_time = ReceivedMessage.objects.get_or_create(id=message['message']['mid'])
                    else:
                        first_time = True
                    if not first_time:
                        return HttpResponse("EVENT_RECEIVED")

                    psid = message['sender']['id']

                    # Create the User object, or get it if it already exists
                    try:
                        # user is User object
                        # first_time is bool, is True if User was created
                        user, first_time = User.objects.get_or_create(username=psid)
                    except Exception as e:
                        print(e)
                        raise Exception("Could not create the User entry in the database.")

                    if 'message' in message:
                        try:
                            text = message['message']['text']
                            print("Message received from Facebook:" + text)

                        except KeyError:
                            print("Message received from Facebook with no text")
                            text = None

                        # If it's the first time a User has sent a message, greet the user.
                        if first_time and 'quick_reply' not in message['message']:
                            user.profile.greet()
                            user.profile.request_oauth()
                        elif text:
                            # Some test shortcuts, just for testing...
                            if DEBUG:
                                if text.lower() == "likes":
                                    user.profile.get_likes()
                                elif text.lower() == "play?":
                                    user.profile.ask_to_start(oauth=False)
                                elif text.lower() == "end":
                                    user.profile.end_quiz()
                                elif text == "oauth":
                                    user.profile.request_oauth()
                                elif text == "opera":
                                    user.profile.send_opera_goer_q()
                                    return HttpResponse("OK")

                            if 'quick_reply' in message['message']:
                                return process_payload(user,
                                                       message['message']['quick_reply']['payload'])
                            else:
                                user.profile.outofscope_message()
                        else:
                            # No text got sent at all
                            user.profile.outofscope_message()

                    # Respond to incoming messages appropriately.
                    # This part handles the buttons postbacks, not the quick reply postbacks.

                    elif "postback" in message:
                        process_button_payload(user, message['postback']['payload'])

            else:
                return HttpResponse("EVENT_RECEIVED")
        # Let Facebook know the message was received correctly.
        # Very important - if not done, Facebook will shut down app.
        # Also marks message as received for the sender.
        return HttpResponse("EVENT_RECEIVED")


def close_window(request):
    """
    Respond with a redirect - for use when Facebook authentication complete.
    Should close the Messenger window. (note: feature doesn't work on iOS)."""
    return HttpResponseRedirect(
        "https://www.messenger.com/closeWindow/?" +
        urlencode({"image_url": "https://{}/static/logo.jpg".format(os.environ['SERVER_URL']),
                   "display_text":
                       "Done! Thank you for your patience - you can close this window now."}))


def message(request):
    """
    Redirect to Messenger
    """
    return HttpResponseRedirect("")
