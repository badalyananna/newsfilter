from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your views here.
def welcome(request):
    if request.user.is_authenticated:
        return redirect('feed/all')
    else:
        return render(request, 'welcome_page.html')
