from allauth.socialaccount.forms import SignupForm
from django.contrib.auth.models import User
from .models import Profile
import yaml

class ProfileSignupForm(SignupForm):
    def save(self, request):
        user = super(ProfileSignupForm, self).save(request)
        profile = Profile.objects.create(user=user)
        with open("admins.yaml", 'r') as stream:
            try:
                admins =  yaml.safe_load(stream)['admins']
                if request.user.email in admins:
                    profile.is_admin = True
                else:
                    profile.is_admin = False
            except yaml.YAMLError as exc:
                print(exc)
        profile.save()
        return user