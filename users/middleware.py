from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse


class CheckBlockedMiddleware:
    """
    Constantly checks if user is not blocked. If true - logout him and show the message.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            if request.user.is_blocked:
                messages.info(request, "Вы были заблокированы в сервисе")
                logout(request)
                return redirect(reverse('users:login'))

        response = self.get_response(request)
        return response
