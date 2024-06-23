from django.conf import settings
from django.urls import reverse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
import yaml

class MyAccountAdapter(DefaultSocialAccountAdapter):
    def get_connect_redirect_url(self, request, socialaccount):
        if request.user.is_superuser:
            return reverse("admin-dashboard")
        else:
            return reverse("user-dashboard")
        # print("test")
        # with open("admins.yaml", 'r') as stream:
        #     try:
        #         admins = yaml.safe_load("admins")
        #         print(admins)
        #         if request.user.email in admins:
        #             return reverse("admin-dashboard")
        #         else:
        #             return reverse("user-dashboard")
        #     except yaml.YAMLError as exc:
        #         print(exc)