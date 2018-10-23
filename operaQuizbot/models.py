from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils.html import format_html

from .helpers import facebook_get_json, facebook_post_json, facebook_base_get_json
from .settings import SERVER_URL


class FacebookPage(models.Model):
    facebook_id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=256)
    categories = models.ManyToManyField('OperaCategory')

    class Meta:
        verbose_name = "Facebook Page"

    def __repr__(self):
        return "FacebookPage({},{})".format(self.facebook_id, self.name)

    def __str__(self):
        return str(self.name)

    @property
    def facebook_url(self):
        return "https://facebook.com/{}".format(self.facebook_id)

    def facebook_link(self):
        return format_html(
            '<a href="{}">Facebook Page</a>',
            self.facebook_url)


class Question(models.Model):
    id = models.IntegerField(primary_key=True)
    text = models.CharField(max_length=128)
    next_question = models.OneToOneField('Question', null=True)

    def __repr__(self):
        return "Question({},{})".format(self.id, self.text)

    def __str__(self):
        return str(self.text)


class AnswerCategoryWeighting(models.Model):
    """Class which manages weighting between Answer and Category."""
    answer = models.ForeignKey('Answer')
    category = models.ForeignKey('OperaCategory')
    weighting = models.FloatField()


class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=128)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    categories = models.ManyToManyField('OperaCategory', through=AnswerCategoryWeighting)

    def __repr__(self):
        return "Answer({},{},{})".format(self.id, self.text, repr(self.question))

    @property
    def str_pos_associations(self):
        pos = self.categories.filter(answercategoryweighting__weighting__gt=0)
        pos = [x.name for x in pos]
        return ", ".join(pos)

    @property
    def str_neg_associations(self):
        neg = self.categories.filter(answercategoryweighting__weighting__lt=0)
        neg = [x.name for x in neg]
        return ", ".join(neg)

    str_neg_associations.fget.short_description = "Negative associations"
    str_pos_associations.fget.short_description = "Positive associations"


