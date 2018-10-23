from django.contrib import admin
from django.contrib.auth.models import User, Group
from social_django.models import Association, Nonce, UserSocialAuth
from django.db.models import ManyToManyField
from django.forms import CheckboxSelectMultiple


from .models import Profile, FacebookPage, Question, Answer, Opera

# TODO maybe modify view so that weightings can be seen


class AnswersInline(admin.StackedInline):
    model = Answer
    fields = ('text', 'str_neg_associations', 'str_pos_associations')
    readonly_fields = ('str_neg_associations', 'str_pos_associations')

class QuestionAdmin(admin.ModelAdmin):
    formfield_overrides = {
        ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    list_display = ('text',)
    inlines = (AnswersInline,)
    fields = ('text', 'next_question',)


class OperaAdmin(admin.ModelAdmin):
    formfield_overrides = {
        ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    list_display = ('name',)
    fields = ('name', 'url', 'categories')

class FacebookPageAdmin(admin.ModelAdmin):
    formfield_overrides = {
        ManyToManyField: {'widget': CheckboxSelectMultiple},
    }
    list_display = ('name',)
    fields = ('name', 'facebook_link', 'categories',)
    readonly_fields = ('facebook_link',)

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'financial', 'opera_goer', 'approach_culture')
    fields = ('first_name', 'last_name', 'likes', 'financial', 'opera_goer', 'approach_culture')


admin.site.register(Question, QuestionAdmin)
admin.site.register(Opera, OperaAdmin)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(FacebookPage, FacebookPageAdmin)

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(Association)
admin.site.unregister(Nonce)
admin.site.unregister(UserSocialAuth)
