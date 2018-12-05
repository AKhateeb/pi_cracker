import re
from django.shortcuts import render
import instagram

cracker = None
current_password = "xxxx"


def index(request):
    return render(request, template_name=__package__+".html",context=None)

def start(request):
    username = request.GET.get('username', None)
    if username and re.match(r"^[a-zA-Z0-9._]+$", username):
        cracker = ""