class FinancialCategory(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Financial Status"


class OperaGoerCategory(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Opera Attendance Status"


class ApproachCultureCategory(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name: "Approach to Culture"


class DidYouKnowQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=256)
    approach_culture = models.ManyToManyField(ApproachCultureCategory, blank=True)
    opera_goer = models.ManyToManyField(OperaGoerCategory, blank=True)
    financial = models.ManyToManyField(FinancialCategory, blank=True)

    image_url = models.CharField(max_length=256, default='')
    link_url = models.CharField(max_length=256, default='')


class Profile(models.Model):
    """
    Profile class. Anyone writing a message will have a profile class created.
    Profile.user is an instance of User.
    User.profile is an instance of Profile.

    Example usage:

    user = User.objects.get_or_create(username="foobar")
    user.profile.greet()
    user.profile.send_message("Hello there!")"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    facebook_psid = models.BigIntegerField(primary_key=True)
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    likes = models.ManyToManyField(FacebookPage, verbose_name="Facebook Likes")
    recorded_answers = models.ManyToManyField(Question, through='UserAnswer')

    financial = models.ForeignKey(FinancialCategory, null=True, verbose_name="Financial sensitivity")
    opera_goer = models.ForeignKey(OperaGoerCategory, null=True, verbose_name="Opera Attendance Status")
    approach_culture = models.ForeignKey(ApproachCultureCategory, null=True, verbose_name="Approach to Culture")

    did_you_know = models.ManyToManyField(DidYouKnowQuestion, blank=True)

    class Meta:
        verbose_name = "User"

    def __repr__(self):
        return "Profile({}, {}, {})".format(self.facebook_psid, self.first_name, self.last_name)

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    @property
    def facebook_asid(self):
        """Fetches the user's asid from social_auth."""
        return self.user.social_auth.get(provider='facebook').uid

    def send_message(self, message_text):
        """Sends a Facebook message to the user."""

        response = facebook_post_json('me/messages', {"recipient": {"id": self.facebook_psid},
                                                      "message": {"text": message_text}})

        if response.ok:
            print("Message '{}' successfully sent to user {}".format(message_text, str(self)))
        else:
            print("Problem sending message '{}' to user {}".format(message_text, str(self)))

    def sender_action(self, action_text):
        """Sends a sender action to Facebook."""
        assert action_text in ["typing_on", "typing_off", "mark_seen"]
        response = facebook_post_json('me/messages', {"recipient": {
            "id": self.facebook_psid},
            "sender_action": action_text})
        if response.ok:
            print("Sender action {} successfully sent to user {}".format(action_text, str(self)))

    def get_info(self):
        """Fetches the user's basic information from Facebook"""

        response = facebook_get_json(self.facebook_psid)
        self.first_name = response['first_name']
        self.last_name = response['last_name']
        self.save()

    def greet(self):
        self.get_info()
        self.send_message("Hello, {}!".format(self.first_name))
        self.send_message("We'd like to help you find an opera you might like, based on your interests.")

    def request_oauth(self):
        """Sends a message to the user requesting that they provide OAuth authentication.
        This enables us to access their Facebook likes.
        """

        # TODO Domain whitelisting doesn't have to be done on every occasion
        facebook_post_json('me/messenger_profile', {"whitelisted_domains": SERVER_URL})
        self.send_buttons(
            "To help us match operas to you, we'd like to look at what you've liked on Facebook. Is that OK? This might take a second. 😅",
            [
                {
                    "type": "web_url",
                    "url": "https://" + SERVER_URL + "/oauth/login/facebook/",
                    "title": "Sure! 😀"
                },
                {
                    "type": "postback",
                    "title": "No thanks. 😐",
                    "payload": "oauth_refused"
                }
            ])

    def get_likes(self):
        """Gets the user's Facebook likes and echos back the first couple."""

        # Get the first page of user's likes
        j = self.facebook_get_user_json('likes')
        # Move on to the next page each time, if the key exists.
        for x in j['data']:
            # We're only interested in the Facebook pages that we actually have information on.
            try:
                facebook_page = FacebookPage.objects.get(facebook_id=int(x['id']), name=x['name'])
                self.likes.add(facebook_page)
            except FacebookPage.DoesNotExist:
                pass
        self.save()

    def send_buttons(self, text, buttons):
        """Sends a Facebook message with buttons to the user."""

        message = {"recipient": {"id": self.facebook_psid},
                   "message": {
                       "attachment": {
                           "type": "template",
                           "payload": {
                               "template_type": "button",
                               "text": text,
                               "buttons": buttons
                           }
                       }
                   }
                   }

        response = facebook_post_json('me/messages', message)

        if response.ok:
            print("Message '{}' successfully sent to user {}".format(message, str(self)))
        else:
            print(response.status_code, response.text)
            print("Problem sending message '{}' to user {}".format(message, str(self)))

    def send_quick_replies(self, text, replies):
        """Sends a Facebook message with quick replies to the user."""

        buttons = [
            {
                "content_type": "text",
                "title": x[0],
                "payload": x[1]
            }
            for x in replies]

        message = {"recipient": {"id": self.facebook_psid},
                   "message": {
                       "text": text,
                       "quick_replies": buttons}
                   }

        response = facebook_post_json('me/messages', message)

        if response.ok:
            print("Message '{}' successfully sent to user {}".format(message, str(self)))
        else:
            print(response.status_code, response.text)
            print("Problem sending message '{}' to user {}".format(message, str(self)))

    def facebook_get_user_json(self, endpoint):
        """Makes a GET request to Facebook at /{asid}/{endpoint}"""
        url = "".join(['/', str(self.facebook_asid), '/', endpoint])
        print(url)
        return facebook_base_get_json(url, params={
            "access_token": self.user.social_auth.get(provider='facebook').extra_data['access_token']})

    def ask_to_start(self, oauth):
        """Asks the user if they want to start the quiz."""
        if oauth:
            self.send_message("Thanks for that!")
        else:
            self.send_message("No problem!")

        # Now send the user a message about the Opera Finder
        self.send_quick_replies("Do you want to play Opera Finder?",
                                [("Yes", "operafinder_yes"),
                                 ("No", "operafinder_no"),
                                 ("Tell me more?", "operafinder_more")])

    def start_quiz(self):
        """Method that will start a quiz for the user."""

        self.send_question(Question.objects.get(id=1))

    def send_question(self, question):
        self.send_quick_replies(question.text,
                                [(answer.text, "question_{}_{}".format(question.id, answer.text))
                                 for answer in Answer.objects.filter(question=question).order_by('id')])

    def end_quiz(self):
        """Initial opera recommendation process."""
        user_category_weightings = {x.name: 0 for x in OperaCategory.objects.all()}
        user_answers = UserAnswer.objects.filter(profile=self)

        for x in user_answers:
            for category in x.answer.categories.all():
                # For all categories in the weighting, add the answer's weighting
                answer_weighting = AnswerCategoryWeighting.objects.get(answer=x.answer, category=category).weighting
                user_category_weightings[category.name] += answer_weighting

        user_facebook_likes = self.likes.all()

        for x in user_facebook_likes:
            for category in x.categories.all():
                user_category_weightings[category.name] += 0.51

        print(user_category_weightings)

        favourite = [x for x in user_category_weightings.items() if x[1] > 0]
        favourite.sort(key=lambda x: x[1])
        if favourite:
            self.send_message(f"Looks like you love {favourite[-1][0].lower()}...")

        all_operas = [opera for opera in Opera.objects.all() if opera.url]

        highest_opera = all_operas[0]
        highest_opera_value = 0
        for opera in all_operas:
            opera_value = 0
            categories = [x.name for x in opera.categories.all()]
            # Add to the value where the opera is in there.
            for x in categories:
                opera_value += user_category_weightings[x]
            if opera_value > highest_opera_value:
                highest_opera, highest_opera_value = opera, opera_value

        buttons = [
            {
                "type": "web_url",
                "url": highest_opera.url,
                "title": "Find out more"
            }]

        self.send_buttons("Based on your answers, we recommend {}! {}".format(highest_opera.name,
                                                                              highest_opera.description),
                          buttons)

        self.send_quick_replies("Thanks so much for trying our quizbot. "
                                "Would you like to try again?",
                                [("Yes", "restart_yes")])

        # buttons = [
        #     {
        #         "type": "web_url",
        #         "url": "https://takke.typeform.com/to/l2AdhA",
        #         "title": "Go to survey"
        #     }]
        # self.send_buttons("Thanks so much for trying out our quizbot. We'd really appreciate your feedback, so it would be great if you could fill in our survey, if you don't mind! Thank you 😀", buttons)

    def send_operafinder_no(self):
        self.send_quick_replies(
            "Oh, no. 😔 Opera Finder is just a quiz-game that we use to help you explore opera, "
            "by suggesting a production you might enjoy - are you sure you don’t want to play?",
            [("Yes", "operafinder_yes"),
             ("No", "operafinder_nono")])

    def send_operafinder_info(self):
        self.send_message(
            "Of course! Opera Finder is a quiz-game that we use to help you explore opera, by suggesting a production you might enjoy. We consider your interests, as well as plot and music preferences - and then find your opera match! If you are interested, then, you can always read more about your match on our website.")
        self.send_quick_replies("Would you like to play?",
                                [("Yes", "operafinder_yes"),
                                 ("No", "operafinder_nono")])

    def send_operafinder_info_inquiz(self):
        self.send_message(
            "Of course! Opera Finder is a quiz-game that we use to help you explore opera, by suggesting a production you might enjoy. We consider your interests, as well as plot and music preferences - and then find your opera match! If you are interested, then, you can always read more about your match on our website.")
        question = self.recorded_answers.all().order_by('-id')[0].id
        self.send_quick_replies("Would you like to go back to the quiz?",
                                [("Resume quiz", f"question_{question}_none"),
                                 ("Restart quiz", "restart_yes")])

    def outofscope_message(self):
        text = "Sorry, I didn't understand that. 🧐"
        # Test if user has already started quiz
        if self.recorded_answers.exists():
            # Get the last question they have answered, and supply the next one
            question = self.recorded_answers.all().order_by('-id')[0].id
            buttons = [("Help", "operafinder_more_inquiz"),
                       ("Resume quiz", f"question_{question}_none")]
        else:
            buttons = [("Tell me more", "operafinder_more"),
                       ("Start quiz", "operafinder_yes")]

        self.send_quick_replies(text, buttons)

    def send_opera_goer_q(self):
        text = "Out of curiosity, have you ever been to an opera?"
        buttons = [
            {
                "type": "postback",
                "title": "Never",
                "payload": "opera_goer_1"
            },
            {
                "type": "postback",
                "title": "Once",
                "payload": "opera_goer_3"
            },
            {
                "type": "postback",
                "title": "More than once",
                "payload": "opera_goer_2"
            }]
        buttons2 = [
            {
                "type": "postback",
                "title": "From time to time",
                "payload": "opera_goer_4"
            },
            {
                "type": "postback",
                "title": "Regularly",
                "payload": "opera_goer_5"
            }
        ]
        self.send_buttons(text, buttons)
        self.send_buttons("or", buttons2)

    def send_culture_q(self):
        text = "What kind of culture do you like?"
        buttons = [
            {
                "type": "postback",
                "title": f"{name}",
                "payload": f"culture_{no}"
            }
            for no, name in [(1, "I love any culture"),
                             (2, "ballet or museum"),
                             (3, "movie/festival/sport")]
        ]
        self.send_buttons(text, buttons)
        buttons = [
            {
                "type": "postback",
                "title": f"{name}",
                "payload": f"culture_{no}"
            }
            for no, name in [(4, "neighbourhood events"),
                             (5, "Culture? Not for me!")]
        ]
        self.send_buttons("or", buttons)

    def send_financial_q(self):
        text = "What kind of ticket would you usually get for such an event?"
        buttons = [
            {
                "type": "postback",
                "title": f"{name}",
                "payload": f"financial_{no}"
            }
            for no, name in [(1, "As cheap as possible"),
                             (2, "Not too expensive"),
                             (3, "Budget front row")]
        ]
        self.send_buttons(text, buttons)
        buttons = [
            {
                "type": "postback",
                "title": f"{name}",
                "payload": f"financial_{no}"
            }
            for no, name in [(4, "Front row please!")]
        ]
        self.send_buttons('or', buttons)

    def find_dyk_questions(self):
        # Randomise the did you know questions
        for dyk in DidYouKnowQuestion.objects.all():
            print(self.opera_goer_id, [t.id for t in dyk.opera_goer.all()], self.financial_id,
                  [t.id for t in dyk.financial.all()], self.approach_culture_id,
                  [t.id for t in dyk.approach_culture.all()])
            if int(self.opera_goer_id) in [int(t.id) for t in dyk.opera_goer.all()]:
                if int(self.financial_id) in [int(t.id) for t in dyk.financial.all()]:
                    if int(self.approach_culture_id) in [int(t.id) for t in dyk.approach_culture.all()]:
                        self.did_you_know.add(dyk)

        self.save()

    def send_dyk_message(self):
        print(self.did_you_know.all())
        if self.did_you_know.all():
            print("DYK found")
            try:
                dyk = self.did_you_know.order_by('?')[0]
            except IndexError:
                return
        else:
            return

        if dyk.link_url:
            buttons = [{
                "type": "web_url",
                "url": dyk.link_url,
                "title": "Find out more"
            }]

            self.send_buttons(dyk.text, buttons)

        elif dyk.image_url:
            self.send_message(dyk.text)
            facebook_post_json('me/messages', {
                "recipient": {
                    "id": self.facebook_psid
                },
                "message": {
                    "attachment": {
                        "type": "image",
                        "payload": {
                            "url": dyk.image_url,
                            "is_reusable": True
                        }
                    }
                }
            })

        else:
            self.send_message(dyk.text)

        self.did_you_know.remove(dyk)


class UserAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('question', 'profile',)

    def __repr__(self):
        return "UserAnswer({}, {}, {})".format(repr(self.question), repr(self.profile), repr(self.answer))


class OperaCategory(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)

    def __repr__(self):
        return "OperaCategory({}, {})".format(self.id, self.name)

    def __str__(self):
        return str(self.name)


class Opera(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=128)
    categories = models.ManyToManyField(OperaCategory)
    url = models.CharField(max_length=128, verbose_name="'More info' web page")
    description = models.TextField()

    def __repr__(self):
        return "Opera({}, {})".format(self.id, self.name)


# TODO this model is currently not being used, maybe get rid of it
class Performance(models.Model):
    id = models.AutoField(primary_key=True)
    datetime = models.DateTimeField()
    opera = models.ForeignKey(Opera, on_delete=models.CASCADE)


class ReceivedMessage(models.Model):
    id = models.CharField(primary_key=True, max_length=128)


@receiver(post_save, sender=User)
def create_user_profile(instance, created, **kwargs):
    """Create a new Profile every time a User is created."""
    if created:
        try:
            Profile.objects.create(user=instance, facebook_psid=instance.username)
        except ValueError:
            Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(instance, **kwargs):
    """Save the Profile every time a User is saved."""
    instance.profile.save()


@receiver(post_delete, sender=Profile)
def delete_user_profile(instance, **kwargs):
    """Delete the User every time a Profile is deleted.
    User won't be deleted directly, so we don't need the converse.
    """
    instance.user.delete()
